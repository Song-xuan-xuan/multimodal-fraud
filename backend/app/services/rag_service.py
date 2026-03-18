import json
import logging
import sys
import threading
import uuid
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Ensure the repository root is importable so `model` can be resolved.
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

_initialized = False
_init_error: str | None = None
_initializing = False
_MANIFEST_FILE = 'knowledge_index_manifest.json'


def _resolve_rag_data_path() -> Path:
    settings = get_settings()
    fraud_path = settings.data_path / 'fraud_knowledge.json'
    legacy_path = settings.data_path / 'output_data.json'
    return fraud_path if fraud_path.exists() else legacy_path


def _manifest_path(storage_path: Path) -> Path:
    return storage_path / _MANIFEST_FILE


def load_index_manifest(storage_path: Path) -> dict:
    manifest_path = _manifest_path(storage_path)
    if not manifest_path.exists():
        return {'indexed_item_ids': []}

    try:
        return json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        logger.warning('Failed to load index manifest from %s, starting fresh', manifest_path)
        return {'indexed_item_ids': []}


def persist_index_manifest(storage_path: Path, indexed_item_ids: list[str]) -> None:
    manifest_path = _manifest_path(storage_path)
    manifest_path.write_text(
        json.dumps({'indexed_item_ids': sorted(indexed_item_ids)}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def ensure_rag_initialized():
    global _initialized, _init_error, _initializing
    if _initialized or _initializing:
        return

    _initializing = True

    try:
        from model.rag.service import get_rag_service
        settings = get_settings()
        service = get_rag_service()
        service.build_or_load(
            data_path=_resolve_rag_data_path(),
            storage_path=settings.chroma_path,
            api_key=settings.OPENAI_API_KEY,
            api_base=settings.OPENAI_BASE_URL,
            model=settings.OPENAI_MODEL,
            embedding_model=settings.EMBEDDING_MODEL,
            embedding_device=settings.EMBEDDING_DEVICE,
            chunk_size=settings.CHUNK_SIZE,
            collection_name=settings.CHROMA_COLLECTION_NAME,
        )
        _initialized = True
        _init_error = None
        logger.info('RAG service initialized successfully')
    except Exception as e:
        _initialized = False
        _init_error = str(e)
        logger.error('Failed to initialize RAG service: %s', e)
    finally:
        _initializing = False


def warm_rag_in_background() -> bool:
    global _initialized, _initializing
    if _initialized or _initializing:
        return False

    thread = threading.Thread(target=ensure_rag_initialized, name='rag-warmup', daemon=True)
    thread.start()
    return True


def get_rag_init_state() -> str:
    if _initialized:
        return 'ready'
    if _initializing:
        return 'warming_up'
    if _init_error:
        return 'error'
    return 'not_initialized'


def rebuild_rag_index(data_path: str | Path):
    global _initialized, _init_error

    from model.rag.service import get_rag_service

    settings = get_settings()
    service = get_rag_service()
    service.rebuild(
        data_path=data_path,
        storage_path=settings.chroma_path,
        api_key=settings.OPENAI_API_KEY,
        api_base=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_device=settings.EMBEDDING_DEVICE,
        chunk_size=settings.CHUNK_SIZE,
        collection_name=settings.CHROMA_COLLECTION_NAME,
    )
    _initialized = True
    _init_error = None
    manifest = load_index_manifest(settings.storage_path)
    persist_index_manifest(settings.storage_path, manifest.get('indexed_item_ids', []))
    return settings.chroma_path


def append_rag_documents(documents_data: list[dict]) -> tuple[Path, int]:
    global _initialized, _init_error

    if not documents_data:
        settings = get_settings()
        return settings.chroma_path, 0

    from model.rag.service import get_rag_service, has_persisted_rag_index

    settings = get_settings()
    manifest_storage_path = settings.storage_path
    chroma_path = settings.chroma_path
    manifest_storage_path.mkdir(parents=True, exist_ok=True)
    chroma_path.mkdir(parents=True, exist_ok=True)

    service = get_rag_service()
    service._api_key = settings.OPENAI_API_KEY
    service._api_base = settings.OPENAI_BASE_URL
    service._model = settings.OPENAI_MODEL
    service._temperature = 0.2

    if not has_persisted_rag_index(chroma_path, settings.CHROMA_COLLECTION_NAME):
        temp_export = settings.data_path / f'fraud_knowledge.append.{uuid.uuid4().hex}.json'
        temp_export.write_text(json.dumps(documents_data, ensure_ascii=False, indent=2), encoding='utf-8')
        try:
            service.build_or_load(
                data_path=temp_export,
                storage_path=chroma_path,
                api_key=settings.OPENAI_API_KEY,
                api_base=settings.OPENAI_BASE_URL,
                model=settings.OPENAI_MODEL,
                embedding_model=settings.EMBEDDING_MODEL,
                embedding_device=settings.EMBEDDING_DEVICE,
                chunk_size=settings.CHUNK_SIZE,
                collection_name=settings.CHROMA_COLLECTION_NAME,
            )
        finally:
            if temp_export.exists():
                temp_export.unlink()

        persist_index_manifest(manifest_storage_path, [str(item.get('id')) for item in documents_data if item.get('id')])
        _initialized = True
        _init_error = None
        return chroma_path, len(documents_data)

    appended_count = service.append_documents(
        documents_data=documents_data,
        storage_path=chroma_path,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_device=settings.EMBEDDING_DEVICE,
        chunk_size=settings.CHUNK_SIZE,
        collection_name=settings.CHROMA_COLLECTION_NAME,
    )

    manifest = load_index_manifest(manifest_storage_path)
    indexed_item_ids = set(manifest.get('indexed_item_ids', []))
    indexed_item_ids.update(str(item.get('id')) for item in documents_data if item.get('id'))
    persist_index_manifest(manifest_storage_path, list(indexed_item_ids))

    _initialized = True
    _init_error = None
    logger.info('Appended %d RAG documents into Chroma', appended_count)
    return chroma_path, appended_count


async def ask_question(question: str, session_id: str | None = None) -> dict:
    ensure_rag_initialized()

    if not session_id:
        session_id = str(uuid.uuid4())

    if not _initialized:
        raise RuntimeError(_init_error or 'RAG service is not initialized')

    try:
        from model.rag.service import get_rag_service
        settings = get_settings()
        service = get_rag_service()
        result = service.query(question, similarity_top_k=settings.SIMILARITY_TOP_K)
        return {
            'answer': result['answer'],
            'sources': result['sources'],
            'session_id': session_id,
        }
    except Exception as e:
        logger.error('RAG query failed: %s', e)
        raise RuntimeError(f'RAG query failed: {str(e)}') from e


def retrieve_relevant_sources(question: str, similarity_top_k: int | None = None) -> list[dict]:
    ensure_rag_initialized()

    if not _initialized:
        raise RuntimeError(_init_error or 'RAG service is not initialized')

    try:
        from model.rag.service import get_rag_service

        settings = get_settings()
        service = get_rag_service()
        top_k = similarity_top_k or settings.SIMILARITY_TOP_K
        return service.retrieve_sources(question, similarity_top_k=top_k)
    except Exception as e:
        logger.error('RAG retrieve failed: %s', e)
        raise RuntimeError(f'RAG retrieve failed: {str(e)}') from e

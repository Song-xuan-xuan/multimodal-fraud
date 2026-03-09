from fastapi import APIRouter, Depends, HTTPException
from app.schemas.rag import AskRequest, AskResponse
from app.services.rag_service import ask_question, ensure_rag_initialized, get_rag_init_state
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_rag(req: AskRequest, user=Depends(get_current_user)):
    try:
        result = await ask_question(req.question, req.session_id)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/health")
async def rag_health():
    try:
        state = get_rag_init_state()
        from model.rag.service import get_rag_service
        service = get_rag_service()
        return {
            'status': 'ready' if service.is_ready else state,
            'ready': service.is_ready,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG unavailable: {str(e)}")

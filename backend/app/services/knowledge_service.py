import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.knowledge_item import KnowledgeItem
from app.db.models.report import Report
from app.services.rag_service import append_rag_documents, load_index_manifest, rebuild_rag_index


async def create_knowledge_item(db: AsyncSession, payload: dict, submitted_by: str) -> KnowledgeItem:
    existing = await db.execute(select(KnowledgeItem).where(KnowledgeItem.item_id == payload["item_id"]))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="知识条目标识已存在")

    item = KnowledgeItem(
        item_id=payload["item_id"],
        item_type=payload.get("item_type", "case"),
        title=payload["title"],
        content=payload["content"],
        conclusion=payload.get("conclusion") or None,
        fraud_type=payload.get("fraud_type") or None,
        risk_level=payload.get("risk_level") or None,
        source=payload.get("source") or None,
        tags=payload.get("tags") or [],
        target_groups=payload.get("target_groups") or [],
        signals=payload.get("signals") or [],
        advice=payload.get("advice") or [],
        submitted_by=submitted_by,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(item)
    await db.flush()
    return item


async def list_knowledge_items(db: AsyncSession, status: str | None = None):
    stmt = select(KnowledgeItem).order_by(KnowledgeItem.created_at.desc())
    if status:
        stmt = stmt.where(KnowledgeItem.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


async def review_knowledge_item(db: AsyncSession, item_id: int, status: str, reviewer: str, reason: str | None) -> KnowledgeItem:
    result = await db.execute(select(KnowledgeItem).where(KnowledgeItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")

    item.status = status
    item.reviewed_by = reviewer
    item.reviewed_reason = reason or None
    item.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return item


def serialize_knowledge_item(item: KnowledgeItem) -> dict:
    return {
        "id": item.id,
        "item_id": item.item_id,
        "item_type": item.item_type,
        "title": item.title,
        "content": item.content,
        "conclusion": item.conclusion or "",
        "fraud_type": item.fraud_type or "",
        "risk_level": item.risk_level or "",
        "source": item.source or "",
        "tags": item.tags or [],
        "target_groups": item.target_groups or [],
        "signals": item.signals or [],
        "advice": item.advice or [],
        "status": item.status,
        "submitted_by": item.submitted_by or "",
        "reviewed_by": item.reviewed_by or "",
        "reviewed_reason": item.reviewed_reason or "",
        "created_at": item.created_at.isoformat() if item.created_at else "",
        "updated_at": item.updated_at.isoformat() if item.updated_at else "",
    }


async def export_approved_knowledge(db: AsyncSession) -> tuple[Path, int]:
    settings = get_settings()
    result = await db.execute(select(KnowledgeItem).where(KnowledgeItem.status == "approved").order_by(KnowledgeItem.updated_at.desc()))
    items = result.scalars().all()
    export_path = settings.data_path / "fraud_knowledge.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        {
            "id": item.item_id,
            "type": item.item_type,
            "title": item.title,
            "content": item.content,
            "conclusion": item.conclusion or "",
            "fraud_type": item.fraud_type or "",
            "risk_level": item.risk_level or "",
            "source": item.source or "",
            "tags": item.tags or [],
            "target_groups": item.target_groups or [],
            "signals": item.signals or [],
            "advice": item.advice or [],
        }
        for item in items
    ]

    export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return export_path, len(payload)


async def rebuild_knowledge_index(db: AsyncSession) -> dict:
    export_path, item_count = await export_approved_knowledge(db)

    result = await db.execute(
        select(KnowledgeItem)
        .where(KnowledgeItem.status == "approved")
        .order_by(KnowledgeItem.updated_at.desc())
    )
    items = result.scalars().all()

    settings = get_settings()
    manifest = load_index_manifest(settings.storage_path)
    indexed_item_ids = set(manifest.get("indexed_item_ids", []))

    new_payload = [
        {
            "id": item.item_id,
            "type": item.item_type,
            "title": item.title,
            "content": item.content,
            "conclusion": item.conclusion or "",
            "fraud_type": item.fraud_type or "",
            "risk_level": item.risk_level or "",
            "source": item.source or "",
            "tags": item.tags or [],
            "target_groups": item.target_groups or [],
            "signals": item.signals or [],
            "advice": item.advice or [],
        }
        for item in items
        if item.item_id not in indexed_item_ids
    ]

    if not items:
        return {
            "message": "当前没有已审核通过的知识条目可用于索引",
            "item_count": 0,
            "storage_path": str(settings.storage_path),
            "status": "ready",
        }

    if not new_payload:
        return {
            "message": "没有新的已审核知识需要追加，已保留现有索引",
            "item_count": item_count,
            "storage_path": str(settings.storage_path),
            "status": "ready",
        }

    storage_path, appended_count = append_rag_documents(new_payload)
    return {
        "message": f"反诈知识库索引追加完成，新增 {appended_count} 条知识",
        "item_count": item_count,
        "storage_path": str(storage_path),
        "status": "ready",
    }


async def create_knowledge_from_report(db: AsyncSession, report_id: int, submitted_by: str) -> KnowledgeItem:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    existing = await db.execute(select(KnowledgeItem).where(KnowledgeItem.item_id == f"report_{report.id}"))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="该举报已转入知识库")

    item = KnowledgeItem(
        item_id=f"report_{report.id}",
        item_type="case",
        title=f"举报案例：{report.type}",
        content=report.description,
        conclusion="来自用户举报的候选案例，建议管理员进一步补充风险信号与处置建议。",
        fraud_type=report.type,
        risk_level="medium",
        source=report.url or "用户举报",
        tags=[report.type],
        target_groups=[],
        signals=[],
        advice=[],
        status="pending",
        submitted_by=submitted_by,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(item)
    await db.flush()
    return item

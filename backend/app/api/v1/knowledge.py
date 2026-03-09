from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.knowledge import (
    KnowledgeItemCreate,
    KnowledgeItemListResponse,
    KnowledgeItemResponse,
    KnowledgeItemReviewRequest,
    KnowledgeRebuildResponse,
)
from app.services.knowledge_service import (
    create_knowledge_item,
    list_knowledge_items,
    rebuild_knowledge_index,
    review_knowledge_item,
    serialize_knowledge_item,
)

router = APIRouter()


@router.get("/items", response_model=KnowledgeItemListResponse)
async def list_knowledge(
    status: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await list_knowledge_items(db, status=status)
    payload = [KnowledgeItemResponse(**serialize_knowledge_item(item)) for item in items]
    return KnowledgeItemListResponse(items=payload, total=len(payload))


@router.post("/items", response_model=KnowledgeItemResponse)
async def create_knowledge(
    req: KnowledgeItemCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await create_knowledge_item(db, req.model_dump(), submitted_by=user.username)
    return KnowledgeItemResponse(**serialize_knowledge_item(item))


@router.post("/items/{item_id}/review", response_model=KnowledgeItemResponse)
async def review_knowledge(
    item_id: int,
    req: KnowledgeItemReviewRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await review_knowledge_item(db, item_id=item_id, status=req.status, reviewer=user.username, reason=req.reason)
    return KnowledgeItemResponse(**serialize_knowledge_item(item))


@router.post("/rebuild-index", response_model=KnowledgeRebuildResponse)
async def rebuild_index(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await rebuild_knowledge_index(db)
        return KnowledgeRebuildResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

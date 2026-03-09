from fastapi import APIRouter

from .admin import router as admin_router
from .alerts import router as alerts_router
from .auth import router as auth_router
from .chat import router as chat_router
from .community import router as community_router
from .crawler import router as crawler_router
from .detection import router as detection_router
from .education import router as education_router
from .fact_check import router as fact_check_router
from .feedback import router as feedback_router
from .map import router as map_router
from .media import router as media_router
from .news import router as news_router
from .knowledge import router as knowledge_router
from .profile import router as profile_router
from .rag import router as rag_router
from .report import router as report_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(news_router, prefix="/news", tags=["news"])
api_router.include_router(detection_router, prefix="/detection", tags=["detection"])
api_router.include_router(fact_check_router, prefix="/fact-check", tags=["fact-check"])
api_router.include_router(rag_router, prefix="/rag", tags=["rag"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(map_router, prefix="/map", tags=["map"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(education_router, prefix="/education", tags=["education"])
api_router.include_router(community_router, prefix="/community", tags=["community"])
api_router.include_router(report_router, prefix="/report", tags=["report"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(crawler_router, prefix="/crawler", tags=["crawler"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])

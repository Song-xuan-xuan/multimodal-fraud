"""Profile API — user profile, role defense, and personalized suggestions."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.profile import (
    SuggestionResponse,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.services.profile_service import (
    _profile_to_data,
    build_role_defense,
    generate_suggestions,
    get_behavior_stats,
    get_or_create_profile,
    update_profile,
)

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_or_create_profile(db, user.id)
    profile_data = _profile_to_data(profile)
    stats = await get_behavior_stats(db, user.username, user.id)
    role_defense = build_role_defense(profile_data)
    return UserProfileResponse(
        username=user.username,
        profile=profile_data,
        stats=stats,
        role_defense=role_defense,
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await update_profile(db, user.id, data)
    profile_data = _profile_to_data(profile)
    stats = await get_behavior_stats(db, user.username, user.id)
    role_defense = build_role_defense(profile_data)
    return UserProfileResponse(
        username=user.username,
        profile=profile_data,
        stats=stats,
        role_defense=role_defense,
    )


@router.get("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_or_create_profile(db, user.id)
    profile_data = _profile_to_data(profile)
    stats = await get_behavior_stats(db, user.username, user.id)
    suggestions = await generate_suggestions(profile_data, stats)
    return SuggestionResponse(suggestions=suggestions)

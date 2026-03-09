import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import get_db
from app.db.models.news import NewsArticle
from app.schemas.map import (
    ChinaMapDataResponse,
    ProvinceDetailResponse,
    ProvinceMapStat,
    ProvinceNewsItem,
)

router = APIRouter()
settings = get_settings()

_CHINA_PROVINCES = [
    "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江", "江苏",
    "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南",
    "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏",
    "宁夏", "新疆", "香港", "澳门",
]

_CITY_TO_PROVINCE = {
    "广州": "广东", "深圳": "广东", "佛山": "广东", "东莞": "广东", "珠海": "广东",
    "杭州": "浙江", "宁波": "浙江", "温州": "浙江", "嘉兴": "浙江", "绍兴": "浙江",
    "南京": "江苏", "苏州": "江苏", "无锡": "江苏", "常州": "江苏", "徐州": "江苏",
    "成都": "四川", "绵阳": "四川", "德阳": "四川",
    "武汉": "湖北", "宜昌": "湖北", "襄阳": "湖北",
    "长沙": "湖南", "株洲": "湖南", "湘潭": "湖南",
    "西安": "陕西", "宝鸡": "陕西",
    "郑州": "河南", "洛阳": "河南",
    "青岛": "山东", "济南": "山东", "烟台": "山东",
    "哈尔滨": "黑龙江", "长春": "吉林", "沈阳": "辽宁",
    "南宁": "广西", "呼和浩特": "内蒙古", "拉萨": "西藏", "银川": "宁夏", "乌鲁木齐": "新疆",
    "海口": "海南", "福州": "福建", "南昌": "江西", "合肥": "安徽", "贵阳": "贵州", "昆明": "云南",
    "兰州": "甘肃", "西宁": "青海", "台北": "台湾",
}


def _normalize_province(location: str) -> str:
    if not location:
        return "未知"

    raw = location.strip()
    normalized = (
        raw.replace("壮族自治区", "")
        .replace("维吾尔自治区", "")
        .replace("回族自治区", "")
        .replace("自治区", "")
        .replace("特别行政区", "")
        .replace("省", "")
        .replace("市", "")
    )

    alias_map = {
        "北京": "北京",
        "天津": "天津",
        "上海": "上海",
        "重庆": "重庆",
        "内蒙古": "内蒙古",
        "广西": "广西",
        "西藏": "西藏",
        "宁夏": "宁夏",
        "新疆": "新疆",
        "香港": "香港",
        "澳门": "澳门",
    }

    if normalized in alias_map:
        return alias_map[normalized]

    for city, province in _CITY_TO_PROVINCE.items():
        if city in normalized or city in raw:
            return province

    for province in _CHINA_PROVINCES:
        if province in normalized or province in raw:
            return province

    return "未知"


@router.get("/china-geojson")
async def get_china_geojson():
    geojson_path = settings.BASE_DIR / "app" / "static" / "geojson" / "china.json"
    if not geojson_path.exists():
        raise HTTPException(status_code=404, detail="china.json 不存在")

    try:
        with geojson_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="china.json 格式错误") from exc

    return JSONResponse(content=data)


@router.get("/china-data", response_model=ChinaMapDataResponse)
async def get_china_map_data(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsArticle.location, NewsArticle.label))
    rows = result.all()

    stats_map: dict[str, ProvinceMapStat] = {}
    total_news = 0
    total_fake = 0

    for location, label in rows:
        province = _normalize_province(location or "")
        if province not in stats_map:
            stats_map[province] = ProvinceMapStat(province=province, value=0)

        item = stats_map[province]
        item.total += 1
        total_news += 1

        normalized_label = (label or "").lower()
        if any(token in normalized_label for token in ["fake", "谣", "假"]):
            item.fake_count += 1
            item.value = item.fake_count
            total_fake += 1
        elif any(token in normalized_label for token in ["real", "真", "可信"]):
            item.real_count += 1
            item.value = item.fake_count
        else:
            item.unknown_count += 1
            item.value = item.fake_count

    provinces = sorted(stats_map.values(), key=lambda x: x.total, reverse=True)
    return ChinaMapDataResponse(
        provinces=provinces,
        total_news=total_news,
        total_fake=total_fake,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/province/{province}", response_model=ProvinceDetailResponse)
async def get_province_detail(
    province: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    label: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    all_result = await db.execute(
        select(NewsArticle).where(func.coalesce(NewsArticle.location, "").contains(province))
    )
    all_items = all_result.scalars().all()

    if not all_items:
        raise HTTPException(status_code=404, detail=f"未找到省份 {province} 的数据")

    stats = ProvinceMapStat(province=province, value=0)
    for news in all_items:
        stats.total += 1
        normalized_label = (news.label or "").lower()
        if any(token in normalized_label for token in ["fake", "谣", "假"]):
            stats.fake_count += 1
        elif any(token in normalized_label for token in ["real", "真", "可信"]):
            stats.real_count += 1
        else:
            stats.unknown_count += 1
    stats.value = stats.fake_count

    filtered_items = all_items
    if label:
        normalized_filter = label.lower().strip()
        if normalized_filter in {"fake", "谣言", "谣", "假"}:
            filtered_items = [
                news for news in all_items if any(token in (news.label or "").lower() for token in ["fake", "谣", "假"])
            ]
        elif normalized_filter in {"real", "事实", "真", "可信"}:
            filtered_items = [
                news for news in all_items if any(token in (news.label or "").lower() for token in ["real", "真", "可信"])
            ]

    total = len(filtered_items)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    effective_page = min(page, total_pages) if total_pages > 0 else 1
    start = (effective_page - 1) * page_size
    end = start + page_size
    paged_items = filtered_items[start:end]

    response_items = [
        ProvinceNewsItem(
            news_id=news.news_id,
            title=news.title or "",
            label=news.label or "",
            platform=news.platform or "",
            publish_time=news.publish_time or "",
            location=news.location or "",
        )
        for news in paged_items
    ]

    return ProvinceDetailResponse(
        province=province,
        stats=stats,
        items=response_items,
        total=total,
        page=effective_page,
        page_size=page_size,
        total_pages=total_pages,
    )

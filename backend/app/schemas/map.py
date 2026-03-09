from pydantic import BaseModel, Field


class ProvinceMapStat(BaseModel):
    province: str
    total: int = 0
    fake_count: int = 0
    real_count: int = 0
    unknown_count: int = 0
    value: int = 0


class ProvinceNewsItem(BaseModel):
    news_id: str
    title: str = ""
    label: str = ""
    platform: str = ""
    publish_time: str = ""
    location: str = ""


class ChinaMapDataResponse(BaseModel):
    provinces: list[ProvinceMapStat] = Field(default_factory=list)
    total_news: int = 0
    total_fake: int = 0
    updated_at: str = ""


class ProvinceDetailResponse(BaseModel):
    province: str
    stats: ProvinceMapStat
    items: list[ProvinceNewsItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

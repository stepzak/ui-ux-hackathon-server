from typing import Optional

from pydantic import BaseModel

class VersionMetrics(BaseModel):
    visits_count: int
    hits_count: int
    avg_visit_duration: float
    bounce_rate: float
    avg_page_views: float
    error_rate: float
    not_bounce_rate: float
    link_click_rate: float
    form_view_count: int
    form_submit_count: int
    vk_contact_clicks: int
    tg_contact_clicks: int
    device_category_distribution: Optional[dict[str, int]] = None
    os_distribution: Optional[dict[str, int]] = None

    class Config:
        extra = "allow"
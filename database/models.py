from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserInteraction:
    id: Optional[int]
    user_id: int
    username: Optional[str]
    request_text: str
    response_text: str
    created_at: datetime


@dataclass
class PriceAlert:
    id: Optional[int]
    user_id: int
    symbol: str
    target_price: float
    alert_type: str  # 'above' or 'below'
    is_active: bool
    created_at: datetime


@dataclass
class UserSubscription:
    id: Optional[int]
    user_id: int
    subscription_type: str  # 'crypto', 'stocks', 'news'
    is_active: bool
    created_at: datetime

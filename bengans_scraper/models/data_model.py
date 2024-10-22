from pydantic import BaseModel
from typing import Optional

class BengansProducts(BaseModel):
    product_name: str
    band_name: str
    discounted_price: Optional[float] = None
    original_price: Optional[float] = None
    current_price: float
    status: str
    media_format: str
    product_link: str

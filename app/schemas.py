from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Item schemas
class ItemBase(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    expiry_date: Optional[str] = None

class Item(ItemBase):
    id: str = Field(alias="_id")
    insert_date: datetime

    class Config:
        populate_by_name = True

# Clock-in schemas
class ClockInBase(BaseModel):
    email: str
    location: str

class ClockInCreate(ClockInBase):
    pass

class ClockInUpdate(BaseModel):
    email: Optional[str] = None
    location: Optional[str] = None

class ClockIn(ClockInBase):
    id: str = Field(alias="_id")
    insert_datetime: datetime

    class Config:
        populate_by_name = True
        
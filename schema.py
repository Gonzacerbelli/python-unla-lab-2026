from pydantic import BaseModel, field_validator
from datetime import date, time


class ProductCreate(BaseModel):
    name: str
    price: float

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    creation_date: date
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("open", "close"):
            raise ValueError("status must be 'open' or 'close'")
        return v

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartItemProduct(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    id: int
    product: CartItemProduct
    quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    creation_date: date
    status: str
    items: list[CartItemResponse]

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    date: date
    time: time
    cart_id: int

    class Config:
        from_attributes = True


class SaleUpdate(BaseModel):
    date: date
    time: time

    class Config:
        from_attributes = True


class SaleCartAssign(BaseModel):
    cart_id: int

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    date: date
    time: time
    total_price: float
    cart: CartResponse

    class Config:
        from_attributes = True
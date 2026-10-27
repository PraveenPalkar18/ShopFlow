from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.product_names import normalize_product_name


class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class UserOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_admin: bool


class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if isinstance(value, str):
            value = normalize_product_name(value)
            if not value:
                raise ValueError("Product name must not be blank")
        return value


class ProductOutput(ProductInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool


class CartInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=100)


class CartLine(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    line_total: float


class OrderOutput(BaseModel):
    id: int
    status: str
    total: float
    items: list[CartLine]

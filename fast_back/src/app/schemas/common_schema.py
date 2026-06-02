from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class ApiResponseDTO(BaseModel, Generic[T]):
  success: bool
  message: str
  date: T | None = None #Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthRsp(BaseModel):
    is_healthy: bool


@router.get(
    "/health",
    response_model=HealthRsp,
)
def get_health() -> HealthRsp:
    return HealthRsp(is_healthy=True)

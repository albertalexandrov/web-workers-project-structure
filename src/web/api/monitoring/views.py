from fastapi import APIRouter

router = APIRouter(tags=['Здоровье'])


@router.get("/health", status_code=204)
def health_check() -> None:
    pass

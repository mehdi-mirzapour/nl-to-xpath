from fastapi import APIRouter

router = APIRouter()


@router.get("/sent-task-mapper/", tags=["Pre-processors"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


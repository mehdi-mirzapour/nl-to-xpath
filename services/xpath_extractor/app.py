from fastapi import APIRouter

router = APIRouter()


@router.get("/xpath-extract/", tags=["Processors"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


from fastapi import APIRouter

router = APIRouter()


@router.get("/html_cut/", tags=["Pre-processors"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_users():
    return [{"name": "John Doe"}, {"name": "Jane Doe"}]
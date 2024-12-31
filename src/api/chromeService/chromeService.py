from fastapi import APIRouter

router = APIRouter(prefix="/chrome")


@router.get("/items/")
async def read_items():
    return {"message": "Hello World"}

@router.get('/admin/ls')
async def admin_list():
    return {}


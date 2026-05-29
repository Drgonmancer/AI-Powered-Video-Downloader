from fastapi import APIRouter

from services.watermark_service import get_watermark_status

router = APIRouter(prefix="/api/watermark", tags=["水印"])


@router.get("/status")
async def watermark_status():
    return {"success": True, "data": get_watermark_status()}

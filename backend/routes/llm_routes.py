from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from middleware.auth_middleware import get_current_user
from services.llm_provider_service import (
    create_provider,
    delete_provider,
    list_providers,
    set_default_provider,
)

router = APIRouter(prefix="/api/llm", tags=["大模型配置"])


class LlmProviderCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=80)
    api_key: str = Field(..., min_length=1)
    base_url: str = ""
    model: str = ""


@router.get("/providers")
async def get_providers(current_user: dict = Depends(get_current_user)):
    items = list_providers(current_user["id"])
    return {"success": True, "data": items}


@router.post("/providers")
async def add_provider(
    body: LlmProviderCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        item = create_provider(
            current_user["id"],
            body.display_name,
            body.api_key,
            body.base_url,
            body.model,
        )
        return {"success": True, "data": item}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/providers/{provider_id}")
async def remove_provider(
    provider_id: int,
    current_user: dict = Depends(get_current_user),
):
    if not delete_provider(current_user["id"], provider_id):
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "message": "已删除"}


@router.post("/providers/{provider_id}/default")
async def make_default(
    provider_id: int,
    current_user: dict = Depends(get_current_user),
):
    item = set_default_provider(current_user["id"], provider_id)
    if not item:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "data": item}

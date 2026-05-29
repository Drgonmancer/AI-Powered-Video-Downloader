from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from services.membership_service import (
    get_membership_status,
    create_checkout_session,
    cancel_subscription,
    check_permission,
    handle_webhook_event,
    verify_checkout_session
)
from middleware.auth_middleware import get_current_user, get_optional_user

router = APIRouter(prefix="/api/membership", tags=["会员"])


class CheckoutRequest(BaseModel):
    plan: str


@router.get("/plans")
async def get_plans():
    from config.stripe_config import get_stripe_config
    
    config = get_stripe_config()
    
    return {
        "success": True,
        "data": {
            "plans": {
                "free": {
                    "name": "免费版",
                    "price": 0,
                    "features": {
                        "max_downloads_per_day": 5,
                        "max_quality": "720p",
                        "max_ai_summaries_per_day": 3,
                        "batch_download": False
                    }
                },
                "basic": {
                    "name": config["prices"]["basic"]["name"],
                    "price": config["prices"]["basic"]["amount"],
                    "currency": config["prices"]["basic"]["currency"],
                    "period": "月",
                    "features": {
                        "max_downloads_per_day": 50,
                        "max_quality": "1080p",
                        "max_ai_summaries_per_day": 30,
                        "batch_download": True
                    }
                },
                "pro": {
                    "name": config["prices"]["pro"]["name"],
                    "price": config["prices"]["pro"]["amount"],
                    "currency": config["prices"]["pro"]["currency"],
                    "period": "月",
                    "features": {
                        "max_downloads_per_day": -1,
                        "max_quality": "8k",
                        "max_ai_summaries_per_day": -1,
                        "batch_download": True
                    }
                }
            }
        }
    }


@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    status = get_membership_status(current_user["id"])
    
    return {
        "success": True,
        "data": status
    }


@router.post("/checkout")
async def checkout(body: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    try:
        checkout_url = create_checkout_session(
            user_id=current_user["id"],
            email=current_user["email"],
            plan=body.plan
        )
        
        return {
            "success": True,
            "data": {
                "checkout_url": checkout_url
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建支付会话失败: {str(e)}")


@router.post("/cancel")
async def cancel(current_user: dict = Depends(get_current_user)):
    try:
        success = cancel_subscription(current_user["id"])
        
        return {
            "success": True,
            "message": "订阅已取消，将在当前周期结束后生效",
            "data": {"canceled": success}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消订阅失败: {str(e)}")


@router.get("/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    from services.membership_service import (
        get_download_limits,
        check_daily_download_limit,
        get_daily_reset_info,
    )

    allowed, used, remaining = check_daily_download_limit(current_user["id"])
    membership = get_membership_status(current_user["id"])
    current_plan = membership.get("plan", "free")
    limits = get_download_limits()
    limit = limits.get(current_plan, 5)
    reset_info = get_daily_reset_info()

    return {
        "success": True,
        "data": {
            "plan": current_plan,
            "downloads": {
                "used": used if used >= 0 else 0,
                "limit": limit,
                "remaining": remaining,
            },
            "is_unlimited": limit == -1,
            "usage_date": reset_info["usage_date"],
            "resets_at": reset_info["resets_at"],
            "reset_timezone": reset_info["timezone"],
            "reset_policy": reset_info["reset_policy"],
        }
    }


@router.post("/verify-session")
async def verify_session(request: Request, current_user: dict = Depends(get_current_user)):
    import json
    body = await request.json()
    session_id = body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="缺少session_id参数")

    try:
        result = verify_checkout_session(session_id, current_user["id"])
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证支付会话失败: {str(e)}")


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="缺少Stripe签名")
    
    try:
        result = handle_webhook_event(payload, signature)
        return {"status": "ok", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理Webhook失败: {str(e)}")


from datetime import datetime

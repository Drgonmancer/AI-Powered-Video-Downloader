import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database.connection import get_db_connection

# 每日下载次数按「北京时间 0 点」自然日切换（新日期 = 新计数，无需定时任务）
USAGE_TZ = ZoneInfo("Asia/Shanghai")


def get_usage_date_str(now: Optional[datetime] = None) -> str:
    if now is None:
        now = datetime.now(USAGE_TZ)
    else:
        now = now.astimezone(USAGE_TZ) if now.tzinfo else now.replace(tzinfo=USAGE_TZ)
    return now.strftime("%Y-%m-%d")


def get_daily_reset_info(now: Optional[datetime] = None) -> Dict[str, Any]:
    if now is None:
        now = datetime.now(USAGE_TZ)
    else:
        now = now.astimezone(USAGE_TZ) if now.tzinfo else now.replace(tzinfo=USAGE_TZ)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_reset = today_start + timedelta(days=1)
    return {
        "usage_date": now.strftime("%Y-%m-%d"),
        "timezone": "Asia/Shanghai",
        "resets_at": next_reset.isoformat(),
        "reset_policy": "daily_midnight",
    }
from config.stripe_config import get_stripe_config

stripe.api_key = get_stripe_config()["secret_key"]


def _stripe_object_to_dict(obj) -> Dict[str, Any]:
    """将 Stripe Event 中的 object 转为普通 dict（兼容 stripe-python v15+）。"""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "keys"):
        return {k: obj[k] for k in obj.keys()}
    return {}


def _payment_reference_from_session(session_data: Dict[str, Any]) -> Optional[str]:
    """订阅 Checkout 可能没有 payment_intent，用 session id 保证支付记录幂等。"""
    return session_data.get("payment_intent") or (
        f"cs_{session_data['id']}" if session_data.get("id") else None
    )


def get_membership_status(user_id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT plan, status, current_period_start, current_period_end, 
               cancel_at_period_end, stripe_subscription_id
        FROM memberships 
        WHERE user_id = ?
    """, (user_id,))
    
    membership = cursor.fetchone()
    conn.close()
    
    if not membership:
        return {
            "plan": "free",
            "status": "active",
            "is_active": True,
            "current_period_start": None,
            "current_period_end": None,
            "cancel_at_period_end": False,
        }
    
    membership_dict = dict(membership)
    
    if membership_dict['status'] == 'canceled':
        membership_dict['is_active'] = False
    elif membership_dict['status'] == 'past_due':
        membership_dict['is_active'] = False
    elif membership_dict['current_period_end']:
        end_str = membership_dict['current_period_end']
        try:
            end_date = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
        if datetime.now() > end_date:
            membership_dict['is_active'] = False
        else:
            membership_dict['is_active'] = True
    else:
        membership_dict['is_active'] = True
    
    return membership_dict


def _valid_stripe_price_id(price_id: Optional[str]) -> bool:
    if not price_id or not isinstance(price_id, str):
        return False
    pid = price_id.strip()
    return pid.startswith("price_") and "你的" not in pid and len(pid) > 10


def _checkout_line_item(price_config: dict) -> dict:
    """有 Dashboard Price ID 则用订阅价；否则用 price_data 动态创建（免配 price_xxx）。"""
    if _valid_stripe_price_id(price_config.get("price_id")):
        return {"price": price_config["price_id"], "quantity": 1}
    return {
        "price_data": {
            "currency": price_config.get("currency", "cny"),
            "unit_amount": int(price_config["amount"]),
            "recurring": {"interval": "month"},
            "product_data": {"name": price_config.get("name", "会员订阅")},
        },
        "quantity": 1,
    }


def create_checkout_session(user_id: int, email: str, plan: str) -> str:
    config = get_stripe_config()

    secret_key = (config.get("secret_key") or "").strip()
    if not secret_key:
        raise ValueError("未配置 Stripe Secret Key，请创建 backend/config/stripe_config.py")

    stripe.api_key = secret_key

    if plan not in config["prices"]:
        raise ValueError(f"无效的套餐: {plan}")

    price_config = config["prices"][plan]

    membership = get_membership_status(user_id)
    if membership["plan"] != "free" and membership["is_active"]:
        raise ValueError("您已有活跃的订阅")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[_checkout_line_item(price_config)],
        mode="subscription",
        customer_email=email,
        success_url=f"{config['success_url']}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=config["cancel_url"],
        metadata={
            "user_id": str(user_id),
            "plan": plan,
        },
    )

    return session.url


def handle_webhook_event(payload: bytes, signature: str) -> Dict[str, Any]:
    import traceback
    config = get_stripe_config()

    print(f"[Webhook] ========================================")
    print(f"[Webhook] 收到事件, 签名验证中...")

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, config["webhook_secret"]
        )
        print(f"[Webhook] 签名验证成功! 事件类型: {event['type']}")
    except stripe.error.SignatureVerificationError as e:
        print(f"[Webhook] 签名验证失败: {e}")
        raise ValueError(f"Webhook签名验证失败: {e}")

    event_type = event["type"]
    event_data = _stripe_object_to_dict(event["data"]["object"])
    result = {"event_type": event_type, "processed": False}

    # 只处理会触发会员状态变更的核心事件
    if event_type not in ("checkout.session.completed", "customer.subscription.updated",
                          "customer.subscription.deleted"):
        print(f"[Webhook] 跳过事件: {event_type} (无需处理)")
        return result

    print(f"[Webhook] 开始处理: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            metadata = event_data.get("metadata") or {}
            raw_user_id = metadata.get("user_id")
            plan = metadata.get("plan")

            if not raw_user_id:
                print(f"[Webhook] checkout.session.completed 缺少 metadata.user_id, 跳过")
                return result
            if not plan:
                print(f"[Webhook] checkout.session.completed 缺少 metadata.plan, 跳过")
                return result

            user_id = int(raw_user_id)
            print(f"[Webhook] 支付完成! user_id={user_id}, plan={plan}")
            print(f"[Webhook] customer={event_data.get('customer')}, subscription={event_data.get('subscription')}")

            _update_membership_after_payment(
                user_id=user_id, plan=plan,
                stripe_customer_id=event_data.get("customer"),
                stripe_subscription_id=event_data.get("subscription")
            )
            print(f"[Webhook] 会员状态已更新!")

            _record_payment(
                user_id=user_id,
                stripe_payment_intent_id=_payment_reference_from_session(event_data),
                amount=event_data.get("amount_total", 0),
                currency=event_data.get("currency", "cny"),
                status="succeeded",
                plan=plan
            )
            print(f"[Webhook] 支付记录已保存!")
            result["processed"] = True

        elif event_type == "customer.subscription.updated":
            customer_id = event_data.get("customer")
            user_id = _get_user_by_stripe_customer(customer_id)
            if user_id:
                _update_subscription_dates(
                    user_id=user_id,
                    period_start=event_data.get("current_period_start"),
                    period_end=event_data.get("current_period_end"),
                    cancel_at_period_end=event_data.get("cancel_at_period_end", False)
                )
                result["processed"] = True

        elif event_type == "customer.subscription.deleted":
            customer_id = event_data.get("customer")
            user_id = _get_user_by_stripe_customer(customer_id)
            if user_id:
                _cancel_membership(user_id)
                result["processed"] = True

    except Exception as e:
        print(f"[Webhook] 处理事件出错: {e}")
        traceback.print_exc()
        raise

    print(f"[Webhook] 处理完成: processed={result['processed']}")
    return result


def cancel_subscription(user_id: int) -> bool:
    membership = get_membership_status(user_id)
    
    if not membership.get("stripe_subscription_id"):
        raise ValueError("没有找到活跃的订阅")
    
    try:
        stripe.Subscription.modify(
            membership["stripe_subscription_id"],
            cancel_at_period_end=True
        )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE memberships SET cancel_at_period_end = 1, updated_at = ? 
               WHERE user_id = ?""",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id)
        )
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        raise ValueError(f"取消订阅失败: {e}")


def check_permission(user_id: int, required_action: str) -> bool:
    membership = get_membership_status(user_id)
    
    if not membership["is_active"]:
        return False
    
    permissions = {
        "free": {
            "max_downloads_per_day": 5,
            "max_quality": "720p",
            "max_ai_summaries_per_day": 3,
            "batch_download": False
        },
        "basic": {
            "max_downloads_per_day": 50,
            "max_quality": "1080p",
            "max_ai_summaries_per_day": 30,
            "batch_download": True
        },
        "pro": {
            "max_downloads_per_day": -1,
            "max_quality": "8k",
            "max_ai_summaries_per_day": -1,
            "batch_download": True
        }
    }
    
    return required_action in permissions.get(membership["plan"], permissions["free"])


def get_download_limits() -> dict:
    return {
        "free": 5,
        "basic": 50,
        "pro": -1,
    }


def check_daily_download_limit(user_id: int) -> tuple:
    from database.connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    membership = get_membership_status(user_id)
    plan = membership.get("plan", "free")
    limits = get_download_limits()
    limit = limits.get(plan, 5)

    if limit == -1:
        conn.close()
        return True, -1, -1

    today = get_usage_date_str()
    cursor.execute(
        "SELECT download_count FROM daily_usage WHERE user_id = ? AND usage_date = ?",
        (user_id, today),
    )
    row = cursor.fetchone()
    used = row["download_count"] if row else 0
    remaining = limit - used
    conn.close()

    if used >= limit:
        return False, used, 0
    return True, used, remaining


def get_usage_snapshot(user_id: int) -> Dict[str, Any]:
    """当前用户今日下载用量（供 API 响应与前端刷新）。"""
    allowed, used, remaining = check_daily_download_limit(user_id)
    membership = get_membership_status(user_id)
    plan = membership.get("plan", "free")
    limits = get_download_limits()
    limit = limits.get(plan, 5)
    reset_info = get_daily_reset_info()
    return {
        "plan": plan,
        "downloads": {
            "used": used if used >= 0 else 0,
            "limit": limit,
            "remaining": remaining,
        },
        "is_unlimited": limit == -1,
        "usage_date": reset_info["usage_date"],
        "resets_at": reset_info["resets_at"],
        "reset_timezone": reset_info["timezone"],
    }


def increment_daily_download_count(user_id: int) -> int:
    from database.connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    today = get_usage_date_str()
    cursor.execute(
        """INSERT INTO daily_usage (user_id, usage_date, download_count)
           VALUES (?, ?, 1)
           ON CONFLICT(user_id, usage_date)
           DO UPDATE SET download_count = download_count + 1""",
        (user_id, today),
    )
    conn.commit()

    cursor.execute(
        "SELECT download_count FROM daily_usage WHERE user_id = ? AND usage_date = ?",
        (user_id, today),
    )
    row = cursor.fetchone()
    conn.close()

    return row["download_count"] if row else 0


def _update_membership_after_payment(user_id: int, plan: str,
                                     stripe_customer_id: Optional[str],
                                     stripe_subscription_id: Optional[str]):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    from dateutil.relativedelta import relativedelta
    period_end = now + relativedelta(months=1)
    period_end_str = period_end.strftime('%Y-%m-%d %H:%M:%S')

    print(f"[DB] 写入会员表 - user_id={user_id}, plan={plan}, 到期={period_end_str}")
    print(f"[DB] stripe_customer={stripe_customer_id}, stripe_subscription={stripe_subscription_id}")

    cursor.execute("""
        INSERT OR REPLACE INTO memberships
        (user_id, plan, status, stripe_customer_id, stripe_subscription_id,
         current_period_start, current_period_end, updated_at)
        VALUES (?, ?, 'active', ?, ?, ?, ?, ?)
    """, (user_id, plan, stripe_customer_id, stripe_subscription_id, now_str, period_end_str, now_str))

    conn.commit()

    cursor.execute("SELECT * FROM memberships WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    print(f"[DB] 写入结果: {dict(result) if result else 'None'}")
    conn.close()


def _record_payment(user_id: int, stripe_payment_intent_id: Optional[str],
                    amount: int, currency: str, status: str, plan: str):
    if not stripe_payment_intent_id:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM payments WHERE stripe_payment_intent_id = ?",
        (stripe_payment_intent_id,),
    )
    if cursor.fetchone():
        conn.close()
        print(f"[DB] 支付记录已存在，跳过: {stripe_payment_intent_id}")
        return

    cursor.execute("""
        INSERT INTO payments
        (user_id, stripe_payment_intent_id, amount, currency, status, plan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, stripe_payment_intent_id, amount, currency, status, plan))

    conn.commit()
    conn.close()


def _update_subscription_dates(user_id: int, period_start: Optional[int], 
                                period_end: Optional[int], cancel_at_period_end: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    start_str = datetime.fromtimestamp(period_start).strftime('%Y-%m-%d %H:%M:%S') if period_start else None
    end_str = datetime.fromtimestamp(period_end).strftime('%Y-%m-%d %H:%M:%S') if period_end else None
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        UPDATE memberships 
        SET current_period_start = ?, current_period_end = ?, 
            cancel_at_period_end = ?, updated_at = ?
        WHERE user_id = ?
    """, (start_str, end_str, 1 if cancel_at_period_end else 0, now, user_id))
    
    conn.commit()
    conn.close()


def _cancel_membership(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        "UPDATE memberships SET status = 'canceled', updated_at = ? WHERE user_id = ?",
        (now, user_id)
    )
    
    conn.commit()
    conn.close()


def verify_checkout_session(session_id: str, user_id: int) -> Dict[str, Any]:
    print(f"[VerifySession] ========================================")
    print(f"[VerifySession] 验证会话: {session_id}, 用户ID: {user_id}")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        session_data = _stripe_object_to_dict(session)
        print(f"[VerifySession] 会话状态: {session_data.get('status')}, 支付状态: {session_data.get('payment_status')}")
        print(f"[VerifySession] metadata: {session_data.get('metadata')}")
    except Exception as e:
        print(f"[VerifySession] 获取Stripe会话失败: {e}")
        raise ValueError(f"获取Stripe会话失败: {e}")

    metadata = session_data.get("metadata") or {}
    meta_user_id = metadata.get("user_id")
    if meta_user_id and int(meta_user_id) != user_id:
        raise ValueError("支付会话与当前登录用户不匹配")

    plan = metadata.get("plan")
    if not plan:
        raise ValueError("支付会话缺少套餐信息")

    is_paid = (
        session_data.get("status") == "complete"
        and session_data.get("payment_status") in ("paid", "no_payment_required")
    )

    if is_paid:
        print(f"[VerifySession] 支付已确认! 套餐: {plan}")

        _update_membership_after_payment(
            user_id=user_id,
            plan=plan,
            stripe_customer_id=session_data.get("customer"),
            stripe_subscription_id=session_data.get("subscription"),
        )

        _record_payment(
            user_id=user_id,
            stripe_payment_intent_id=_payment_reference_from_session(session_data),
            amount=session_data.get("amount_total", 0),
            currency=session_data.get("currency", "cny"),
            status="succeeded",
            plan=plan,
        )

        print(f"[VerifySession] 会员状态已更新!")
        return {"verified": True, "plan": plan, "status": session_data.get("status")}
    else:
        print(f"[VerifySession] 支付未完成: status={session_data.get('status')}, payment_status={session_data.get('payment_status')}")
        return {
            "verified": False,
            "status": session_data.get("status"),
            "payment_status": session_data.get("payment_status"),
        }


def _get_user_by_stripe_customer(stripe_customer_id: Optional[str]) -> Optional[int]:
    if not stripe_customer_id:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT user_id FROM memberships WHERE stripe_customer_id = ?",
        (stripe_customer_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result["user_id"] if result else None

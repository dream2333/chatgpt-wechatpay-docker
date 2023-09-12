import json
import secrets
import time
from typing import List, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.logger import logger
from fastapi.params import Depends
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.routing import APIRouter
from pydantic import UUID4

from app.auth import check_balance, check_jwt, create_jwt, check_user
from app.models import Context, SystemPrompt, User
from app.schemas import (
    ContextGetPydantic,
    ContextListPydantic,
    Message,
    PromptCreatePydantic,
    PromptListPydantic,
    UserPydantic,
)
from chat.openai import Assistant
from chat.wechatapi import WeChatAPI
import settings
from wechatpayv3 import WeChatPay, WeChatPayType
from random import sample
from string import ascii_letters, digits

router = APIRouter(prefix="/api", tags=["chatGPT"])
openai = Assistant()
wechatapi = WeChatAPI()
wechatpayapi = WeChatPay(
    wechatpay_type=WeChatPayType.NATIVE,
    mchid=settings.MCHID,
    private_key=settings.PRIVATE_KEY,
    cert_serial_no=settings.CERT_SERIAL_NO,
    apiv3_key=settings.APIV3_KEY,
    appid=settings.APPID,
    notify_url=settings.NOTIFY_URL,
    cert_dir=settings.CERT_DIR,
    logger=logger,
    partner_mode=settings.PARTNER_MODE,
    proxy=settings.PROXY,
)


@router.on_event("startup")
async def startup_event():
    await openai.init(settings.OPENAI_PROXY)
    await wechatapi.init(settings.WECHAT_APPID, settings.WECHAT_APPSECRET)


@router.get("/chat/create", response_model=str)
async def create_chat(promptid: int | None = None, user: User = Depends(check_user)):
    """创建会话"""
    prompt = await SystemPrompt.get_or_none(id=promptid) if promptid else None
    context = await Context.create(user=user, prompt=prompt)
    return PlainTextResponse(str(context.session_id))


@router.get("/chat/get", response_model=ContextGetPydantic)
async def show_chat(sessionid: UUID4, user: User = Depends(check_user)):
    """返回指定session_id的会话，不存在则返回204"""
    context = await Context.get_or_none(session_id=sessionid, user=user).select_related(
        "prompt"
    )
    if not context:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return context


@router.post("/chat/send")
async def send_chat(
    message: Message,
    request: Request,
    user: User = Depends(check_balance),
):
    """向指定会话发送消息"""
    append_user_msg = {"role": "user", "content": message.content}
    context = await Context.get(session_id=message.sessionid, user=user).select_related(
        "prompt"
    )
    # 如果有prompt，则附加prompt
    if context.prompt:
        prompt_msg = {"role": "system", "content": context.prompt.content}
        to_send = [prompt_msg, *context.content[-6:], append_user_msg]
    else:
        default_prompt = {
            "role": "system",
            "content": "You are ChatGPT, a large language model trained by OpenAI.",
        }
        to_send = [default_prompt, *context.content[-6:], append_user_msg]

    async def wrapped():
        try:
            reply = ""
            async for i in openai.context_chat(settings.OPENAI_KEYS[0], to_send):
                if await request.is_disconnected():
                    return
                reply += i
                yield i
            append_assistant_msg = {"role": "assistant", "content": reply}
            full_context = [*context.content, append_user_msg, append_assistant_msg]
            await context.update_from_dict({"content": full_context})
            await context.save()
            await user.update_from_dict({"balance": user.balance - 1})
            await user.save()
        except Exception as e:
            logger.error(e)
            yield f"<font color='red'>OpenAI服务异常，请重试或上报管理员:</font>\n\n`{e}`"

    return StreamingResponse(wrapped())


@router.get("/chat/all", response_model=List[ContextListPydantic])
async def show_all_chat(user: User = Depends(check_user)):
    """展示当前用户下的会话列表，不存在则返回204"""
    context_all = (
        await Context.filter(user=user)
        .order_by("-id")
        .only("session_id", "summary", "create_time")
    )
    if not context_all:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return context_all


@router.get("/chat/remove")
async def remove_chat(sessionid: UUID4, user: User = Depends(check_user)):
    """移除当前用户下的指定会话"""
    await Context.filter(user=user, session_id=sessionid).delete()


@router.post(
    "/prompt/create",
    # dependencies=[Depends(check_jwt)],
)
async def create_prompt(prompt: PromptCreatePydantic):
    """添加SystemPrompt"""
    await SystemPrompt.create(**prompt.dict())
    return True


@router.get(
    "/prompt/all",
    response_model=List[PromptListPydantic],
    dependencies=[Depends(check_jwt)],
)
async def show_all_prompt():
    """展示所有的SystemPrompt"""
    prompts = await SystemPrompt.all().only("id", "name", "description")
    return [await PromptListPydantic.from_tortoise_orm(prompt) for prompt in prompts]


@router.get("/user/auth", response_class=JSONResponse)
async def wechat_login(code: str, state: Optional[str] = None):
    # 根据code获取用户信息和openid
    access_meta = await wechatapi.get_access_token(code)
    access_token = access_meta["access_token"]
    openid = access_meta["openid"]
    user = await User.get_or_none(openid=openid)
    # 不存在用户则创建
    userinfo = await wechatapi.get_user_info(access_token, openid)
    if not user:
        user = await User.create(
            openid=userinfo["openid"],
            username=userinfo["nickname"],
            avatar=userinfo["headimgurl"],
            balance=10,
        )
    else:
        await user.update_from_dict(
            {"avatar": userinfo["headimgurl"], "username": userinfo["nickname"]}
        ).save()
        user = await User.get_or_none(openid=openid)
    jwt = create_jwt({"openid": user.openid})
    return {"token": jwt, "username": user.username, "avatar": user.avatar}


@router.get("/user/info")
async def userinfo(user: User = Depends(check_user)):
    # 根据code获取用户信息和openid
    return user


orders = {}


@router.get("/pay/jsapi")
def pay_jsapi(premiumId: int, user: User = Depends(check_user)):
    # 以jsapi下单为例，下单成功后，将prepay_id和其他必须的参数组合传递给JSSDK的wx.chooseWXPay接口唤起支付
    out_trade_no = "".join(sample(ascii_letters + digits, 8))
    description = "会员购买"
    match (premiumId):
        case 0:
            amount = 1000
        case 1:
            amount = 3000
    payer = {"openid": user.openid}
    code, message = wechatpayapi.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={"total": amount},
        pay_type=WeChatPayType.JSAPI,
        payer=payer,
    )
    result = json.loads(message)
    if code in range(200, 300):
        prepay_id = result.get("prepay_id")
        timestamp = str(int(time.time() * 1000))
        noncestr = secrets.token_hex(8)
        package = "prepay_id=" + prepay_id
        paysign = wechatpayapi.sign([settings.APPID, timestamp, noncestr, package])
        signtype = "RSA"
        orders[out_trade_no] = {"premium_id": premiumId, "user": user}
        return {
            "code": 0,
            "result": {
                "appId": settings.APPID,
                "timeStamp": timestamp,
                "nonceStr": noncestr,
                "package": "prepay_id=%s" % prepay_id,
                "signType": signtype,
                "paySign": paysign,
            },
        }
    else:
        return {"code": -1, "result": {"reason": result}}


@router.post("/pay/notify")
async def notify(request: Request):
    headers = request.headers
    body = await request.body()
    result = wechatpayapi.callback(headers, body)
    # 支付成功
    if result and result.get("event_type") == "TRANSACTION.SUCCESS":
        resp = result.get("resource")
        appid = resp.get("appid")
        mchid = resp.get("mchid")
        out_trade_no = resp.get("out_trade_no")
        transaction_id = resp.get("transaction_id")
        trade_type = resp.get("trade_type")
        trade_state = resp.get("trade_state")
        trade_state_desc = resp.get("trade_state_desc")
        bank_type = resp.get("bank_type")
        attach = resp.get("attach")
        success_time = resp.get("success_time")
        payer = resp.get("payer")
        amount = resp.get("amount").get("total")
        # TODO: 根据返回参数进行必要的业务处理，处理完后返回200或204
        order = orders.pop(out_trade_no, None)
        if order:
            user: User = order["user"]
            logger.info(f"用户{user.username}支付成功，订单号{out_trade_no}")
            match (order["premium_id"]):
                case 0:
                    # 体验会员
                    chat_times = 100
                case 1:
                    # 初级会员
                    chat_times = 500
            await user.update_from_dict({"balance": user.balance + chat_times}).save()
        return {"code": "SUCCESS", "message": "成功"}
    else:
        logger.error("支付失败")
        return {"code": "FAILED", "message": "失败"}, 500

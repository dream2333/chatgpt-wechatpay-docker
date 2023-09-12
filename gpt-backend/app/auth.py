from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError
from app.models import User
from settings import JWT_SECRET


token_auth_scheme = HTTPBearer()


def create_jwt(data: dict, expires_delta=timedelta(hours=8)):
    """
    :param data: 需要进行JWT令牌加密的数据
    :param expires_delta: 令牌有效期
    :return: token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    # 添加失效时间
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt


async def check_jwt(token=Depends(token_auth_scheme)):
    """
    验证token
    :param token:
    :return: 返回openid
    """
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms="HS256")
        openid: str = payload.get("openid")
        return openid
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": 5001,
                "message": "登录状态过期",
            },
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": 5000,
                "message": "身份令牌错误",
            },
        )


async def check_user(openid=Depends(check_jwt)):
    return await User.get_or_none(openid=openid)


async def check_balance(user: User = Depends(check_user)):
    if user.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": 5002,
                "message": "您的对话余额不足,请到用户页充值",
            },
        )
    else:
        return user

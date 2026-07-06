"""Pydantic v2 Schema —— 请求/响应数据校验与序列化"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ============ 用户 ============

class UserCreate(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, examples=["zhangsan"])
    email: str = Field(..., min_length=5, max_length=120, examples=["zhangsan@example.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["mypassword123"])


class UserLogin(BaseModel):
    """登录请求"""
    username: str = Field(..., examples=["zhangsan"])
    password: str = Field(..., examples=["mypassword123"])


class UserResponse(BaseModel):
    """用户信息响应（不含密码）"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ 文章 ============

class ItemCreate(BaseModel):
    """创建文章"""
    title: str = Field(..., min_length=1, max_length=200, examples=["我的第一篇博客"])
    content: str = Field(default="", max_length=10000, examples=["这是文章正文内容..."])


class ItemUpdate(BaseModel):
    """更新文章（所有字段可选）"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, max_length=10000)


class ItemResponse(BaseModel):
    """文章响应"""
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    """文章列表响应"""
    items: List[ItemResponse]
    total: int

"""文章路由 —— CRUD 操作，全部需要 JWT 认证"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, Item
from schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from auth import get_current_user

router = APIRouter(prefix="/api/v1/items", tags=["文章"])


@router.get("", response_model=ItemListResponse)
async def list_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文章列表 —— 只返回当前用户的文章"""
    # 查询总数
    count_result = await db.execute(
        select(func.count()).select_from(Item).where(Item.author_id == current_user.id)
    )
    total = count_result.scalar() or 0

    # 查询列表
    result = await db.execute(
        select(Item)
        .where(Item.author_id == current_user.id)
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()

    return ItemListResponse(
        items=[ItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建文章"""
    item = Item(title=data.title, content=data.content, author_id=current_user.id)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return ItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单篇文章"""
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.author_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return ItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新文章"""
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.author_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    # 只更新提供的字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.flush()
    await db.refresh(item)
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除文章"""
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.author_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

    await db.delete(item)

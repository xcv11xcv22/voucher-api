import enum
from datetime import datetime, date, timezone

from sqlalchemy import (
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from db import Base
from enums import IntEnumType
def utcnow():
    return datetime.now(timezone.utc)
class VoucherStatus(enum.IntEnum):
    UNUSED = 0   # 未使用
    USED = 1       # 已使用
    EXPIRED = 2 # 過期

STATUS_MAP = {
    "unused": VoucherStatus.UNUSED,
    "used": VoucherStatus.USED,
    "expired": VoucherStatus.EXPIRED,
}

class Voucher(Base):
    __tablename__ = "vouchers"
    __table_args__ = (
        UniqueConstraint("code", name="uq_voucher_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(String(32), nullable=False)   # 優惠券唯一編碼
    name: Mapped[str] = mapped_column(String(128), nullable=False)  # 優惠券名稱
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # 價格
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[VoucherStatus] = mapped_column(
        IntEnumType(VoucherStatus),  # IntEnumType 自定義轉換
        nullable=False,
        default=VoucherStatus.UNUSED,
    )

    # 新增的欄位 建立時間
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utcnow,
    )
    # 新增的欄位 更新時間
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


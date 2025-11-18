from sqlalchemy import select
from models import Voucher, VoucherStatus, STATUS_MAP

class VoucherRepository:
    def __init__(self, session):
        self.session = session

    def list(self, **filters):
        stmt = select(Voucher)
        stmt = self.apply_filters(stmt, **filters)
        return self.session.scalars(stmt).all()
    
    def filter(self, **filters):
        stmt = select(Voucher)
        stmt = self.apply_filters(stmt, **filters)
        return self.session.scalars(stmt).first()

    def get(self, voucher_id: int) -> Voucher | None:
        return self.session.get(Voucher, voucher_id)

    def add(self, voucher: Voucher):
        self.session.add(voucher)

    def delete(self, voucher: Voucher):
        self.session.delete(voucher)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

    def refresh(self, voucher: Voucher):
        self.session.refresh(voucher)

    def apply_filters(self, stmt, **filters):
        """
        根據過濾條件動態組合 SQLAlchemy Select 查詢
        Args:
            stmt (select): SQLAlchemy select(Voucher) 查詢物件。
            filters(dict): 從 VoucherFilterSchema 驗證後取得的篩選條件 dict
        Returns:
            select(Voucher):經過加上 where 條件後的 SQLAlchemy Select 查詢物件

        """
        if id := filters.get("id"):
            stmt = stmt.where(Voucher.id == id)

        if code := filters.get("code"):
            stmt = stmt.where(Voucher.code == code)

        if name := filters.get("name"):
            stmt = stmt.where(Voucher.name.ilike(f"%{name}%"))

        if status := filters.get("status"):
            t = VoucherStatus(STATUS_MAP[status])
            stmt = stmt.where(Voucher.status == t)
        
        if filters.get("is_active") is not None:
            stmt = stmt.where(Voucher.is_active == filters["is_active"])

        return stmt

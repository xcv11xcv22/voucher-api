from apiflask import APIBlueprint, abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from db import SessionLocal
from models import Voucher, VoucherStatus, STATUS_MAP
from schemas import VoucherCreateSchema, VoucherOutSchema, VoucherUpdateSchema, VoucherFilterSchema
from datetime import datetime
import redis

bp = APIBlueprint('vouchers', __name__, url_prefix='/vouchers')
redis_client = redis.Redis(host="localhost", port=6378, db=0)

QUEUE_KEY = "voucher_jobs"
def apply_filters(stmt, **filters):
    """
    根據過濾條件動態組合 SQLAlchemy Select 查詢
    Args:
        stmt (select): SQLAlchemy select(Voucher) 查詢物件。
        filters(dict): 從 VoucherFilterSchema 驗證後取得的篩選條件 dict
    Returns:
        select(Voucher):經過加上 where 條件後的 SQLAlchemy Select 查詢物件

    """
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


@bp.post('/')
@bp.input(VoucherCreateSchema)
@bp.output(VoucherOutSchema, status_code=201)
def create_voucher(json_data):
    """
    建立一張新的優惠券

    Args:
        json_data (dict):  VoucherCreateSchema 驗證的新增參數

    Returns:
        Voucher:以VoucherOutSchema 序列化後回傳的優惠券物件
    Raises:
        400 Bad Request: 優惠券已存在
    """
    session = SessionLocal()
    try:
        voucher = Voucher(
            code=json_data['code'],
            name=json_data['name'],
            price=json_data['price'],
            discount_percent=json_data['discount_percent'],
            valid_from=json_data.get('valid_from'),
            valid_to=json_data.get('valid_to'),
            is_active=json_data.get('is_active', True),
            status=VoucherStatus(json_data.get('status', 0)),
        )
        session.add(voucher)
        session.commit()
        session.refresh(voucher)
        return voucher
    except IntegrityError:
        session.rollback()
        abort(400, message='Voucher code already exists')
    finally:
        session.close()


@bp.get('/')
@bp.input(VoucherFilterSchema, location="query")
@bp.output(VoucherOutSchema(many=True))
def list_vouchers(query_data):
    """
    列出所有優惠券, 透過查詢參數進行篩選

    Args:
        query_data (dict):  VoucherFilterSchema 驗證的查詢參數

    Returns:
        list[Voucher]: 由VoucherOutSchema(many=True) 序列化為列表輸出
    """
    session = SessionLocal()
    try:
        stmt = select(Voucher)
        stmt = apply_filters(stmt, **query_data)
        vouchers = session.scalars(stmt).all()
        return vouchers
    finally:
        session.close()

@bp.get('/<int:voucher_id>')
@bp.output(VoucherOutSchema)
def get_voucher(voucher_id):
    """
    取得指定 ID 的優惠券
    Args:
        voucher_id (int): 優惠券 ID

    Returns:
        Voucher: VoucherOutSchema 定義的輸出格式

    Raises:
        404 Bad Request: 優惠券不存在
    """
    session = SessionLocal()
    try:
        voucher = session.get(Voucher, voucher_id)
        if not voucher:
            abort(404, message='Voucher not found')
        return voucher
    finally:
        session.close()

@bp.patch('/<int:voucher_id>')
@bp.input(VoucherUpdateSchema(partial=True))
@bp.output(VoucherOutSchema)
def update_voucher(voucher_id, json_data):
    """
    更新優惠券

    Args:
        voucher_id (int): 優惠券 ID。
        json_data(dict):已通過 VoucherUpdateSchema 更新的參數

    Returns:
        Voucher: VoucherOutSchema 定義的輸出格式。

    Raises:
        HTTP 404: 若優惠券不存在。
    """
    session = SessionLocal()
    try:
        voucher = session.get(Voucher, voucher_id)
        if not voucher:
            abort(404, message='Voucher not found')

        # 逐欄位更新
        for key, value in json_data.items():
            if key == 'status':
                value = VoucherStatus(value)
            setattr(voucher, key, value)
        voucher.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(voucher)
        return voucher
    finally:
        session.close()


@bp.delete('/')
@bp.input(VoucherFilterSchema)
def delete_voucher(json):
    """
    刪除優惠券

    Args:
        json(dict):已通過 VoucherFilterSchema 遇刪除的參數

    Returns:
        dict: 刪除成功訊息，{"message": "Voucher id, code deleted"}。

    Raises:
        HTTP 404: 優惠券不存在。
    """
    session = SessionLocal()
    try:
        stmt = select(Voucher)
        stmt = apply_filters(stmt, **json)
        voucher = session.scalars(stmt).first()

        if not voucher:
            abort(404, message='Voucher not found')

        session.delete(voucher)
        session.commit()
        return {'message': f'Voucher id:{voucher.id},code:{voucher.code} deleted'}
    finally:
        session.close()


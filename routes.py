from apiflask import APIBlueprint, abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from flask import current_app
from models import Voucher, VoucherStatus, STATUS_MAP
from schemas import VoucherCreateSchema, VoucherOutSchema, VoucherUpdateSchema, VoucherFilterSchema
from datetime import datetime, timezone
import redis
import uuid
import json
from voucher_repository import VoucherRepository
import os
bp = APIBlueprint('vouchers', __name__, url_prefix='/vouchers')
host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_PORT", 6378))
redis_client = redis.Redis(host=host, port=port, db=0)

QUEUE_KEY = "voucher_jobs"

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
    repo = VoucherRepository(current_app.session_local())
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
        repo.add(voucher)
        repo.commit()
        repo.refresh(voucher)
        return voucher
    except IntegrityError as e:
        print(str(e.orig))
        repo.rollback()
        abort(400, message='Voucher code already exists')
    finally:
        repo.close()


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
    repo = VoucherRepository(current_app.session_local())
    try:
        vouchers = repo.list(**query_data)
        return vouchers
    finally:
        repo.close()

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
    repo = VoucherRepository(current_app.session_local())
    try:
        voucher = repo.get(voucher_id)
        if not voucher:
            abort(404, message='Voucher not found')
        return voucher
    finally:
        repo.close()

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
    repo = VoucherRepository(current_app.session_local())
    try:
        voucher = repo.get(voucher_id)
        if not voucher:
            abort(404, message='Voucher not found')

        # 逐欄位更新
        for key, value in json_data.items():
            if key == 'status':
                value = VoucherStatus(value)
            setattr(voucher, key, value)
        repo.commit()
        repo.refresh(voucher)
        return voucher
    finally:
        repo.close()


@bp.delete('/')
@bp.input(VoucherFilterSchema)
def delete_voucher(json_data):
    """
    刪除優惠券

    Args:
        json_data(dict):已通過 VoucherFilterSchema 遇刪除的參數

    Returns:
        dict: 刪除成功訊息，{"message": "Voucher id, code deleted"}。

    Raises:
        HTTP 404: 優惠券不存在。
    """
    
    repo = VoucherRepository(current_app.session_local())
    try:
        voucher = repo.filter(**json_data)
        if not voucher:
            abort(404, message='Voucher not found')

        repo.delete(voucher)
        repo.commit()
        return {'message': f'Voucher id:{voucher.id},code:{voucher.code} deleted'}
    finally:
        repo.close()

@bp.post("/bulk")
@bp.input(VoucherCreateSchema(many=True), arg_name="vouchers_data")
def bulk_create_vouchers(vouchers_data):
    """
    一次大量建立多筆優惠券

    Args:
        vouchers_data(dict): VoucherCreateSchema(many=True)驗證的 新增的參數(List)

    Returns:
        dict: job資訊
        return {
            "job_ids": job_ids, 
            "queued": total,         
            "message": "Jobs accepted and queued",
        }

    """
    batch_size = 5000
    job_ids = []
    total = len(vouchers_data)

    for start in range(0, total, batch_size):
        end = start + batch_size
        batch = vouchers_data[start:end]

        job_id = str(uuid.uuid4())
        job_ids.append(job_id)

        job = {
            "job_id": job_id,
            "vouchers": batch,
        }

        redis_client.rpush(QUEUE_KEY, json.dumps(job, ensure_ascii=False))

    return {
        "job_ids": job_ids, 
        "queued": total,         
        "message": "Jobs accepted and queued",
    }
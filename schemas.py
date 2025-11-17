# schemas.py
from apiflask import Schema
from marshmallow import fields, validate


class VoucherBaseSchema(Schema):

    code = fields.String(
        required=True,
        validate=validate.Length(max=32),
        metadata={"description": "優惠券唯一編碼"},
    )
    name = fields.String(
        required=True,
        validate=validate.Length(max=128),
        metadata={"description": "優惠券名稱"},
    )
    price = fields.Integer(
        required=True,
        as_string=True,
        metadata={"description": "原價"},
    )
    discount_percent = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=100),
        metadata={"description": "折扣百分比 0~100"},
    )
    valid_from = fields.Date(load_default=None)
    valid_to = fields.Date(load_default=None)
    is_active = fields.Boolean(load_default=True)
    status = fields.Integer(
        load_default=0,
        validate=validate.OneOf([0, 1, 2])
    )


# 建立用
class VoucherCreateSchema(VoucherBaseSchema):
    pass

# 更新用
class VoucherUpdateSchema(VoucherBaseSchema):
    pass

# 回傳給前端用
class VoucherOutSchema(VoucherBaseSchema):
    id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class VoucherFilterSchema(Schema):
    code = fields.String()
    name = fields.String()
    status = fields.String(validate=validate.OneOf(["unused", "used", "expired"]))
    is_active = fields.Boolean()

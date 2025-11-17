from sqlalchemy.types import TypeDecorator, Integer

class IntEnumType(TypeDecorator):
    impl = Integer
    cache_ok = True   # SQLAlchemy 2.x 需要這個，不然會有警告

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        # 寫入 DB 前：Enum -> int
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return int(value.value)
        # 如果你不小心給了 int，也接受
        return int(value)

    def process_result_value(self, value, dialect):
        # 從 DB 讀出：int -> Enum
        if value is None:
            return None
        return self.enum_class(value)

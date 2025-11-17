from apiflask import APIFlask

from db import Base, engine
import models  
from routes import bp as voucher_bp


app = APIFlask(__name__)

# 建立資料表
Base.metadata.create_all(bind=engine)

# 註冊 voucher API
app.register_blueprint(voucher_bp)


@app.get("/ping")
def ping():
    return {"message": "pong"}


def create_app(test_config=None):
    app = APIFlask(__name__)

    if test_config is None:
        # 正常模式：用原本的 vouchers.db
        Base.metadata.create_all(bind=engine)
    else:
        # 測試模式：用外部傳進來的 engine
        test_engine = test_config["engine"]
        Base.metadata.create_all(bind=test_engine)

    app.register_blueprint(voucher_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
from apiflask import APIFlask

from db import Base
import models  
from routes import bp as voucher_bp
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
app = APIFlask(__name__)


# 註冊 voucher API
app.register_blueprint(voucher_bp)


@app.get("/ping")
def ping():
    return {"message": "pong"}


def create_app(test_config=None):
    app = APIFlask(__name__)
  
    if test_config is not None and "engine" in test_config:
        engine = test_config["engine"]
    else:
        engine = create_engine("sqlite:///vouchers.db", future=True)
    app.engine = engine
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    app.session_local = SessionLocal
 
    app.register_blueprint(voucher_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
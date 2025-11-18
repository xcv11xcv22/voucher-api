from apiflask import APIFlask
import os
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
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATA_DIR = os.path.join(BASE_DIR, "data")
        os.makedirs(DATA_DIR, exist_ok=True) 
        db_path = os.path.join(DATA_DIR, "vouchers.db")
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL, future=True)
        Base.metadata.create_all(bind=engine)
    app.engine = engine
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    app.session_local = SessionLocal
 
    app.register_blueprint(voucher_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
import json
import redis
from sqlalchemy.exc import IntegrityError
import os
from models import Voucher, VoucherStatus

QUEUE_KEY = "voucher_jobs"
host = os.getenv("REDIS_HOST", "localhost")
port = int(os.getenv("REDIS_PORT", 6378))
redis_client = redis.Redis(host=host, port=port, db=0)

def process_job(job: dict):
    """
    job 裡的 vouchers 寫入資料庫
    job 結構：
    {
        "job_id": "...",
        "vouchers": [ { ... }, { ... }, ... ]
    }
    """
    vouchers_data = job["vouchers"]

    session = SessionLocal()
    try:
        vouchers = []
        for data in vouchers_data:
            vouchers.append(
                Voucher(
                    code=data["code"],
                    name=data["name"],
                    price=data["price"],
                    discount_percent=data["discount_percent"],
                    valid_from=data.get("valid_from"),
                    valid_to=data.get("valid_to"),
                    is_active=data.get("is_active", True),
                    status=VoucherStatus(data.get("status", "unused")),
                )
            )
        session.add_all(vouchers)
        session.commit()
        print(f"[OK] job {job['job_id']} inserted {len(vouchers)} vouchers")

    except IntegrityError as e:
        session.rollback()
        print(f"FAIL job {job['job_id']} IntegrityError: {e}")

    except Exception as e:
        session.rollback()
        print(f"FAIL job {job['job_id']} unexpected error: {e}")

    finally:
        session.close()


def main():
    print("Worker started, waiting for jobs ...")
    while True:
        # BLPOP 會阻塞等待，右邊的 0 代表一直等
        _, raw = redis_client.blpop(QUEUE_KEY, timeout=0)
        # raw 是 bytes，要轉成字串再轉 json
        job = json.loads(raw.decode("utf-8"))
        process_job(job)


if __name__ == "__main__":
    main()

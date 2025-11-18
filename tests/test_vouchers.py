from work import process_job
from models import Voucher 
import uuid
def test_create_and_get_voucher(client):
    client, app = client 
    # 建立
    payload = {
        "code": "T100",
        "name": "Test Voucher",
        "price": 500,
        "discount_percent": 10
    }
    resp = client.post("/vouchers/", json=payload)
    assert resp.status_code == 201

    data = resp.get_json()
    voucher_id = data["id"]

    # 查詢
    resp2 = client.get(f"/vouchers/{voucher_id}")
    assert resp2.status_code == 200
    data2 = resp2.get_json()

    assert data2["code"] == "T100"
    assert data2["name"] == "Test Voucher"


def test_update_voucher(client):
    client, app = client 
    # 建立
    payload = {
        "code": "T200",
        "name": "Before Update",
        "price": 1000,
        "discount_percent": 5
    }
    resp = client.post("/vouchers/", json=payload)
    voucher_id = resp.get_json()["id"]

    # 更新
    resp2 = client.patch(f"/vouchers/{voucher_id}", json={"name": "After Update"})
    assert resp2.status_code == 200

    # 查詢驗證
    resp3 = client.get(f"/vouchers/{voucher_id}")
    assert resp3.get_json()["name"] == "After Update"


def test_delete_voucher(client):
    client, app = client 
    # 建立
    payload = {
        "code": "T300",
        "name": "Will Delete",
        "price": 900,
        "discount_percent": 15
    }
    resp = client.post("/vouchers/", json=payload)
    voucher_id = resp.get_json()["id"]

    # 刪除
    resp2 = client.delete("/vouchers/",
                            json={"id": voucher_id})
    assert resp2.status_code == 200

    # 再查應該 404
    resp3 = client.get(f"/vouchers/{voucher_id}")
    assert resp3.status_code == 404


def test_query_filter(client):
    client, app = client 
    # 建立兩筆
    resp1 = client.post("/vouchers/", json={
        "code": "A1",
        "name": "Alpha",
        "price": 100,
        "discount_percent": 10
    })
    assert resp1.status_code == 201
    client.post("/vouchers/", json={
        "code": "B1",
        "name": "Beta",
        "price": 200,
        "discount_percent": 20
    })

    # 篩選
    resp = client.get("/vouchers/",
                      query_string={"code": "B1"})
    data = resp.get_json()

    assert len(data) == 1
    assert data[0]["code"] == "B1"


def test_bulk_create(client):
    client, app = client 
    job_ids = []
    job_id = str(uuid.uuid4())
    job_ids.append(job_id)
   
    job = {
        'job_id': job_id,
        'vouchers':[
        {
            "code": "BULK_A",
            "name": "Bulk A",
            "price": 100,
            "discount_percent": 1
        },
        {
            "code": "BULK_B",
            "name": "Bulk B",
            "price": 200,
            "discount_percent": 2
        }
    ]
    }

    resp = client.post("/vouchers/bulk", json=job['vouchers'])
    with app.app_context():
        process_job(job)
    assert resp.status_code == 200

    result = resp.get_json()
    assert "job_ids" in result
    SessionLocal = app.session_local
    with app.app_context():
        with SessionLocal() as session:
            rows = session.query(Voucher).all()
            assert len(rows) == len(job['vouchers'])


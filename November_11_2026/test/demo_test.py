from fastapi import FastAPI

from fastapi.testclient import TestClient

demo_app = FastAPI()

@demo_app.get("/")
def demo_home():
    return {"message": "all good"}


client = TestClient(demo_app)

def test_message():
    response = client.get("/")
    assert response.status_code == 200


#  uv run pytest .\November_11_2026\test\demo_test.py -v
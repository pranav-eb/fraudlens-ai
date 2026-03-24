from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/test")
async def test_upload(file: UploadFile = File(...)):
    return {"size": len(await file.read())}

client = TestClient(app)

try:
    response = client.post("/test", files={"file": ("test.csv", b"a,b\n1,2")})
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    import traceback
    traceback.print_exc()

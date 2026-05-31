from fastapi import FastAPI
from routers import predict

app = FastAPI(title="Harry Potter API Gateway")
app.include_router(predict.router)

@app.get("/health")
def health():
    return {"status": "ok"}
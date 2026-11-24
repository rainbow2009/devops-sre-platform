from fastapi import FastAPI

app = FastAPI(
    title="DevOps SRE Platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "service": "payment-api",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}

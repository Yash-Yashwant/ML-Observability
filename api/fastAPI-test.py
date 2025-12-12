from fastapi import FastAPI

app = FastAPI()

@app.get("/")

async def root():
    return {"information": "This is a demo"}
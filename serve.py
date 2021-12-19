from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return "I am a teapot"

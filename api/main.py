from fastapi import FastAPI
from auth.endpoints import router as router_auth

app = FastAPI(
    title="Passwords Manager App"
)

app.include_router(router_auth, tags=["Auth"], prefix="/auth")


@app.get("/")
async def start_page():
    return "Welcome to ManagerPassword! Go to link /docs"

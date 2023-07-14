from fastapi import FastAPI
from auth.endpoints import router as router_auth
from crypt_password.endpoints import router as router_crypt

# TODO: добавить логирование gunicorn

app = FastAPI(
    title="Passwords Manager App"
)


@app.get("/")
async def start_page():
    return "Welcome to ManagerPassword! Go to link /docs"

app.include_router(router_auth, tags=["Auth"], prefix="/auth")
app.include_router(router_crypt, tags=["Crypt Password"], prefix="/crypt")

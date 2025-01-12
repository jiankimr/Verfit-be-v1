from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from generation import generation
from workbook import workbook
from accounts import routers as accounts
from mypage import routers as mypage
from home import routers as home
from share import routers as share
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from database import db

app = FastAPI(
    title="My API",
    description="API description",
    version="0.1.0",
    docs_url="/docs",
)

app.db = db
# 정식 배포전 변경, 분리 예정
app.add_middleware(SessionMiddleware, secret_key="f65db23bc05cf219709a76078fead95507d023cc2ef0d278ff09a180c92100d9")

# CORS 설정
origins = [
    "http://localhost:5173",  # Frontend 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router)
app.include_router(workbook.router)
app.include_router(accounts.router)
app.include_router(mypage.router)
app.include_router(home.router)
app.include_router(share.router)


@app.get("/healthcheck")
async def health_check():
    return {"message": "200 OK"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

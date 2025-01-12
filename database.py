#from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient


# MongoDB 서버 설정
MONGO_SERVER = "mongodb://localhost:27017"

# MongoDB 클라이언트 생성
#client = MongoClient(MONGO_SERVER)
client = AsyncIOMotorClient(MONGO_SERVER)

# MongoDB 데이터베이스 선택
db = client.Verfit

# User 컬렉션에 대한 고유 인덱스 생성
db.users.create_index("useremail", unique=True)

# Admin 컬렉션에 대한 고유 인덱스 생성
db.admins.create_index("adminemail", unique=True)

db.token_blacklist.create_index("jti", unique=True)


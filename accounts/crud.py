from .schemas import User, Admin
from .dependencies import get_password_hash
from database import db
from datetime import datetime


async def create_user(user: User):
    user_dict = user.dict()
    user_dict['userpassword'] = get_password_hash(user_dict['userpassword'])  # Assumes this function is defined
    await db["users"].insert_one(user_dict)
    return user


async def get_user_by_email(email: str):
    return await db["users"].find_one({"useremail": email})


async def delete_user(email: str):
    await db["users"].delete_one({"useremail": email})


async def create_admin(admin: Admin):
    admin_dict = admin.dict()
    admin_dict['adminpassword'] = get_password_hash(admin_dict['adminpassword'])  # Assumes this function is defined
    await db["admins"].insert_one(admin_dict)
    return admin


async def get_admin_by_email(email: str):
    return await db["admins"].find_one({"adminemail": email})


async def delete_admin(email: str):
    await db["admins"].delete_one({"adminemail": email})


async def logout_user(db, token_jti: str, token_exp: datetime):
    await db["token_blacklist"].insert_one({"jti": token_jti, "exp": token_exp})


async def is_token_blacklisted(db, token_jti: str):
    blacklisted_token = await db["token_blacklist"].find_one({"jti": token_jti})
    return blacklisted_token is not None

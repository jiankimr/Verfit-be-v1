from .schemas import UserInfo, UserUpdate, AbilityTestResult, AbilityTestAnswers,MyPageResponse
from database import db
from accounts.crud import get_password_hash
from accounts.dependencies import get_current_user

async def get_user_info(useremail: str):
    user= await db["users"].find_one({"useremail": useremail})
    user_info= UserInfo(user)
    user_info.get_myWorkbooks()
    user_info.get_favWorkbooks()
    return user_info

async def update_user_info(useremail: str, user_update: UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    await db["users"].update_one({"useremail": useremail}, {"$set": update_data})
    return await get_user_info(useremail)

async def perform_ability_test(useremail: str, test_answers: AbilityTestAnswers):
    test_result = {category: sum(scores) for category, scores in test_answers}
    await db["users"].update_one({"useremail": useremail}, {"$set": {"ability_score": test_result}})
    return test_result


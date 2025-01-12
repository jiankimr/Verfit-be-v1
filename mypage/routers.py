# routers.py
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from accounts.schemas import UserInDB
from .crud import update_user_info, perform_ability_test
from .schemas import MyPageResponse, AbilityTestAnswers, UserUpdate
from accounts.dependencies import get_current_user, get_token_from_session
from .abilityTest import questions
from fastapi.security import OAuth2PasswordBearer
from workbook import database


router = APIRouter(prefix="/mypage")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("", tags=['mypage'])
def get_my_page(current_user: UserInDB = Depends(get_current_user)):
    workbooks = database.get_workbooks()

    made_workbooks = [wb for wb in workbooks if wb["workbook_id"] in current_user["made_workbook_id"]]

    made_workbooks_without_id = [
        {key: value for key, value in wb.items() if key != '_id'}
        for wb in made_workbooks
    ]

    workbooks = database.get_workbooks()

    fav_workbooks = [wb for wb in workbooks if wb["workbook_id"] in current_user["fav_workbook_id"]]

    fav_workbooks_without_id = [
        {key: value for key, value in wb.items() if key != '_id'}
        for wb in fav_workbooks
    ]

    return {
        "nickname": current_user["username"],
        "email": current_user["useremail"],
        "ability_score": current_user["ability_score"],
        "made_workbooks": made_workbooks_without_id,
        "fav_workbooks": fav_workbooks_without_id,
    }


#update user-info
@router.put("/profile", response_model=MyPageResponse)
async def update_profile(user_update: UserUpdate, request: Request):
    token = await get_token_from_session(request)
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = await get_current_user(token)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    updated_user_info = await update_user_info(user['useremail'], user_update)
    return MyPageResponse(
        nickname=updated_user_info.user['username'],
        useremail=updated_user_info.user['useremail'],
        ability_score=updated_user_info.user['ability_score'],
        myWorkbooks=updated_user_info.myWorkbooks,
        favWorkbooks=updated_user_info.favWorkbooks
    )


@router.post("/ability-test/submit", tags=['mypage'])  # response_model=AbilityTestResult
async def ability_test_submit( test_answer: AbilityTestAnswers, current_user: UserInDB = Depends(get_current_user)):
    test_result = await perform_ability_test(current_user['useremail'], test_answer)
    return test_result  # AbilityTestResult(test_result)


@router.get("/ability_test")
async def get_ability_test():
    return questions

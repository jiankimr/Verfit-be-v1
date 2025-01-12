from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
import workbook.database as database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from accounts.schemas import Token, User, UserInDB
from accounts.dependencies import oauth2_scheme, get_current_user, get_token_from_session
from workbook.models import Workbook
from dotenv import load_dotenv
from typing import Optional
from fastapi import Depends, FastAPI



load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/share",
)

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_token_from_session(token)
    if not user:
        return None
    return user

# 사용자의 워크북만 가져오기
@router.get("", tags=['share'])
def get_workbooks(limit: int, current_user: UserInDB = Depends(get_current_user)):
    workbooks = database.get_workbooks(limit)
    if workbooks:
        response = {"workbooks": workbooks}
        if current_user:
            response["usernmae"] = current_user.nickname
        return response
    else:
        return {"message": "Workbook not found"}
    
# 사용자의 워크북에서 문제집 검색
@router.get("/search", tags=['share'])
def search_workbooks(search: str):
    workbooks = database.search_workbooks(search)
    if workbooks:
        return workbooks
    else:
        return {"message": "Workbook not found"}

    
@router.get("/search/{params}", tags=['share'])
def filter_workbooks(Subject: Optional[str] = None, Type: Optional[int] = None, Date: Optional[str] = None):
    workbooks = database.filter_workbooks(Subject, Type, Date)
    if workbooks:
        return workbooks
    else:
        return {"message": "Workbook not found"}
    




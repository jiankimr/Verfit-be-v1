# schemas.py
from pydantic import BaseModel, Field, conint,EmailStr
from typing import List, Optional, Dict, Tuple
from workbook.models import Workbook
from workbook.database import get_workbook
from accounts.schemas import User

class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]

class AbilityTestAnswers(BaseModel):
    # Example: {"인식능력": [1, 2, 3], "학습전략": [2, 3, 1], ...}
    인식능력: Tuple[conint(ge=1, le=5), conint(ge=1, le=5), conint(ge=1, le=5)]
    학습전략: Tuple[conint(ge=1, le=5), conint(ge=1, le=5), conint(ge=1, le=5)]
    학습활동: Tuple[conint(ge=1, le=5), conint(ge=1, le=5), conint(ge=1, le=5)]
    자기평가: Tuple[conint(ge=1, le=5), conint(ge=1, le=5), conint(ge=1, le=5)]
    의사소통과_협력: Tuple[conint(ge=1, le=5), conint(ge=1, le=5), conint(ge=1, le=5)]

class AbilityTestResult(BaseModel):
    # Example: {"인식능력": 10, "학습전략": 4, ..., "total": 35}
    scores: Dict[str, int]

class UserInfo():   
    def __init__(self, user: User):
        self.user = user  # User 객체의 인스턴스 저장
        self.myWorkbooks: List[Workbook]=[]
        self.favWorkbooks: List[Workbook]=[]
    
    def get_myWorkbooks(self):
        try:
            for i in  self.user.made_workbook_id:
                self.myWorkbooks.append(get_workbook(i))
        except:
            self.myWorkbooks=[]

    def get_favWorkbooks(self):
        try:
            for i in  self.user.fav_workbook_id:
                self.favWorkbooks.append(get_workbook(i))
        except:
            self.favWorkbooks=[]

class MyPageResponse(BaseModel):
    nickname: str =Field(...,description="username")
    useremail: EmailStr =Field(...,description="고유 email")
    ability_score: Dict[str, int]= Field(description="인식능력, 학습전략, 학습활동, 평가, 의사소통과 협력, 총점")
    myWorkbooks: List[Workbook] =Field(default="[]",description="내가 만든 문제집")
    favWorkbooks: List[Workbook] =Field(default="[]",description="즐겨찾기한 문제집")
    """
    def __init__(self, userinfo: UserInfo):
        self.nickname: userinfo.user['username']
        self.useremail: userinfo.user['useremail']
        self.ability_score: userinfo.user['ability_score']
        self.myWorkbooks: userinfo.myWorkbooks
        self.favWorkbooks: userinfo.favWorkbooks
"""
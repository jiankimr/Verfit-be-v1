from fastapi import APIRouter
from dotenv import load_dotenv
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from workbook import database

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/home",
)


@router.get("", tags=['home'])
def get_workbooks(
    type: Optional[str] = None,
    keyword: Optional[str] = None,
):
    workbooks = database.get_workbooks()
    workbooks = [wb for wb in workbooks if wb["pubpriv"] == 1]
    if type and keyword:
        if type == "제목":
            filtered_workbooks = [wb for wb in workbooks if keyword.lower() in wb["title"].lower()]
        elif type == "과목":
            filtered_workbooks = [wb for wb in workbooks if keyword.lower() in wb["subject"].lower()]
        elif type == "설명":
            filtered_workbooks = [wb for wb in workbooks if keyword.lower() in wb["description"].lower()]
        else:
            filtered_workbooks = \
                [wb for wb in workbooks if (keyword.lower() in wb["title"].lower()) or
                 (keyword.lower() in wb["subject"].lower()) or (keyword.lower() in wb["description"].lower())]

        if filtered_workbooks:
            filtered_workbooks_without_id = [
                {key: value for key, value in wb.items() if key != '_id'}
                for wb in filtered_workbooks
            ]
            return {"workbooks": filtered_workbooks_without_id}
        else:
            return {"workbooks": [], "message": "Matching Workbooks not found", "type": type, "keyword": keyword}
    else:
        if workbooks:
            workbooks_without_id = [
                {key: value for key, value in wb.items() if key != '_id'}
                for wb in workbooks
            ]
            return {"workbooks": workbooks_without_id}
        else:
            return {"workbooks": [], "message": "Workbook not found"}

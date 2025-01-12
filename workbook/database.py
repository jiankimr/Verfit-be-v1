from pymongo import MongoClient
from workbook.models import Workbook  # Workbook 모델 임포트

MONGODB_URL = "mongodb://localhost:27017"
client = MongoClient(MONGODB_URL)
db = client.Verfit  # 데이터베이스 이름 설정


# 데이터베이스 워크북 생성
def create_workbook(workbook_data: Workbook):
    if db.Workbooks.find_one({"workbook_id": workbook_data.workbook_id}):
        return False
    db.Workbooks.insert_one(workbook_data.dict())
    return True


# 데이터베이스 워크북 조회
def get_workbook(workbook_id: int):
    workbook = db.Workbooks.find_one({"workbook_id": workbook_id})
    if workbook:
        return Workbook(**workbook)
    else:
        return None


# 데이터베이스 워크북 수정
def update_workbook(workbook_id: int, workbook_data: Workbook):
    workbook = db.Workbooks.find_one({"workbook_id": workbook_id})
    if workbook:
        try:
            db.Workbooks.update_one({"workbook_id": workbook_id}, {"$set": workbook_data.dict()})
        except Exception as e:
            return {"message": f"워크북 업데이트 과정에서 오류가 발생했습니다: {str(e)}"}
        return "Workbook updated successfully"
    else:
        return "Workbook not found"


# 데이터베이스 워크북 삭제
def delete_workbook(workbook_id: int):
    workbook = db.Workbooks.find_one({"workbook_id": workbook_id})
    if workbook:
        db.Workbooks.delete_one({"workbook_id": workbook_id})
        return "Workbook deleted successfully"
    else:
        return "Workbook not found"


# 데이터베이스 워크북 검색 조회
def get_workbooks():
    try:
        workbooks = list(db.Workbooks.find().sort('created_at', -1))
        return workbooks
    except Exception as e:
        print(f"Error fetching workbooks: {e}")
        return []


# 데이터베이스 워크북 개수 세기
def get_total_num_of_workbooks():
    return db.Workbooks.count_documents({})


def update_user_workbooks(user_email, made_workbooks):
    result = db.users.update_one(
        {"useremail": user_email},
        {"$set": {"made_workbook_id": made_workbooks}}
    )

    if result.modified_count == 1:
        return {"message": "정상적으로 업데이트되었습니다."}
    else:
        return {"message": "업데이트에 실패하였습니다."}


def update_user_fav_workbooks(user_email, fav_workbooks):
    result = db.users.update_one(
        {"useremail": user_email},
        {"$set": {"fav_workbook_id": fav_workbooks}}
    )

    if result.modified_count == 1:
        return {"message": "정상적으로 업데이트되었습니다."}
    else:
        return {"message": "업데이트에 실패하였습니다."}

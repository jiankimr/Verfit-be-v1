from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from workbook.database import *
from workbook.models import *
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from accounts.dependencies import get_current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
import json

load_dotenv()

router = APIRouter(
    prefix="/workbook",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/{workbook_id}', tags=['workbook'])
def get_requested_workbook(workbook_id: int, current_user: UserInDB = Depends(get_current_user)):
    workbook = get_workbook(workbook_id)
    is_owner = False
    is_fav = False
    if workbook:
        if workbook.owner_email == current_user["useremail"]:
            is_owner = True
        if workbook.workbook_id in current_user["fav_workbook_id"]:
            is_fav = True
        return {"workbook": workbook, "isOwner": is_owner, "isFav": is_fav, "message": "해당하는 문제집을 성공적으로 불러왔습니다"}
    else:
        return {"message": "해당 문제집을 불러오는 과정에서 에러가 발생하였습니다"}


@router.post('/{workbook_id}/like', tags=['workbook'])
def like_or_dislike(workbook_id: int, current_user: UserInDB = Depends(get_current_user)):
    list_of_fav = current_user["fav_workbook_id"]
    if workbook_id in list_of_fav:
        list_of_fav.remove(workbook_id)
        is_fav = False
    else:
        list_of_fav.append(workbook_id)
        is_fav = True
    
    try:
        update_user_fav_workbooks(current_user["useremail"], list_of_fav)
        return {"isFav": is_fav, "message": "문제집을 즐겨찾기에 추가 혹은 삭제 완료하였습니다."}
    except:
        return {"message": "문제집을 즐겨찾기에 추가/삭제하는 도중 오류가 발생했습니다."}


@router.post('/{workbook_id}/addcomment', tags=['workbook'])
def add_comment(workbook_id: int, comment: str, current_user: UserInDB = Depends(get_current_user)):

    workbook = get_workbook(workbook_id)
    if workbook:
        list_of_comm = workbook.comments
        print(comment)
        comment = Comments(content=comment, writer=current_user["useremail"], writer_nickname=current_user["username"],
                           created_at=datetime.now())
        list_of_comm.append(comment)
        workbook.comments = list_of_comm

        try:
            update_workbook(workbook_id, workbook)
            updated_workbook = get_workbook(workbook_id)
            return {"comments": updated_workbook.comments, "message": "댓글이 성공적으로 추가되었습니다."}
        except:
            return {"message": "댓글 추가 중 오류가 발생했습니다."}


@router.post('/{workbook_id}/pubpriv', tags=['workbook'])
def pub_or_priv(workbook_id: int, current_user: UserInDB = Depends(get_current_user)):

    workbook = get_workbook(workbook_id)
    if workbook:
        if workbook.owner_email == current_user["useremail"]:
            if workbook.pubpriv == 0:
                workbook.pubpriv = 1
            else:
                workbook.pubpriv = 0

            try:
                update_workbook(workbook_id, workbook)
                return {"message": "문제집의 공개 여부를 변환 완료하였습니다."}
            except:
                return {"message": "문제집의 공개 여부를 변환하는 과정에서 오류가 발생하였습니다."}
        else:
            return {"message": "현재 유저가 만든 문제집이 아닙니다."}
    else:
        return {"message": "문제집을 찾을 수 없습니다."}


@router.post('/{workbook_id}/generate-pdf', tags=['workbook'])
async def generate_pdf(workbook_id: int):

    try:
        pdf_buffer = await create_pdf(workbook_id)

        return StreamingResponse(
            content=pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=generated_pdf.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


async def create_pdf(workbook_id: int):
    workbook = get_workbook(workbook_id)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    pdf.setFont("HYSMyeongJo-Medium", 12)

    pdf.setTitle(workbook.title)

    pdf.drawString(50, 750, "제목: " + workbook.title)
    pdf.drawString(50, 730, "과목: " + workbook.subject)
    pdf.drawString(50, 710, "과목: " + workbook.description)

    summary = workbook.summaries[0].text.replace('"', '')
    summary_array = summary.split('\\n')

    x, y = 50, 670

    for text in summary_array:
        y = line_break(x, y, text, pdf, 50)
        y -= 5

    problems = workbook.problems[0][1]["text"]
    problems = json.loads(problems)

    y -= 35
    for problem in problems:
        y = line_break(x, y, str(problem["Id"]) + "." + problem["Question"], pdf, 80)
        y -= 10
        y = line_break(x, y, "답: " + problem["Answer"], pdf, 80)
        y -= 5
        y = line_break(x, y, "해설: " + problem["Explanation"], pdf, 80)
        y -= 25

    pdf.save()

    pdf_buffer.seek(0)
    return pdf_buffer


def line_break(xn: int, yn: int, text: str, pdf, chunk_size: int):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    x, y = xn, yn
    line_height = 15

    for chunk in chunks:
        if y <= 50:
            pdf.showPage()
            pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
            pdf.setFont("HYSMyeongJo-Medium", 12)
            y = 750

        pdf.drawString(x, y, chunk)
        y -= line_height

    return y

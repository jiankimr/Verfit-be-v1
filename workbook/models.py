# 문제집 생성
from pydantic import BaseModel, Field
from accounts.schemas import *
from typing import List, Optional
from datetime import datetime


class Text(BaseModel):
    text: str


class Comments(BaseModel):
    content: str = Field(..., description="댓글 내용")
    writer: str = Field(..., description="작성자")
    writer_nickname: str = Field(..., description="작성자 닉네임")
    created_at: datetime = Field(..., description="생성 날짜")


class Workbook(BaseModel):
    workbook_id: int = Field(..., description="문제집 고유 ID")
    title: str = Field(..., description="제목")
    subject: str = Field(..., description="과목")
    description: Optional[str] = Field(None, description="설명")
    imgurl: Optional[str] = Field(..., description="표지 이미지 url")
    created_at: datetime = Field(..., description="생성 날짜")
    rate: int = Field(..., description="좋아요 수")
    problems: List[tuple] = Field(..., description="문제집에 포함되어 있는 문제들(type, questions, answers)")
    summaries: List[Text] = Field(..., description="문제집에 포함된 요약 정리본들")
    owner_email: str = Field(..., description="소유자")
    comments: List[Comments] = Field(..., description="댓글")
    pubpriv: int = Field(..., description="공개여부")

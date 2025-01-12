# Verfit-be-v1
* 함께 작업한 사람들
    * 김지안, 김이주, 신수빈, 이우흥

* repo
    * be-v1 origin repo: https://github.com/Verfit2023/verfit_backend
    * be-v2 repo: https://github.com/jiankimr/Verfit-be-v2
    * fe repo: https://github.com/jiankimr/Verfit-fe

# Usage
* 설치
    * `pip install "fastapi[all]"`
    * `pip install openai`
    * `pip install python-dotenv`

* 준비
    * root 파일에 .env 생성 (openai key 유출 조심!)

* 실행
    * 터미널에서 `uvicorn main:app --reload`를 실행
    * <http://127.0.0.1:8000/docs> 에서 API 문서 확인 가능

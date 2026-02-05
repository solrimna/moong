# MOONG! 번개모임 SNS
- 사용자가 즉시 모임을 생성하고 참여할 수 있는 ‘벙개 만남 중심 플랫폼’
- 단순한 인스타그램 클론 코딩에서 벗어난, SNS 플랫폼 프로젝트 수행.

## 초기 실행 방법(필수)
회원가입 화면의 '활동 지역' 목록은 초기 데이터 적재 후 정상 노출됩니다.

### 1) 패키지 설치 or uv sync 수행(uv 사용 시)
- 1안 : 패키지 설치 pip install -r requirements.txt
- 2안 : uv sync(pyproject.toml 이용)

#### 1-1) 주요 설치 라이브러리 내용 기재 
1. django
2. openai : 게시글 작성 후 ai 해시테그 생성 시 사용
3. python-dotenv : apikey 별도 관리를 위해 추가(.env파일은 .gitignore에 포함)
4. apscheduler : django 스케줄러 사용을 위함.
    - 매일 00:05 만료된 모임 게시글을 scheduler.py ->  expire_posts.py 처리를 통해 완료 혹은 취소 처리를 수행. 
5. pillow : 이미지 표기 시 사용

#### 1-2) API KEY 입력하기 : .env파일 생성 후 api key 입력
클론 받은 경로에 .env 파일을 생성합니다 (moong dir 바로 아래)
파일 내용 설정 : 
OPENAI_API_KEY="자신의 api key 입력"
KAKAO_APP_KEY="자신의 카카오 map api key 입력"

##### 1-2-1) KAKAO_APP_KEY 생성하여 얻어오기 (없다면..)
1. https://developers.kakao.com/console/app 접속
2. + 앱생성(이름이) 후 생성한 앱 클릭(추가 설정을 해주기 위해 앱 설정으로 진입)
3. 왼쪽 메뉴 앱 > 플랫폼 키 > JavaScript 키 > Default JS Key 키 클릭 > JavaScript SDK 도메인 설정 
- http://127.0.0.1:8000 추가 
    (python manage.py runserver했을 때 사용되는 url 기재)
    (특이사항 : 주의 localhost와 127.0.0.1 을 카카오에서 구별하기 때문에 유의 필요)
4. 왼쪽 메뉴 제품 설정 > 카카오맵 > 사용 설정 > 상태 off에서 on으로 변경

### 2) 마이그레이션
python manage.py migrate

### 3) 지역 데이터 적재 (생략 가능)
<!--
python manage.py import_locations 
runserver 시 자동으로 실행되어 생략 가능 (처리 내용 : apps.py)
- 실행 시마다 수행되지만, 이미 저장되어있는 경우에는 skip되므로 중복저장되지않음.
-->

### 4) 관리자 계정 생성
python manage.py createsuperuser

### 5) 실행
python manage.py runserver

## 초기 실행 방법(필수)

회원가입 화면의 '활동 지역' 목록은 초기 데이터 적재 후 정상 노출됩니다.

1) 패키지 설치
pip install -r requirements.txt

2) 마이그레이션
python manage.py migrate

3) 지역 데이터 적재
python manage.py import_locations

4) 관리자 계정 생성
python manage.py createsuperuser

5) 실행
python manage.py runserver

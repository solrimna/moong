@echo off
echo DB init start...

REM DB 삭제
del db.sqlite3 2>nul
echo DB file delete start

REM 프로젝트 폴더의 __pycache__만 삭제 (.venv 제외)
for /d %%d in (moong\__pycache__ users\__pycache__ locations\__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo __pycache__ delete complete

REM 프로젝트 폴더의 .pyc만 삭제
del /s /q moong\*.pyc users\*.pyc locations\*.pyc 2>nul
echo .pyc file delete complete

REM migration 파일 삭제
del /q moong\migrations\*.py 2>nul
del /q users\migrations\*.py 2>nul
del /q locations\migrations\*.py 2>nul

REM __init__.py 다시 생성
type nul > moong\migrations\__init__.py
type nul > users\migrations\__init__.py
type nul > locations\migrations\__init__.py
echo migration file delete complete

echo.
echo new migration create...
python manage.py makemigrations moong
python manage.py makemigrations locations
python manage.py makemigrations users
python manage.py makemigrations

echo.
echo migrate start...
python manage.py migrate

echo.
echo DB init complete!
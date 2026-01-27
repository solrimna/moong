import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from locations.models import Location


class Command(BaseCommand):
    help = "행정구역 CSV import (2단계 / 3단계 모두 허용)"

    def handle(self, *args, **kwargs):
        file_path = (
            Path(settings.BASE_DIR)
            / "locations"
            / "data"
            / "국토교통부_행정구역법정동코드_20250807.CSV"
        )

        if not file_path.exists():
            self.stderr.write(
                self.style.ERROR(f"CSV 파일을 찾을 수 없습니다: {file_path}")
            )
            return

        created_count = 0
        skipped_count = 0
        total_count = 0
        eupmyeondong_set = set()  # 중복 체크용

        with open(file_path, encoding="cp949") as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 2:
                    continue

                code = row[0].strip()
                full_name = row[1].strip()

                # 헤더 스킵
                if code == "법정동코드":
                    continue

                parts = full_name.split()

                # 1단계만 있는 경우는 제외
                if len(parts) < 2:
                    continue

                sido = parts[0]
                sigungu = parts[1]

                # 3단계가 있으면 사용, 없으면 빈 문자열
                eupmyeondong = parts[2] if len(parts) >= 3 else ""

                # 중복 체크 (이미 추가한 읍면동은 건너뛰기)
                key = f"{sido}_{sigungu}_{eupmyeondong}"
                if key in eupmyeondong_set:
                    continue

                eupmyeondong_set.add(key)

                obj, created = Location.objects.get_or_create(
                    sido=sido,
                    sigungu=sigungu,
                    eupmyeondong=eupmyeondong,
                )
                #self.stdout.write(f'처리 중... {sido}, {sigungu}, {eupmyeondong}')

                if created:
                    created_count += 1
                else:
                    skipped_count += 1

                # 진행 상황
                if len(eupmyeondong_set) % 100 == 0:
                    self.stdout.write(f'처리 중... {len(eupmyeondong_set)}개 읍면동 skip 갯수확인 {skipped_count}')

        self.stdout.write(
            self.style.SUCCESS(
                f"행정구역 import 완료 (신규 생성: {created_count}개)"
            )
        )

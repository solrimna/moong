from django.db import models

class Location(models.Model):
    sido = models.CharField(max_length=20)
    sigungu = models.CharField(max_length=20)
    eupmyeondong = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"

    # admin 페이지에서 Location 목록이나 선택드롭다운에서 이 형식으로 보인다.
    # class Location이 문자화 되는 모든 곳에 적용

    class Meta:
        verbose_name = '지역'
        verbose_name_plural = '지역'
        db_table = 'location'
        indexes = [
            models.Index(fields=['sido', 'sigungu', 'eupmyeondong']),
        ]
        unique_together = [['sido', 'sigungu', 'eupmyeondong']]  # 중복 방지
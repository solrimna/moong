from datetime import date

from django.core.management.base import BaseCommand

from moong.models import Post


class Command(BaseCommand):
    help = '모임 날짜가 지난 게시글을 자동 만료 처리합니다.'

    def handle(self, *args, **options):
        today = date.today()

        # 만료 대상: moim_date가 오늘 이전 + 아직 완료/폭파 처리 안 된 게시글
        expired_posts = Post.objects.filter(
            moim_date__lt=today,
            complete=True,
            moim_finished=False,
            is_cancelled=False,
        )

        finished_count = 0
        cancelled_count = 0

        for post in expired_posts:
            if post.is_closed:
                # 확정된 모임 → 완료 처리
                post.moim_finished = True
                post.save()
                post.participations.filter(status='APPROVED').update(status='COMPLETED')
                finished_count += 1
            else:
                # 미확정 모임 → 폭파 처리
                post.is_cancelled = True
                post.save()
                cancelled_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'만료 처리 완료 - 완료: {finished_count}건, 폭파: {cancelled_count}건'
            )
        )

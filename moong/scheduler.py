from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: call_command('expire_posts'),
        trigger=CronTrigger(hour=0, minute=5),
        id='expire_posts_daily',
        replace_existing=True,
    )
    scheduler.start()
    print('[Scheduler] 만료 처리 스케줄러 시작 (매일 00:05)')

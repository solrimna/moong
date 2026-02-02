import os

from django.apps import AppConfig


class MoongConfig(AppConfig):
    name = 'moong'

    def ready(self):
        # runserver auto-reload 이중 실행 방지
        if os.environ.get('RUN_MAIN') == 'true':
            from django.core.management import call_command
            call_command('import_locations')

            from moong import scheduler
            scheduler.start()

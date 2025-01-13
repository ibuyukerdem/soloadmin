from django.core.management.base import BaseCommand
from common.utils.logging_helper import test_log_action


class Command(BaseCommand):
    help = 'LogAction test komutu'

    def handle(self, *args, **kwargs):
        self.stdout.write("Log testi başlatılıyor...")
        test_log_action()
        self.stdout.write("Log testi tamamlandı.")

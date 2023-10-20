from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from breathecode.admissions.models import Academy
from ...models import EventbriteWebhook


class Command(BaseCommand):
    help = 'Delete logs and other garbage'

    def handle(self, *args, **options):
        how_many_days_with_error = 60
        how_many_days_with_done = 30
        webhooks = EventbriteWebhook.objects.filter(created_at__lte=datetime.now() -
                                                    timedelta(days=how_many_days_with_done), status='DONE')
        count_done = webhooks.count()
        webhooks.delete()

        webhooks = EventbriteWebhook.objects.filter(created_at__lte=datetime.now() -
                                                    timedelta(days=how_many_days_with_error)).exclude(status='DONE')
        count_error = webhooks.count()
        webhooks.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {str(count_done)} done, and {str(count_error)} errored EventbriteWebhook's"))

import random
from datetime import timedelta

from django.utils import timezone
from faker import Faker

from apps.tasks.models import Task, TimeLog
from apps.accounts.models import User

from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'Create random timelogs for all tasks in database.'

    def add_arguments(self, parser):
        parser.add_argument('instances', type=int, help='Number of task instances to be created.')

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = kwargs['instances']
        task_id = list(Task.objects.values_list('id', flat=True))
        user_id = list(User.objects.values_list('id', flat=True))
        if task_id:
            instances = []
            for i in range(total):
                instances.append(
                    TimeLog(task_id=random.choice(task_id),
                            user_id=random.choice(user_id),
                            started_at=timezone.now() - timedelta(hours=i * 2),
                            duration=timedelta(minutes=random.randint(2, 1000)),)
                )
            TimeLog.objects.bulk_create(instances, total)
        else:
            return self.stdout.write(self.style.ERROR(f'The database has no tasks to timelog.'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} timelogs.'))

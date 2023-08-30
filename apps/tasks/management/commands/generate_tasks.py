import random

from faker import Faker

from apps.accounts.models import User

from django.core.management.base import BaseCommand

from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Create random tasks for all users in database.'

    def add_arguments(self, parser):
        parser.add_argument('instances', type=int, help='Number of task instances to be created.')

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = kwargs['instances']
        users_id = list(User.objects.values_list('id', flat=True))
        if users_id:
            instances = []
            for i in range(total):
                instances.extend([
                    Task(title=fake.name(),
                         description=fake.text(),
                         assigned_to_id=random.choice(users_id),
                         created_by_id=random.choice(users_id))
                ]
                )
            while True:
                if not len(instances):
                    break
                Task.objects.bulk_create(instances, total)
        else:
            return self.stdout.write(self.style.ERROR(f'The database has no users to assign tasks.'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} tasks.'))

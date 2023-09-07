import random

from faker import Faker

from apps.tasks.models import Task, Comment

from django.core.management.base import BaseCommand

from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Create random comments for all tasks in database.'

    def add_arguments(self, parser):
        parser.add_argument('instances', type=int, help='Number of task instances to be created.')

    def handle(self, *args, **kwargs):
        if not kwargs.get('instances') and kwargs.get('instances') > 0:
            return self.stdout.write((self.style.ERROR('Missing argument the "instances".')))

        total = kwargs.get('instances')
        fake = Faker()
        task_id = list(Task.objects.values_list('id', flat=True))
        if not task_id:
            return self.stdout.write(self.style.ERROR(f'The database has no tasks to comment.'))

        instances = []
        for _ in range(total):
            instances.append(
                Comment(task_id=random.choice(task_id),
                        text=fake.text())
            )
        Comment.objects.bulk_create(instances, total)



        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} comments.'))

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
        fake = Faker()
        total = kwargs['instances']
        task_id = list(Comment.objects.values_list('id', flat=True))
        if task_id:
            instances = []
            for i in range(total):
                instances.extend([
                    Comment(task_id=random.choice(task_id),
                            text=fake.text())
                ]
                )
            while True:
                if not len(instances):
                    break
                Task.objects.bulk_create(instances, total)
        else:
            return self.stdout.write(self.style.ERROR(f'The database has no tasks to comment.'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} comments.'))
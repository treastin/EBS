import datetime

from django.db import models
from django.utils import timezone

from apps.accounts.models import User


# Create your models here.

class Task(models.Model):

    class Status(models.TextChoices):
        todo = 'to_do', 'To do'
        assigned = 'assigned', 'Assigned'
        in_progress = 'in_progress', 'In progress'
        completed = 'completed', 'Completed'

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.todo)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by', null=True)

    def __str__(self):
        return f" \"{self.title}\" By: {self.assigned_to.get_full_name()}"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.task.title} : {self.text}'


class Timelog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(default=None, null=True)

    def __str__(self):
        return f'Timelog of \"{self.task.title}\" id({self.id})'



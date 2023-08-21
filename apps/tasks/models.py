import datetime

from django.db import models
from django.utils import timezone

from apps.accounts.models import CustomUser


# Create your models here.


# id title description status owner

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=32)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f" \"{self.title}\" By: {self.owner.get_full_name()}"


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



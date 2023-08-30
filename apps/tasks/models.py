import datetime

from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User


# Create your models here.

class TaskQuerySet(models.QuerySet):
    def with_total_duration(self):
        return self.annotate(total_duration=(models.Sum('timelog_task__duration'))).order_by('-id')


class Task(models.Model):
    objects = TaskQuerySet.as_manager()

    class Status(models.TextChoices):
        TODO = 'to_do'
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.TODO)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigns', null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', null=True)


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.task.title} : {self.text}'


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelog_task', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timelog_user', null=True)
    started_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(default=datetime.timedelta(), null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Timelog of \"{self.task.title}\" id({self.id})'


class Timer(models.Model):
    class Meta:
        unique_together = [
            ('user', 'task')
        ]
        ordering = ['-id']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_timer')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_timer')
    started_at = models.DateTimeField(auto_now_add=True)
    is_started = models.BooleanField(default=False)

    def start(self):
        if not self.is_started:
            self.is_started = True
            self.started_at = timezone.now()
            self.save()

    def stop(self):
        if self.is_started:
            duration = timezone.now() - self.started_at

            self.is_started = False
            self.save()

            timelog = TimeLog.objects.create(
                user=self.user,
                task=self.task,
                started_at=self.started_at,
                duration=duration
            )
            timelog.save()
        else:
            raise ValidationError({'detail': f'Task id:{self.id} has no ongoing timer.'})


@receiver(pre_save, sender=Task)
def send_email(sender, instance, *args, **kwargs):
    if instance.status == 'completed':
        mail_subject = "You have task is now complete!"
        mail_message = f"The task \"{instance.title}\"!"
    else:
        mail_subject = "You have ben assigned a new task!",
        mail_message = f"You have ben assigned a new task!\n The new task is \"{instance.title}\"."

    try:
        send_mail(
            recipient_list=[instance.assigned_to.email],
            subject=mail_subject,
            message=mail_message,
            from_email=None
        )
    except:
        return


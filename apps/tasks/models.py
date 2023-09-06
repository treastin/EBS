import datetime

from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'to_do'
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.TODO)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigns')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.task.title} : {self.text}'


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelog_task')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timelog_user')
    started_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(default=datetime.timedelta())

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
        if not self.is_started:
            raise ValidationError({'detail': f'Task id:{self.task.id} has no ongoing timer.'})

        duration = timezone.now() - self.started_at

        self.is_started = False
        self.save()

        timelog = TimeLog.objects.create(
            user=self.user,
            task=self.task,
            started_at=self.started_at,
            duration=duration
        )
        return timelog


@receiver(post_save, sender=Task)
def send_email(sender, instance, created, *args, **kwargs):
    if created:
        mail_subject = "You have ben assigned a new task!",
        mail_message = f"You have ben assigned a new task!\n The new task is \"{instance.title}\"."
        send_mail(
            recipient_list=[instance.assigned_to.email],
            subject=mail_subject,
            message=mail_message,
            from_email=None,
            fail_silently=True,
        )


from django.contrib import admin

from apps.tasks.models import Task, TimeLog, Comment

# Register your models here.

admin.site.register(Task)
admin.site.register(TimeLog)
admin.site.register(Comment)

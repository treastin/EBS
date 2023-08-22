from django.contrib import admin

from apps.tasks.models import Task, Timelog, Comment

# Register your models here.

admin.site.register(Task)
admin.site.register(Timelog)
admin.site.register(Comment)

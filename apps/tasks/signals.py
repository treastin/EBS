from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.tasks.models import Comment
from apps.tasks.documents import TaskDocument


@receiver(post_save, sender=Comment)
def update_document(sender, **kwargs):
    instance = kwargs.get('instance')
    document = TaskDocument()
    document.update(instance.task)


@receiver(post_delete, sender=Comment)
def delete_document(sender, **kwargs):
    instance = kwargs.get('instance')
    document = TaskDocument()
    document.update(instance.task)

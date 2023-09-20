from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.tasks.models import Comment, Task
from apps.tasks.documents import TaskDocument
from apps.tasks.serializers import TaskListDocumentSerializer

from apps.tasks.elasticsearch import elastic


@receiver([post_save, post_delete], sender=Comment)
def update_document_dsl_drf(sender, **kwargs):
    instance = kwargs.get('instance')
    document = TaskDocument()
    document.update(instance.task)


@receiver(post_save, sender=Task)
def update_document(sender, **kwargs):
    instance = kwargs.get('instance')
    data = TaskListDocumentSerializer(instance).data
    elastic.add_document(elastic.index_prefix, data, '_doc', data.get('id'))


@receiver(post_delete, sender=Task)
def update_document(sender, **kwargs):
    instance = kwargs.get('instance')
    elastic.session.delete(elastic.index_prefix, instance.id)


@receiver(post_save, sender=Comment)
def update_document(sender, **kwargs):
    instance = kwargs.get('instance')
    data = TaskListDocumentSerializer(instance.task).data
    elastic.add_document(elastic.index_prefix, data, '_doc', data.get('id'))


@receiver(post_delete, sender=Comment)
def update_document(sender, **kwargs):
    instance = kwargs.get('instance')
    data = TaskListDocumentSerializer(instance.task).data
    elastic.add_document(elastic.index_prefix, data, '_doc', data.get('id'))

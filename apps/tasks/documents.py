from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.tasks.models import Task, Comment


@registry.register_document
class TaskDocument(Document):
    comment = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'text': fields.TextField(),

    })

    class Index:
        name = 'tasks_dsl_drf'
        settings = {
            'number_of_shards': 1,
            "number_of_replicas": 0
        }

    class Django:
        model = Task
        fields = [
            'id',
            'title',
        ]
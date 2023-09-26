from django.core.management import BaseCommand
from apps.tasks.elasticsearch import elastic
from apps.tasks.models import Task
from apps.tasks.serializers import TaskESSerializer
from elasticsearch import Elasticsearch
import json


class Command(BaseCommand):
    help = 'Synchronises ElasticSearch indexes.'

    def handle(self, *args, **kwargs):
        queryset = Task.objects.prefetch_related('comment')
        es = Elasticsearch(hosts=elastic.hosts)

        self.stdout.write(f'Indexing {queryset.count()} tasks')
        prefix = elastic.index_prefix

        item_count = 0
        body = []
        for task in queryset:
            data = TaskESSerializer(task).data
            body.append({"index": {"_index": prefix, "_id": task.id}})
            body.append(json.dumps(data))

            if item_count % 500 == 0:
                es.bulk(body=body)
                body.clear()
            item_count += 1

        if body.count:
            es.bulk(body=body)
            body.clear()

        self.stdout.write(self.style.SUCCESS(f'Successfully indexed {queryset.count()} tasks'))

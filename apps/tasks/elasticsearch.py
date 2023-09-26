from django.conf import settings
from drf_util.elastic import ElasticUtil


class Elastic(ElasticUtil):
    hosts = settings.ELASTICSEARCH_DSL.get('default').get('hosts')
    index_prefix = 'tasks'
    content_prefix = 'tasks/'


elastic = Elastic()

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from todo.models import Task
from todo.serializers import TaskSerializer


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 5


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

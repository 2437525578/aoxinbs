from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Chemical
from .serializers import ChemicalSerializer
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache # Import cache


class ChemicalPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChemicalViewSet(viewsets.ModelViewSet):
    queryset = Chemical.objects.all()
    serializer_class = ChemicalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['form_state', 'signal_word', 'hazard_classes']
    search_fields = ['name_cn', 'cas_no', 'specification']
    ordering_fields = ['name_cn', 'cas_no', 'form_state', 'signal_word', 'last_updated']
    pagination_class = ChemicalPagination

    def get_queryset(self):
        queryset = cache.get('chemicals_queryset')
        if queryset is None:
            queryset = Chemical.objects.all()
            cache.set('chemicals_queryset', queryset, 60 * 5)  # Cache for 5 minutes
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        cache.delete('chemicals_queryset')  # Invalidate cache on create
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        # 实现导出 Excel 逻辑
        return Response({"message": "导出 Excel 功能待实现"})

    @action(detail=False, methods=['post'], url_path='import-excel')
    def import_excel(self, request):
        # 实现导入 Excel 逻辑
        return Response({"message": "导入 Excel 功能待实现"})

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache # Import cache

from django.http import HttpResponse


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['chemical', 'location', 'unit']
    search_fields = ['chemical__name_cn', 'chemical__cas_no', 'location', 'batch_number']
    ordering_fields = ['chemical__name_cn', 'location', 'quantity', 'expiry_date', 'last_updated']
    ordering = ['chemical__name_cn']

    def get_queryset(self):
        queryset = cache.get('inventory_items_queryset')
        if queryset is None:
            queryset = InventoryItem.objects.select_related('chemical', 'added_by')
            cache.set('inventory_items_queryset', queryset, 60 * 5)  # Cache for 5 minutes
        return queryset

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
        cache.delete('inventory_items_queryset')  # Invalidate cache on create

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids or not isinstance(ids, list):
            return Response({"detail": "请提供有效的 ID 列表。"}, status=status.HTTP_400_BAD_REQUEST)

        # 可以在这里添加权限检查，例如只有管理员才能批量删除
        # if request.user.role != 'admin':
        #     return Response({"detail": "无权限执行此操作。"}, status=status.HTTP_403_FORBIDDEN)

        # 执行删除
        queryset = self.get_queryset().filter(id__in=ids)
        deleted_count, _ = queryset.delete()
        cache.delete('inventory_items_queryset')  # Invalidate cache on bulk delete
        return Response({"message": f"成功删除了 {deleted_count} 条记录。"},
                        status=status.HTTP_204_NO_CONTENT)  # 204 通常不返回消息体，但可以自定义

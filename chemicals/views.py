from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from .models import Chemical
from .serializers import ChemicalSerializer
from rest_framework import serializers


class ChemicalPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChemicalViewSet(viewsets.ModelViewSet):
    """
    迁移 /add 和 /list
    """
    queryset = Chemical.objects.all()
    serializer_class = ChemicalSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_cn', 'cas_no', 'specification']
    ordering_fields = ['name_cn', 'cas_no', 'form_state', 'signal_word', 'last_updated']
    pagination_class = ChemicalPagination

    def create(self, request, *args, **kwargs):
        """
        迁移 /add
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # 匹配 Flask 的成功响应
            return Response(
                {'message': 'Chemical added successfully', 'chemical': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as e:
            # 匹配 Flask 的错误响应
            error_msg = next(iter(e.detail.values()))[0] if isinstance(e.detail, dict) else e.detail[0]
            if "required" in error_msg:
                return Response({'message': f'{next(iter(e.detail.keys()))} is required'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error adding chemical', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Error adding chemical', 'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        迁移 /list
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        # Flask /list 直接返回列表，DRF 默认也是如此
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'No IDs provided for deletion.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Chemical.objects.filter(id__in=ids).delete()
        return Response({'message': f'Successfully deleted {deleted_count} chemicals.'},
                        status=status.HTTP_204_NO_CONTENT)
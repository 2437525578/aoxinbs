from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Chemical
from .serializers import ChemicalSerializer
from rest_framework import serializers
class ChemicalViewSet(viewsets.ModelViewSet):
    """
    迁移 /add 和 /list
    """
    queryset = Chemical.objects.all().order_by('-created_at')
    serializer_class = ChemicalSerializer
    permission_classes = [permissions.AllowAny] # 保持 Flask 的逻辑（未认证）

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
                return Response({'message': f'{next(iter(e.detail.keys()))} is required'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error adding chemical', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Error adding chemical', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        迁移 /list
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Flask /list 直接返回列表，DRF 默认也是如此
        return Response(serializer.data)
# F:\aoxinbs_django\inventory\serializers.py
from rest_framework import serializers
from .models import InventoryItem
from chemicals.models import Chemical # 需要导入 Chemical 以便设置 queryset
from chemicals.serializers import ChemicalSerializer # 用于嵌套显示化学品详情

class InventoryItemSerializer(serializers.ModelSerializer):
    # Read-only 嵌套显示化学品详细信息
    chemical_details = ChemicalSerializer(source='chemical', read_only=True)
    # Writable 用于在创建/更新时通过 ID 关联化学品
    chemical = serializers.PrimaryKeyRelatedField(queryset=Chemical.objects.all())
    # Read-only 显示添加人的用户名
    added_by_username = serializers.CharField(source='added_by.username', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id',
            'chemical', # Writable ID field
            'chemical_details', # Read-only nested details
            'location',
            'quantity',
            'unit',
            'batch_number',
            'purchase_date',
            'expiry_date',
            'added_by_username',
            'last_updated'
        ]
        read_only_fields = ['last_updated', 'added_by_username']

    # 可以在这里添加验证逻辑，例如 quantity 必须大于 0
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("数量不能为负数。")
        return value
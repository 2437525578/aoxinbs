from rest_framework import serializers
from .models import Chemical


class ChemicalSerializer(serializers.ModelSerializer):
    # 映射 Flask 的驼峰命名
    nameCn = serializers.CharField(source='name_cn')
    casNo = serializers.CharField(source='cas_no')
    formState = serializers.CharField(source='form_state', required=False, allow_null=True, allow_blank=True)
    signalWord = serializers.CharField(source='signal_word', required=False, allow_null=True, allow_blank=True)
    image = serializers.ImageField(required=False)
    hazardClasses = serializers.ListField(
        child=serializers.CharField(),
        source='hazard_classes_list',  #
        required=False
    )

    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Chemical
        # 字段列表使用 API 期望的驼峰命名
        fields = (
            'id',
            'nameCn',
            'casNo',
            'specification',
            'formState',
            'hazardClasses',
            'signalWord',
            'createdAt',
            'updatedAt',
            'image'
        )

    def create(self, validated_data):
        # 将 hazard_classes_list (列表) 转换回 hazard_classes (字符串)
        hazard_list = validated_data.pop('hazard_classes_list', [])
        validated_data['hazard_classes'] = ','.join(hazard_list)
        # Serializer 会自动处理 'source' 字段的映射
        return Chemical.objects.create(**validated_data)
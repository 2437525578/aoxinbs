from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    迁移 /login
    在返回的 Token 中加入 role
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义声明
        token['username'] = user.username
        token['role'] = user.role  #
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # 添加 role 到响应体
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['token'] = data.pop('access')  #
        data['code'] = 200  #
        data['message'] = "登录成功"  #
        data.pop('refresh')
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    迁移 /register 逻辑
    """
    password = serializers.CharField(write_only=True, required=True)
    validators = [validate_password]
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='user'  # 默认角色
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='user'  # 默认角色
        )
        # 使用 Django 的方式设置哈希密码
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    迁移 /change_password 逻辑
    """
    username = serializers.CharField(required=True)  # 接收 username
    oldPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("旧密码不正确或用户不存在")
        try:
            validate_password(new_password, user=user)
        except serializers.ValidationError as e:
            # 将 Django 的验证错误转换为 DRF 的错误
            raise serializers.ValidationError({"newPassword": list(e.messages)})

        data['user_instance'] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data['user_instance']
        user.set_password(self.validated_data['newPassword'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    迁移 /reset-password/request
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    迁移 /reset-password/confirm/<token>
    """
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # 迁移 Flask 的复杂度校验
        if len(value) < 8 or not any(char.isupper() for char in value) or \
                not any(char.islower() for char in value) or not any(char.isdigit() for char in value):
            raise serializers.ValidationError("密码必须至少8个字符，包含大小写字母和数字")
        return value
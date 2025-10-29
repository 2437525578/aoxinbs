
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

from .serializers import (
    MyTokenObtainPairSerializer,
    UserRegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer  # 这个 Serializer 保持不变
)
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_str, force_bytes  # <-- 1. 导入 Django 工具
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # <-- 1. 导入 Django 工具
from django.contrib.auth.tokens import default_token_generator  # <-- 2. 导入 Django 的 token 生成器
from django.core.cache import cache  # 导入 cache 模块


# from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature # <-- 3. 移除 itsdangerous

# --- UserLoginView, UserRegisterView, ChangePasswordView 保持不变 ---
class VerificationCodeView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"code": 400, "message": "缺少邮箱地址"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查邮箱格式
        if not CustomUser.objects.filter(email=email).exists():
            # 这里可以根据需求决定是否在发送验证码时就检查用户是否存在
            # 目前为了安全，即使邮箱不存在也返回成功，避免暴露用户信息
            pass

        # 生成随机验证码
        import random
        verification_code = ''.join(random.choices('0123456789', k=6))

        # 存储验证码到缓存，例如 5 分钟过期
        cache.set(f'verification_code:{email}', verification_code, 300)  # 300 秒 = 5 分钟

        # 发送邮件
        subject = "您的验证码"
        message = f"您的验证码是：{verification_code}，5分钟内有效。"
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"code": 200, "message": "验证码已发送至您的邮箱"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"DEBUG: Failed to send verification code email: {e}")
            return Response({"code": 500, "message": "发送验证码邮件失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"code": 401, "message": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        captcha = request.data.get('captcha')

        if not email or not captcha:
            return Response({"code": 400, "message": "缺少邮箱或验证码"}, status=status.HTTP_400_BAD_REQUEST)

        stored_captcha = cache.get(f'verification_code:{email}')

        if not stored_captcha or stored_captcha != captcha:
            return Response({"code": 400, "message": "验证码错误或已过期"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证码正确，可以删除缓存中的验证码
        cache.delete(f'verification_code:{email}')

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"code": 201, "message": "用户注册成功"}, status=status.HTTP_201_CREATED, )
        except serializers.ValidationError as e:
            error_msg = next(iter(e.detail.values()))[0] if isinstance(e.detail, dict) else e.detail[0]
            code = 409 if "已存在" in error_msg or "已被注册" in error_msg else 400
            return Response({"code": code, "message": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"code": 500, "message": f"用户注册失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"code": 200, "message": "密码修改成功"}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            error_msg = next(iter(e.detail.values()))[0] if isinstance(e.detail, dict) else e.detail[0]
            code = 401 if "旧密码不正确" in error_msg else 400
            return Response({"code": code, "message": error_msg}, status=status.HTTP_400_BAD_REQUEST)


# --- V V V V V V 4. 替换 send_reset_email V V V V V V ---
def send_reset_email(user, request):  # 添加 request 参数
    # 使用 Django 的 token 生成器
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # 更新链接格式，包含 uid 和 token (使用 query 参数)
    frontend_base_url = "http://localhost:5173"  # 确保端口正确
    reset_path = "/reset-password"
    reset_link = f"{frontend_base_url}{reset_path}?uid={uid}&token={token}"  # <-- 新格式

    msg_body = f"""您好，{user.username}！

您请求重置密码。请点击以下链接重置您的密码：
{reset_link}

此链接将在一定时间后失效。

如果您没有请求重置密码，请忽略此邮件。

此致，
您的管理团队
"""
    try:
        send_mail(
            "密码重置请求",
            msg_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"DEBUG: Failed to send password reset email: {e}")
        return False


# --- ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ---


# --- V V V V V V 5. 替换 PasswordResetRequestView V V V V V V ---
class PasswordResetRequestView(APIView):
    """
    请求密码重置 (使用 Django Token)
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"code": 400, "message": "缺少邮箱地址"}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            if not send_reset_email(user, request):  # 传递 request
                return Response({"code": 500, "message": "发送密码重置邮件失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except CustomUser.DoesNotExist:
            pass  # 不暴露用户是否存在

        # 保持安全响应
        return Response({"code": 200, "message": "密码重置链接已发送至您的邮箱"}, status=status.HTTP_200_OK)


# --- ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ---


# --- V V V V V V 6. 替换 PasswordResetConfirmView V V V V V V ---
class PasswordResetConfirmView(APIView):
    """
    确认密码重置 (使用 Django Token)
    (Token 不再是 URL 路径参数，uid 和 token 改为从 query 参数获取)
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        # 从 Query 参数获取 uid 和 token
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not serializer.is_valid() or not uidb64 or not token:
            return Response({"code": 400, "message": "缺少必要参数或密码不符合要求"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        # 使用 Django 的 token 验证器
        if user is not None and default_token_generator.check_token(user, token):
            try:
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"code": 200, "message": "密码重置成功"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"code": 500, "message": "密码重置失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 令牌无效或已过期 (Django 的 check_token 会处理过期)
            return Response({"code": 400, "message": "重置链接无效或已过期"}, status=status.HTTP_400_BAD_REQUEST)


# --- ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ---
class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserRegisterSerializer

    def get_object(self):
        return self.request.user


class CheckUsernameView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"code": 400, "message": "缺少用户名"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response({"code": 409, "message": "用户名已存在"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({"code": 200, "message": "用户名可用"}, status=status.HTTP_200_OK)


class CheckEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"code": 400, "message": "缺少邮箱"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"code": 409, "message": "邮箱已存在"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({"code": 200, "message": "邮箱可用"}, status=status.HTTP_200_OK)
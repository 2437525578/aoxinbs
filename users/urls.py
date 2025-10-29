from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

# 对应 Flask 的 url_prefix='/api/user'
urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('send-verification-code/', views.VerificationCodeView.as_view(), name='send_verification_code'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/request/', views.PasswordResetRequestView.as_view(), name='reset_password_request'),
    path('reset-password/confirm/', views.PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('check-username/', views.CheckUsernameView.as_view(), name='check_username'),
    path('check-email/', views.CheckEmailView.as_view(), name='check_email'),
]
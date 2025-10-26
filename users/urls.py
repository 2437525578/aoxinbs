from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

# 对应 Flask 的 url_prefix='/api/user'
urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/request/', views.PasswordResetRequestView.as_view(), name='reset_password_request'),
    path('reset-password/confirm/', views.PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
]
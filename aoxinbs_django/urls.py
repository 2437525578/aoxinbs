from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls), # Django 自带的管理后台
    
    # 对应 app.register_blueprint(user_bp, url_prefix='/api/user')
    path('api/user/', include('users.urls')),
    
    # 对应 app.register_blueprint(chemical_bp, url_prefix='/api/chemical')
    path('api/chemical/', include('chemicals.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
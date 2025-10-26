from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# /api/chemical/ (GET=list, POST=create)
router.register(r'', views.ChemicalViewSet, basename='chemical')

urlpatterns = [
    path('', include(router.urls)),
]
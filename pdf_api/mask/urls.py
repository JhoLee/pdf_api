from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'mask'

router = routers.DefaultRouter()
router.register('request', views.MaskRequestViewSet)
router.register('result', views.MaskResultViewSet)

urlpatterns = [
    path('', include(router.urls)),

]

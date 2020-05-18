from rest_framework import viewsets

from .models import MaskRequest, MaskResult
from .serializers import MaskRequestSerializer, MaskResultSerializer


class MaskRequestViewSet(viewsets.ModelViewSet):
    queryset = MaskRequest.objects.all()
    serializer_class = MaskRequestSerializer


class MaskResultViewSet(viewsets.ModelViewSet):
    queryset = MaskResult.objects.all()
    serializer_class = MaskResultSerializer

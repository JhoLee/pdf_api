from celery.result import AsyncResult
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MaskRequest, MaskResult
from .serializers import MaskRequestSerializer, MaskResultSerializer


class MaskRequestViewSet(viewsets.ModelViewSet):
    queryset = MaskRequest.objects.all()
    serializer_class = MaskRequestSerializer

    @action(methods=['GET'], detail=True)
    def monitor_mask_progress(self, request, slug):
        mask_request = self.get_object()
        progress = 100
        result = AsyncResult(mask_request.task_id)
        if isinstance(result.info, dict):
            progress = request.info['progress']
        description = result.state
        return Response(
            {
                'progress': progress,
                'description': description
            },
            status=status.HTTP_200_OK)


class MaskResultViewSet(viewsets.ModelViewSet):
    queryset = MaskResult.objects.all()
    serializer_class = MaskResultSerializer

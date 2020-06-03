from celery import chain
from celery.backends.database import TaskSet
from rest_framework import serializers

from .models import MaskRequest, MaskResult
from .tasks import mask_image


class MaskRequestSerializer(serializers.ModelSerializer):
    result_image = serializers.ImageField(source='maskresult.result_image', read_only=True)
    status = serializers.CharField(source='maskresult.status', read_only=True)

    class Meta:
        model = MaskRequest
        fields = ("id", "author", "image", "reg_date", "result_image", "status")

    def create(self, validated_data):
        author = validated_data.get('author')
        image = validated_data.get('image')
        reg_date = validated_data.get('reg_date')
        mask_request = MaskRequest.objects.create(
            author=author,
            image=image,
            reg_date=reg_date
        )
        mask_image.delay(mask_request.id)

        return mask_request


class MaskResultSerializer(serializers.ModelSerializer):
    request_image = serializers.ImageField(source='request.image', read_only=True)

    class Meta:
        model = MaskResult
        fields = ('status', 'request', 'request_image', 'result_image', 'mod_date')

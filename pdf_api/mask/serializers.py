from rest_framework import serializers

from .models import MaskRequest, MaskResult
from .tasks import run_mask


class MaskRequestSerializer(serializers.ModelSerializer):
    result_image = serializers.ImageField(source='maskresult.result_image', read_only=True)
    status = serializers.CharField(source='maskresult.status', read_only=True)

    class Meta:
        model = MaskRequest
        fields = ("id", "author", "image", "seg_method", "masking_method", "reg_date", "result_image", "status")
        # lookup_field = 'result'

    def create(self, validated_data):
        author = validated_data.get('author')
        image = validated_data.get('image')
        seg_method = validated_data.get('seg_method')
        masking_method = validated_data.get('masking_method')
        reg_date = validated_data.get('reg_date')
        mask_request = MaskRequest.objects.create(
            author=author,
            image=image,
            seg_method=seg_method,
            masking_method=masking_method,
            reg_date=reg_date
        )
        # run_mask.delay(mask_request.id)
        run_mask.delay(mask_request.id)
        return mask_request


class MaskResultSerializer(serializers.ModelSerializer):
    request_image = serializers.ImageField(source='request.image', read_only=True)

    class Meta:
        model = MaskResult
        fields = ('status', 'request', 'request_image', 'result_image', 'mod_date')

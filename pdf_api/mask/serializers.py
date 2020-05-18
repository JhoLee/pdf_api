from rest_framework import serializers

from .models import MaskRequest, MaskResult


class MaskRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaskRequest
        fields = "__all__"
        # lookup_field = 'result'


class MaskResultSerializer(serializers.ModelSerializer):
    request_image = serializers.ReadOnlyField(source='maskrequest.image')

    class Meta:
        model = MaskResult
        fields = "__all__"

import os

from django.db import models
from django.utils.translation import gettext_lazy as _


def original_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/%Y/%m/%d/{}/original.{}'.format(instance.id, ext)


def result_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/%Y/%m/%d/{}/result.{}'.format(instance.mask_request.id, ext)


class MaskRequest(models.Model):
    author = models.EmailField(max_length=40)
    image = models.ImageField(default=None, upload_to=original_image_path)
    mask_method = models.CharField(max_length=10)
    reg_date = models.DateTimeField(auto_now_add=True)


class MaskResult(models.Model):
    class Status(models.TextChoices):
        STAND_BY = 'SB', _('StandBy')
        PROCESSING = 'PR', _('Processing')
        FINISH = 'FN', _('Finish')
        ERROR = 'ER', _('Error')
        EXPIRED = 'EX', _('Expired')

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.STAND_BY
    )

    mask_request = models.ForeignKey(MaskRequest, on_delete=models.CASCADE)
    result_image = models.ImageField(blank=True, upload_to=result_image_path)
    mod_date = models.DateTimeField(auto_now=True)
    #TODO

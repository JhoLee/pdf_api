import os
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


def original_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/{:%Y/%m/%d}/{}/original{}'.format(datetime.now(), instance.id, ext)


def result_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/{:%Y/%m/%d}/{}/result{}'.format(datetime.now(), instance.mask_request.id, ext)


class MaskRequest(models.Model):
    author = models.EmailField(max_length=40)
    image = models.ImageField(default=None, upload_to=original_image_path)
    mask_method = models.CharField(max_length=10)
    reg_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.image
            self.image = None
            super(MaskRequest, self).save(*args, **kwargs)
            self.image = saved_image
        return super(MaskRequest, self).save(*args, **kwargs)

    def __str__(self):
        return "Mask Request #{} - {}".format(self.id, self.author)


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

    mask_request = models.OneToOneField(
        MaskRequest,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    result_image = models.ImageField(blank=True, upload_to=result_image_path)
    mod_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            saved_image = self.result_image
            self.result_image = None
            super(MaskResult, self).save(*args, **kwargs)
            self.result_image = saved_image
        return super(MaskResult, self).save(*args, **kwargs)

    def __str__(self):
        return "Mask Result of Request #{}".format(self.mask_request.id)

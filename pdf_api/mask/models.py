import os
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


def original_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/{0:%Y/%m/%d}/original/{0:%H%M%S}{1}'.format(datetime.now(), ext)


def result_image_path(instance, filename):
    ext = os.path.splitext(filename)[-1].lower()
    return 'mask/{0:%Y/%m/%d}/result/{0:%H%M%S}{1}'.format(datetime.now(), ext)


class MaskRequest(models.Model):

    author = models.EmailField(max_length=40)
    image = models.ImageField(default=None, upload_to=original_image_path)
    reg_date = models.DateTimeField(auto_now_add=True)

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

    request = models.OneToOneField(
        MaskRequest,
        on_delete=models.CASCADE,
    )
    result_image = models.ImageField(blank=True, upload_to=result_image_path)
    mod_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Mask Result of Request #{}".format(self.request.id)


@receiver(post_save, sender=MaskRequest)
def create_mask_result(sender, instance, created, **kwargs):
    if created:
        MaskResult.objects.create(request=instance)


@receiver(post_save, sender=MaskRequest)
def save_mask_result(sender, instance, **kwargs):
    instance.maskresult.save()


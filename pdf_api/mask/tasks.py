import os

import cv2
import numpy as np
from django.core.files.base import ContentFile
from pdf_api.celery import app
from pdf_api.settings import BASE_DIR

from .models import MaskRequest, MaskResult
from .seg_models.torchmodel import TorchModel
from .utils import combined_masking

models = ('deeplabv3_resnet101', 'fcn_resnet101')


@app.task(bind=True)
def mask_image(self, mask_request_id):
    try:
        # update the task id on the mask_request for future monitoring
        mask_request = MaskRequest.objects.get(id=mask_request_id)
        mask_request.task_id = self.request.id
        mask_request.maskresult.status = MaskResult.Status.PROCESSING
        mask_request.save()

        # loading model architecture
        self.update_state(state='Loading models', meta={'progress': 0})
        torch_model = TorchModel()

        ## pre-processing the image
        self.update_state(state='Pre-processing the image', meta={'progress': 30})
        img_path = os.path.join(BASE_DIR, 'media', str(mask_request.image))
        torch_model.frame = img_path
        torch_model.preprocess_image()

        ## finding the face
        self.update_state(state='Finding the face', meta={'progress': 50})
        torch_model.predict()
        mask = torch_model.mask

        ## masking the face
        self.update_state(state='Masking the face', meta={'progress': 90})
        img = torch_model.frame
        result = combined_masking(img, mask)

        # Save
        # print(result.shape)
        _, out_img = cv2.imencode('.jpg', np.asarray(result))
        out_img = out_img.tobytes()
        out_file = ContentFile(out_img)
        out_path = img_path.replace('/original/', '/mask/')
        mask_request.maskresult.result_image.save(out_path, out_file)
        mask_request.maskresult.status = MaskResult.Status.FINISH
        mask_request.save()
        e = 1

    except Exception as e:
        mask_request.maskresult.status = MaskResult.Status.ERROR
        mask_request.save()
        print()
        print(str(e))

    finally:
        # finish
        self.update_state(state='Finished', meta={'progress': 100})


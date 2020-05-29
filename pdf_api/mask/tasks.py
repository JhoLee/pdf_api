import base64
import os

import PIL
import cv2
import numpy as np
import torch
from django.core.files.base import ContentFile

from pdf_api.celery import app
from pdf_api.settings import BASE_DIR
from torch.autograd import Variable

from .seg_models.segmodel import SegModel
from .utils import gaussian_blur, mosaic
from .models import MaskRequest, MaskResult


@app.task(bind=True)
def run_mask(self, mask_request_id):
    try:
        # update the task id on the mask_request for future monitoring
        mask_request = MaskRequest.objects.get(id=mask_request_id)
        mask_request.task_id = self.request.id
        mask_request.maskresult.status = MaskResult.Status.PROCESSING
        mask_request.save()

        # loading model architecture
        self.update_state(state='Loading the model', meta={'progress': 0})
        model = SegModel()
        model_name = mask_request.get_seg_method_display().lower()
        model.load_model(model_name)

        ## pre-processing the image
        self.update_state(state='Pre-processing the image', meta={'progress': 30})
        img_path = os.path.join(BASE_DIR, 'media', str(mask_request.image))
        model.load_image(img_path)
        model.preprocess_image()

        ## finding the face
        self.update_state(state='Finding the face', meta={'progress': 50})
        mask = model.predict()

        ## masking the face
        self.update_state(state='Masking the face', meta={'progress': 90})
        img = cv2.imread(img_path)
        method = mask_request.get_masking_method_display().lower()
        if method == 'blurring':
            result = gaussian_blur(img, mask)

        elif method == 'mosaic':
            result = mosaic(img, mask)
        else:
            raise IOError
        ## Save testing image

        ######

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

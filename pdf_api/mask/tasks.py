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

        # # model = torch.load(MODEL_PATH, map_location=torch.device(DEVICE))
        # model = torch.hub.load('pytorch/vision:v0.6.0', 'deeplabv3_resnet101', pretrained=True)
        # model = model.eval()

        ## pre-processing the image
        self.update_state(state='Pre-processing the image', meta={'progress': 30})
        img_path = os.path.join(BASE_DIR, 'media', str(mask_request.image))
        model.load_image(img_path)
        model.preprocess_image()

        # original_img = cv2.imread(img_path)
        # img = original_img
        # print(img_path)
        # print(img.shape)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = torch.from_numpy(img).to(DEVICE)
        # img = Variable(img.float())
        # img = img.unsqueeze(0).permute((0, 3, 1, 2))

        ## finding the face
        self.update_state(state='Finding the face', meta={'progress': 50})
        mask = model.predict()

        # mask = model.predict(img)
        # mask = np.argmax(mask.squeeze().permute(1, 2, 0).cpu().numpy(), axis=2)
        # print(np.unique(mask))
        # # v = 255 // max(np.unique(mask)) if max(np.unique(mask)) != 0 else 255
        # v = 1
        # mask = np.stack((mask,) * 3, axis=-1) * v
        # ##
        # out_name = os.path.join(BASE_DIR, 'media', 'test', 'out.png')
        # if not os.path.exists(os.path.dirname(out_name)):
        #     os.makedirs(os.path.dirname(out_name))
        # cv2.imwrite(out_name, mask)
        # ##

        ## masking the face
        self.update_state(state='Masking the face', meta={'progress': 90})
        img = cv2.imread(img_path)
        method = mask_request.get_masking_method_display().lower()
        if method == 'blurring':
            result = gaussian_blur(img, mask)
            mosaic_result = mosaic(img, mask)
            test_mask = np.stack((mask,) * 3, axis=-1) * 128
            out_mask_name = os.path.join(BASE_DIR, 'media', 'test', 'mask.png')
            out_blur_name = os.path.join(BASE_DIR, 'media', 'test', 'blur.png')
            out_mosaic_name = os.path.join(BASE_DIR, 'media', 'test', 'mosaic.png')
            cv2.imwrite(out_mask_name, test_mask)
            cv2.imwrite(out_mosaic_name, mosaic_result)
            cv2.imwrite(out_blur_name, result)
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

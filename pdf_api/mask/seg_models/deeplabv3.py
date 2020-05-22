import os

import cv2
import torch
import numpy as np
from PIL import Image

from pdf_api.settings import BASE_DIR
from torchvision import transforms

from ..utils import gaussian_blur

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'deeplabv3_resnet101.pth')


class DeepLabV3(object):
    def __init__(self):
        self.img_path = None
        self.model = None
        self.image = None
        self.preprocess = None
        self.batch = None
        self.predictions = None
        self.r = None
        self.test_out = os.path.join(BASE_DIR, 'media', 'test')

    def load_model(self):
        self.model = torch.hub.load('pytorch/vision:v0.6.0', 'deeplabv3_resnet101', pretrained=True)
        # self.model = torch.load(MODEL_PATH, map_location=torch.device(DEVICE))
        self.model.eval()

    def preprocess_image(self, img_path):
        self.img_path = img_path
        image = cv2.imread(img_path)
        image = image[:, :, :3]
        self.image = Image.fromarray(image)
        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        self.tensor = self.preprocess(self.image)
        self.batch = self.tensor.unsqueeze(0)
        return self.batch

    def predict(self):
        self.batch.to(DEVICE)
        self.model.to(DEVICE)

        with torch.no_grad():
            output = self.model(self.batch)['out'][0]
        self.predictions = output.argmax(0)
        self.mask = self.predictions.cpu().numpy()
        self.mask = np.where(self.mask == 15, 1, 0)
        cv2.imwrite(os.path.join(self.test_out, 'mask.png'), self.mask)

        return self.mask

    def color_pallete(self, predictions=None):
        if predictions:
            self.predictions = predictions
        # create a color pallete,
        self.palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
        colors = torch.as_tensor([i for i in range(21)])[:, None] * self.palette
        colors = (colors % 255).numpy().astype("uint8")

        self.r = Image.fromarray(self.predictions.byte().cpu().numpy()).resize(self.image.size)
        self.r.putpalette(colors)
        # self.r.save(os.path.join(self.test_out, 'res.png'), np.asarray(self.r))

        return self.r

    def blur(self, image=None, mask=None):
        if image is not None:
            self.image = image
        if mask is not None:
            self.mask = mask

        self.out_img = gaussian_blur(self.image, self.mask)

        return self.out_img

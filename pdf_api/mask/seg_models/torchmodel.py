import os

import cv2
import torch
import numpy as np
from PIL import Image

from torchvision import transforms

from ..utils import gaussian_blur

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

models = ('deeplabv3_resnet101', 'fcn_resnet101')


class TorchModel(object):

    def __init__(self):
        self.nets = [self.load_model(model) for model in models]

        self.__frame = None
        self.__batch = None
        self.__mask = None
        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    @property
    def frame(self):
        return self.__frame

    @frame.setter
    def frame(self, frame):
        if isinstance(frame, str) is True:
            frame = cv2.imread(frame)
            frame = frame[:, :, :3]
            # frame = Image.fromarray(frame)
        self.__frame = frame

    @property
    def mask(self):
        return self.__mask

    def preprocess_image(self):

        tensor = self.preprocess(self.__frame)
        self.__batch = tensor.unsqueeze(0)

    def predict(self):
        batch = self.__batch
        masks = []
        for net in self.nets:
            net.to(DEVICE)
            batch.to(DEVICE)

            with torch.no_grad():
                output = net(batch)['out'][0]
            predictions = output.argmax(0)
            mask = predictions.cpu().numpy()
            mask = np.where(mask == 15, 1, 0)  # Person: 15
            masks.append(np.stack((mask,) * 3, axis=-1))

        self.__mask = np.logical_or(masks[0], masks[1])

    @staticmethod
    def load_model(model=None):
        model = 'deeplabv3_resnet101' if model is None else model
        model = torch.hub.load('pytorch/vision:v0.6.0', model, pretrained=True)
        model.eval()
        return model

import os
import sys

import cv2
import numpy as np
import torch
import segmentation_models_pytorch as smp
from torch.autograd import Variable

ROOT_DIR = os.path.abspath(os.path.join('..'))
sys.path.append(ROOT_DIR)

from flask import Flask, jsonify, make_response, send_file

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
# MODEL_PATH = os.path.join('models', 'celeba_mask_hq-psp-mobilenet_v2.pth')
MODEL_PATH = os.path.join('..', 'models', 'celeba_mask_hq-psp-densenet121.pth')

model = torch.load(MODEL_PATH, map_location=torch.device(DEVICE))

# print(model)
model.eval()

app = Flask(__name__)


def blur(img_path):
    test_img = cv2.imread(img_path)
    test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
    test_img = torch.from_numpy(test_img).to(DEVICE)
    test_img = Variable(test_img.float())
    test_img = test_img.unsqueeze(0).permute((0, 3, 1, 2))

    out_name = os.path.join('assets', 'test_out.png')
    out_img = model.predict(test_img)
    out_img = np.argmax(out_img.squeeze().permute(1, 2, 0).cpu().numpy(), axis=2) * 60
    cv2.imwrite(out_name, out_img)

    return out_name


# @app.route('/predict', methods=['POST'])
@app.route('/predict')
def predict():
    print('predicting...')
    img_path = os.path.join('assets', 'images.jpg')
    print('predicting ended.')
    return send_file(blur(img_path), mimetype='image/png')
    # return response
    # return jsonify({'class_id': test_img})


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=2080,
        debug=True)

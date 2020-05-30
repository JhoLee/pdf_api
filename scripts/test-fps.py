import os
import sys
import time
import argparse

import cv2
import numpy as np

from pdf_api.mask.seg_models.segmodel import SegModel

parser = argparse.ArgumentParser(description='..')

parser.add_argument('--model', requried=True, help='model')
parser.add_argument('--video', default='atrium_crop.mov', help='video')

args = parser.parse_args()
model_name = args.model
video_name = args.video

sys.path.append(os.getcwd())

cap = cv2.VideoCapture(video_name)
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Video loaded. Total frames:', length)
ret, frame = cap.read()
h, w = frame.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
mask_out = cv2.VideoWriter('test/{}-mask.mp4'.format(model_name), fourcc, 30, (w, h))
blur_out = cv2.VideoWriter('test/{}-blur.mp4'.format(model_name), fourcc, 30, (w, h))
mosaic_out = cv2.VideoWriter('test/{}-mosaic.mp4'.format(model_name), fourcc, 30, (w, h))

font = cv2.FONT_HERSHEY_SIMPLEX

net = SegModel()
net.load_model(model_name)
print('model', model_name, 'loaded.')

i = 0
time_start = []
time_read = []
time_preprocess = []
time_predict = []
time_draw_mask = []
time_draw_blur = []
time_draw_mosaic = []
time_total_mask = []
time_total_blur = []
time_total_mosaic = []
fps_mask = []
fps_blur = []
fps_mosaic = []

while cap.isOpened():
    t_start = time.time()

    ret, frame = cap.read()
    if ret:
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #         image = frame[..., ::-1]
        #         h, w = image.shape[:2]
        t_read = time.time()

        # Pre-process
        net.preprocess_image(frame)
        t_preprocess = time.time()

        # Predict
        mask = net.predict()
        t_predict = time.time()

        # Draw
        mask = np.stack((mask,) * 3, axis=-1).astype(np.uint8)

        ### GaussianBlur
        t_blur_start = time.time()
        rate = 127
        blur = cv2.GaussianBlur(frame, (rate, rate), 0)
        blur = np.where(mask, blur, frame)
        t_blur_end = time.time()
        ###

        ### Mosaic
        t_mosaic_start = time.time()
        rate = 25
        h, w, _ = frame.shape
        mosaic = cv2.resize(frame, (w // rate, h // rate))
        mosaic = cv2.resize(mosaic, (w, h), interpolation=cv2.INTER_AREA)
        mosaic = np.where(mask, mosaic, frame)
        t_mosaic_end = time.time()
        ###

        ### mask
        t_mask_start = time.time()
        mask = mask * 255
        t_mask_end = time.time()
        ###

        # Print runtime
        time_read.append(t_read - t_start)
        time_preprocess.append(t_preprocess - t_read)
        time_predict.append(t_predict - t_preprocess)

        time_draw_mask.append(t_mask_end - t_mask_start)
        time_draw_blur.append(t_blur_end - t_blur_start)
        time_draw_mosaic.append(t_mosaic_end - t_mosaic_start)

        time_total = (time_read[i] + time_preprocess[i] + time_predict[i])
        time_total_mask.append(time_total + time_draw_mask[i])
        time_total_blur.append(time_total + time_draw_blur[i])
        time_total_mosaic.append(time_total + time_draw_mosaic[i])
        fps_mask.append(1 / time_total_mask[i])
        fps_blur.append(1 / time_total_blur[i])
        fps_mosaic.append(1 / time_total_mosaic[i])

        print("[mask] {:03.1f}%; {:05d}; read: {:.3f} [s]; pre-process: {:.3f} [s]; predict: {:.3f} [s]; draw: {:.3f} "
              "[s]; total: {:.3f} [s]; fps: {:.2f} [Hz]".format(
            (i + 1) / length * 100, i + 1, time_read[i], time_preprocess[i], time_predict[i], time_draw_mask[i],
            time_total_mask[i], fps_mask[i]))
        sys.stdout.flush()
        print(
            "[blur] {:03.1f}%; {:05d}; read: {:.3f} [s]; pre-process: {:.3f} [s]; predict: {:.3f} [s]; draw: {:.3f} [s];"
            " total: {:.3f} [s]; fps: {:.2f} [Hz]".format(
                (i + 1) / length * 100, i + 1, time_read[i], time_preprocess[i], time_predict[i], time_draw_blur[i],
                time_total_blur[i], fps_blur[i]))
        sys.stdout.flush()
        print(
            "[mosa] {:03.1f}%; {:05d}; read: {:.3f} [s]; pre-process: {:.3f} [s]; predict: {:.3f} [s]; draw: {:.3f} [s];"
            " total: {:.3f} [s]; fps: {:.2f} [Hz]".format(
                (i + 1) / length * 100, i + 1, time_read[i], time_preprocess[i], time_predict[i], time_draw_mosaic[i],
                time_total_mosaic[i], fps_mosaic[i]))
        sys.stdout.flush()

        # mask
        y0, dy = 25, 25
        cv2.putText(mask, "{:04.2f} [fps]".format(fps_mask[i]), (y0, y0 + dy * 0), font, 0.75, (0, 255, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(mask, "model: {}".format(model_name), (y0, y0 + dy * 1), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(mask, "GPU: Geforce RTX 2070", (y0, y0 + dy * 2), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(mask, "CPU: Intel i5-9400F", (y0, y0 + dy * 3), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)

        # blur
        y0, dy = 25, 25
        cv2.putText(blur, "{:04.2f} [fps]".format(fps_blur[i]), (y0, y0 + dy * 0), font, 0.75, (0, 255, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(blur, "model: {}".format(model_name), (y0, y0 + dy * 1), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(blur, "GPU: Geforce RTX 2070", (y0, y0 + dy * 2), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(blur, "CPU: Intel i5-9400F", (y0, y0 + dy * 3), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)

        # mosaic
        y0, dy = 25, 25
        cv2.putText(mosaic, "{:04.2f} [fps]".format(fps_mosaic[i]), (y0, y0 + dy * 0), font, 0.75, (0, 255, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(mosaic, "model: {}".format(model_name), (y0, y0 + dy * 1), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(mosaic, "GPU: Geforce RTX 2070", (y0, y0 + dy * 2), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(mosaic, "CPU: Intel i5-9400F", (y0, y0 + dy * 3), font, 0.75, (0, 255, 0), 2, cv2.LINE_AA)

        mask_out.write(mask)
        blur_out.write(blur)
        mosaic_out.write(mosaic)
        i += 1
    else:
        break

    import csv

    with open('test/{}_result.csv'.format(model_name), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['frame', 'read', 'pre-process', 'inference', 'mask_draw', 'blur_draw', 'mosaic_draw', 'mask_total',
             'blur_total', 'mosaic_total', 'mask_fps', 'blur_fps', 'mosaic_fps'])

        for i in range(len(fps_mask)):
            writer.writerow([i + 1, time_read[i], time_preprocess[i], time_predict[i],
                             time_draw_mask[i], time_draw_blur[i], time_draw_mosaic[i],
                             time_total_mask[i], time_total_blur[i], time_total_mosaic[i],
                             fps_mask[i], fps_blur[i], fps_mosaic[i]])

cap.release()

import os.path
import shutil
import time

import cv2
from .packages.ultralytics import YL
from tools import *

"""
    pth: Segment Model path
    d_path: Detected images save path
    m_path: Masked images save path
    img_size: Model input image size
"""
pth = f"{os.getcwd()}/runs/v8mTS-train/weights/best.pt"
t = f"{os.getcwd()}/runs/tmp"
d_path = f"{os.getcwd()}/server/outputs/detect"
m_path = f"{os.getcwd()}/server/outputs/mask"
img_size = 1280


class Segment:
    def __init__(self, idx=7, source=None, results=None, ths=0):
        """
        Args:
            path    model path
            idx     gpu index
        """
        self.name = ths
        self.model_path = pth
        if not os.path.exists(self.model_path):
            raise ValueError(f"Invalid model path:{self.model_path}")
        self.model = self.load_model()
        if self.model is None:
            raise ValueError(f"Invalid model type.{self.model}")
        self.source = source
        self.idx = idx

        time.sleep(0.01)

        self.results = results

    def load_model(self):
        return YL(self.model_path)

    def inference(self, source):
        self.results = self.model.predict(source=f"{source}", conf=0.5, iou=0.75, imgsz=img_size, device=self.idx,
                                          show_boxes=True, show_labels=False, save_crop=False, save=True,
                                          save_txt=False, exist_ok=True,
                                          project=split_name(d_path)[0], name=split_name(d_path)[1])

        time.sleep(0.01)

    def output(self, source):
        pred = m_path

        if not os.path.exists(pred):
            os.makedirs(pred)

        for result in self.results:
            img_name = os.path.basename(result.path)
            if not source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                ori = f"{os.path.join(source, img_name)}"
            else:
                ori = f"{source}"

            save_path = os.path.join(pred, f"mask_{img_name}")
            if result.masks is not None and len(result.masks) > 0:
                box = result.boxes.xyxy.cpu().tolist()
                img = cv2.imread(ori)
                crop_img = img[int(box[0][1]): int(box[0][3]), int(box[0][0]): int(box[0][2])]
                # 获取原图尺寸
                height, width = crop_img.shape[:2]
                # 创建全黑背景图像，尺寸比原图大
                im = np.zeros((height + 2 * 25, width + 2 * 25, 3), dtype=np.uint8)
                # 计算原图粘贴到背景图的起始位置
                y_offset = 25
                x_offset = 25
                # 将原图粘贴到背景图上

                data = result.masks.data
                for idx, mk in enumerate(data):
                    mask = cv2.resize(mk.cpu().numpy() * 255, (img.shape[1], img.shape[0]),
                                      interpolation=cv2.INTER_AREA)

                    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
                    crop_mask = mask[int(box[0][1]): int(box[0][3]), int(box[0][0]): int(box[0][2])]
                    res = cv2.bitwise_and(crop_img, crop_img, mask=crop_mask.astype(np.uint8))
                    im[y_offset:y_offset + height, x_offset:x_offset + width] = res

                    if res is not None:
                        cv2.imwrite(save_path, im)
                    else:
                        print(f"\033[91m{os.path.splitext(img_name)[0]}.{img_name[-3:]} \033[0m is None! ")


def lml(x):
    model_list = []
    os.makedirs(f"{os.getcwd()}/data/tmp", exist_ok=True)
    d = f"{os.getcwd()}/data/initialize.jpg"
    for _ in tqdm(range(x), desc="Loading Models", bar_format="\033[91m{l_bar}{bar}{r_bar}\033[0m",
                  ncols=int(shutil.get_terminal_size().columns * 0.3)):
        m = Segment(ths=_)
        m.model.predict(d, device=7)
        model_list.append(m)
    return model_list


if __name__ == '__main__':
    ml = lml(16)

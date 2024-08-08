import os.path
import time
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import requests
import json
import base64
from PIL import Image
from io import BytesIO
import hashlib
from datetime import datetime
from tqdm import tqdm
import logging


def check_torch():
    try:
        import torch
        # 检查是否可以导入 torch
        print("PyTorch 已成功导入！")
        # 检查 PyTorch 版本
        print(f"PyTorch 版本: {torch.__version__}")

        # 检查是否有可用的 CUDA 设备
        if torch.cuda.is_available():
            print("CUDA 可用！")
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"可用的 GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"设备 {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("CUDA 不可用。")
    except ImportError:
        print("未能导入 PyTorch。请确保它已安装。")


def server(ip, port, img_path):
    md5 = hashlib.md5()
    md5.update('medcv_{}_tongueseg'.format(datetime.now().strftime("%Y%m%d")).encode('utf-8'))
    key = md5.hexdigest()

    url = f"http://{ip}:{port}/med_ai/tong_seg/?apikey={key}&version=1"

    # 构造请求数据
    def build_paras(path):
        with open(path, 'rb') as image_file:
            content = base64.b64encode(image_file.read())
        name = os.path.splitext(os.path.basename(path))[0]
        params = {"img": content, "imgname": name}
        return params, name

    # 发送请求
    def post(u, p):
        try:
            # 发送 POST 请求
            response = requests.post(u, data=p, timeout=100)
            # 检查响应状态码
            response.raise_for_status()
            # 解析 JSON 响应
            js = response.json()
            return js
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Response content: {response.content}')
        except requests.exceptions.RequestException as err:
            print(f'Other error occurred: {err}')
        except json.JSONDecodeError as json_err:
            print(f'JSON decoding error: {json_err}')
            print(f'Response content: {response.content}')

    # 检查返回并保存图像
    def check_save(response, img_name):
        if response:
            message = response["msg"]
            if message == "ok":
                img1 = Image.open(BytesIO(base64.b64decode(response["image1"])))
                img1.save(f"{os.getcwd()}/receive/{img_name}_detect.png", "PNG")

                img2 = Image.open(BytesIO(base64.b64decode(response["image2"])))
                img2.save(f"{os.getcwd()}/{img_name}_segment.png", "PNG")
            else:
                print("Error")
            return True
        else:
            print("Failed to get a valid response")
            return False

    # 处理流程
    def process(path):
        paras, name = build_paras(path)
        res = post(url, paras)
        return check_save(res, name)
    print(f"\033[91m::::::::::::::::   SERVER   ::::::::::::::::\033[0m")
    if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
        st = time.time()
        if process(img_path):
            ed = time.time()
            print(f"\033[91m{os.path.splitext(os.path.basename(img_path))[0]} \033[0mDone!"
                  f"Processing time is \033[91m{(ed - st):.2f} second\033[0m.")

        else:
            print("Error")

    else:
        ft = time.time()
        count = 0
        for f in os.listdir(img_path):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                count += 1
                st = time.time()
                if process(os.path.join(img_path, f)):
                    ed = time.time()
                    print(f"\033[91m{f} \033[0mDone! Processing time is \033[91m{(ed - st):.2f} second\033[0m.")
                else:
                    print(f"{f} Error")
            else:
                pass
        fe = time.time()

        print(f"Folder Done! Processing a total of \033[91m{count} files\033[0m. "
              f"The total time is \033[91m{(fe - ft):.2f} seconds\033[0m, "
              f"with an average time of \033[91m{((fe -ft) / count):.2f} second\033[0m.")


def local():
    pass


def test_tqdm():
    # 使用 tqdm 创建一个进度条，自定义 bar_format 参数来设置全部输出为绿色
    for i in tqdm(range(100),
                  bar_format='\033[92m{l_bar}{bar}{r_bar}\033[0m'):
        time.sleep(0.05)


class NullWriter:
    def write(self, arg):
        pass

    def flush(self):
        pass


def suppress_print(func):
    def wrapper(*args, **kwargs):
        # 保存当前的stdout和stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # 将stdout和stderr重定向到空设备
        sys.stdout = NullWriter()
        sys.stderr = NullWriter()

        # 记录当前日志记录器的级别
        logging.disable(logging.CRITICAL)

        try:
            result = func(*args, **kwargs)
        finally:
            # 恢复stdout和stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # 恢复日志记录器的级别
            logging.disable(logging.NOTSET)

        return result

    return wrapper


def txt_nms(path):
    for f in tqdm(os.listdir(path), desc="NMS Program Processing"):
        if f.lower().endswith('.txt'):
            with open(os.path.join(path, f), 'r') as fs:
                lines = fs.readline().split("\n")


def clean(path):
    for f in tqdm(os.listdir(path), desc="Scanning Images"):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            try:
                img = cv2.imread(os.path.join(path, f))
                if img is not None:
                    cv2.imwrite(os.path.join(path, f), img)
                else:
                    os.remove(os.path.join(path, f))
            except Exception as e:
                print(f"Error processing {path}: {e}")
    time.sleep(0.1)
    print(f"Found {len(os.listdir(path))} useful images")


def create_data(path):
    model = YOLO(f"{os.getcwd()}/runs/v8nTS-train/weights/best.pt")
    project = f"{os.getcwd()}/server/outputs"
    name = f"exp"
    # clean(path)
    for f in tqdm(os.listdir(path), desc="Inferencing"):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            res = suppress_print(model.predict)
            results = res(source=f"{os.path.join(path, f)}", conf=0.35,  iou=0.45, imgsz=2048,
                          device=7, show_boxes=True, show_labels=False, save_crop=False,
                          save=True, save_txt=True, exist_ok=True,
                          project=project, name=name)
    # txt_nms(f"{project}/{name}/labels")


def correct_labels(path):
    for txt in tqdm(os.listdir(path)):
        with open(os.path.join(path, txt), "r") as fs:
            lines = fs.readline().strip()
        correct_lines = "0" + lines[1:]
        with open(os.path.join(path, txt), "w") as fs:
            fs.write(correct_lines)


def split_name(path):
    name = str(path).split("/")[-1]
    return path.replace(f"/{name}", ""), name



if __name__ == "__main__":
    # create_data(r"/data/lizr/dataMy/tmp")
    # server("192.168.0.10", "8000", "/data/lizr/TSLZ/data/initialize.jpg")
    # local()
    #test_tqdm()
    # correct_labels(r"/data/lizr/dataMy/labels/train")
    split_name(f"{os.getcwd()}/dataMy/labels/train")


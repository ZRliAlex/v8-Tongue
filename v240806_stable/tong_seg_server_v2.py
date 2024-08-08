# -*-coding=utf-8 -*-
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
import segment
from segment import Segment
import os.path
import base64
import os
import traceback
from io import BytesIO
import tornado
import tornado.ioloop
import uvicorn
from tornado.ioloop import PeriodicCallback
import tornado.web
from tornado.escape import json_encode
from PIL import Image
from base64 import b64encode
import importlib
import sys
import time
from datetime import datetime
import hashlib
import numpy as np
import concurrent.futures
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor


importlib.reload(sys)
columns = shutil.get_terminal_size().columns * 0.5


def online_server(port, ths_num):
    server = ImageServer(port, None, ths_num)
    server.process()


class ImageServer(object):
    th = 0

    def __init__(self, port, server_address, ths_num):
        print("\33[91m ::::::::::     🐅 SEGMENT SERVER START 🐅     ::::::::::\33[0m".center(int(columns)))

        self.port = port
        self.address = server_address
        # 多线程
        self.models = segment.lml(ths_num)
        print(f"\33[91m----------****   🐅Model has been loaded🐅   ***----------\33[0m".center(int(columns)))

    def process(self):
        app = tornado.web.Application([(r"/med_ai/tong_seg/?", Handler, dict(models=self.models))], )
        app.listen(self.port, address=self.address)
        tornado.ioloop.IOLoop.current().start()


def url_key():
    current_date = datetime.now()
    ymd = current_date.strftime("%Y%m%d")
    apikey = 'medcv_{}_tongueseg'.format(ymd)
    md5 = hashlib.md5()
    md5.update(apikey.encode('utf-8'))
    apikey = md5.hexdigest()
    return apikey


def clear_directory(folder_path):
    try:
        # Ensure the folder exists
        if os.path.exists(folder_path):
            # Iterate over all the files and folders in the directory
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    # Check if it's a file or directory
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove directory
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            print(f"The directory {folder_path} does not exist.")
    except Exception as e:
        print(f"Failed to clear directory {folder_path}. Reason: {e}")


class Handler(tornado.web.RequestHandler):
    ml: list
    executor = ThreadPoolExecutor(max_workers=1)

    def initialize(self, models):
        self.ml = models
        d = Path(f"{os.getcwd()}/uploads/tmp")
        if not os.path.exists(f"{os.getcwd()}/uploads/tmp"):
            d.mkdir(parents=True, exist_ok=True)

    @run_on_executor
    def content_process(self):
        """
        """
        # Decode
        result = {}
        ft = time.time()
        if self.get_argument('apikey') == url_key():
            content = base64.b64decode(self.request.arguments.get("img", [None])[0])
            if content is None:
                result["msg"] = "no image content"
            im_name = self.get_name()
            # Information
            print(f"\33[91mTime:{datetime.now().year}-{datetime.now().month:02}-{datetime.now().day:02} "
                  f"{datetime.now().hour:02}:{datetime.now().minute:02}:{datetime.now().second:02}"
                  f" Received {im_name}\33[0m")
            # Check
            im = Image.open(BytesIO(content))
            im_np = np.array(im)
            if im_np.shape[2] == 3:  # 检查是否为彩色图像
                im_np = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"{os.getcwd()}/uploads/tmp/{im_name}", im_np)
            time.sleep(0.01)
            ImageServer.th = (ImageServer.th + 1) % len(self.ml)

            try:
                self.ml[ImageServer.th].inference(f"{os.getcwd()}/uploads/tmp/{im_name}")
                self.ml[ImageServer.th].output(f"{os.getcwd()}/uploads/tmp/{im_name}")
                im1 = Image.open(f"{os.getcwd()}/server/outputs/detect/detect_{im_name}")
                im2 = Image.open(f"{os.getcwd()}/server/outputs/mask/mask_{im_name}")
                by1 = BytesIO()
                im1.save(by1, "JPEG")
                result["image1"] = b64encode(by1.getvalue()).decode('utf-8')

                by2 = BytesIO()
                im2.save(by2, "JPEG")
                result["image2"] = b64encode(by2.getvalue()).decode('utf-8')

                result["msg"] = "ok"
            except Exception as e:
                print(traceback.format_exc())
                result["image1"] = str(e)
                result["image2"] = str(e)
                result["msg"] = str(e)
            # Response
            fe = time.time()
            print(f" \033[92mModel_{ImageServer.th}\033[0m processed  \033[92m{im_name} \033[0m"
                  f"with \033[92m{(fe - ft):.2f} seconds\033[0m.")
        else:
            result['msg'] = 'apikey is wrong!'
            # Response

        self.write(json_encode(result))

    async def post(self):
        # Process
        await self.content_process()

    def get_name(self):
        im_name = self.request.arguments.get("imgname", [None])[0].decode('utf-8')
        if isinstance(im_name, str):
            for char in ["b", "'", "[", "]"]:
                im_name = im_name.replace(char, "")
        if isinstance(im_name, list):
            im_name = im_name[0]
            if isinstance(im_name, (bytes, bytearray)):
                im_name = im_name.decode('utf-8')
        if not im_name.endswith((".jpg", ".png", ".jpeg")):
            im_name += ".jpg"
        return im_name


def start_periodic_cleanup(directory, interval):
    def cleanup():
        clear_directory(directory)
        print(f"\33[91mDirectory {directory} has been cleaned up.\33[0m")
    # ms = hour * min * s * 1000
    interval = interval * 3600 * 1000
    periodic_callback = PeriodicCallback(cleanup, interval)
    periodic_callback.start()


if __name__ == "__main__":

    start_periodic_cleanup(f"{os.getcwd()}/uploads/tmp/", 48)
    online_server("18041", 1)

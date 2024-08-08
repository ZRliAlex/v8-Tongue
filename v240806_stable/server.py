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
importlib.reload(sys)


def c_app():
    a = FastAPI(
        title="🐅 SEGMENT API",
        version=segment.__version__
    )
    ud, od = check_dir()
    print("\33[91m🐅 TONGUE SEGMENT SERVER STARTED\33[0m")
    return a, ud, od


def check_dir():
    ud = Path("uploads")
    od = Path("outputs")
    if not os.path.exists("/data/lizr/TSLZ/server/uploads"):
        ud.mkdir(parents=True, exist_ok=True)
    if not os.path.exists("/data/lizr/TSLZ/server/outputs"):
        od.mkdir(parents=True, exist_ok=True)
    return ud, od


def unicorn_server(host, port):
    app, upload_dir, output_dir = c_app()
    model = Segment("/data/lizr/TSLZ/runs/v8nTS-train/weights/best.pt")

    @app.post(f"/uploadfile/")
    async def upload_file(file: UploadFile = File(...)):
        file_location = os.path.join("/data/lizr/TSLZ/uploads", file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        # Process the image and create two output images
        model.inference(file_location)
        model.output(file_location)
        detect_file = f"detect_{file.filename}"
        mask_file = f"mask_{file.filename}"

        return {"file1": str(detect_file), "file2": str(mask_file)}

    @app.get("/downloadfile/{filename}")
    async def download_file(filename: str):

        if "detect" in filename:
            file_path = "/data/lizr/TSLZ/server" / output_dir / "detect" / filename
        else:
            file_path = "/data/lizr/TSLZ/server" / output_dir / "mask" / filename
        print(file_path)
        if file_path.exists():
            return FileResponse(file_path)
        return {"error": "File not found"}

    uvicorn.run(app, host=host, port=port)


def online_server(port):
    server = ImageServer(port, None)
    server.process()


class ImageServer(object):
    def __init__(self, port, server_address):
        print("\33[91m ::::::::::     🐅 SEGMENT SERVER START 🐅     ::::::::::\33[0m")

        self.port = port
        self.address = server_address
        self.model = segment.Segment()

    def process(self):
        app = tornado.web.Application([(r"/med_ai/tong_seg/?", Handler, dict(model=self.model))], )
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
    model: Segment

    def initialize(self, model: segment.Segment):
        self.model = model
        d = Path(f"{os.getcwd()}/uploads/tmp")
        if not os.path.exists(f"{os.getcwd()}/uploads/tmp"):
            d.mkdir(parents=True, exist_ok=True)

    def post(self):
        result = {}
        if self.get_argument('apikey') == url_key():
            # Decode
            content = base64.b64decode(self.request.arguments.get("img", [None])[0])
            if content is None:
                result["msg"] = "no image content"
            im_name = self.request.arguments.get("imgname", [None])[0].decode('utf-8')
            if isinstance(im_name, (bytes, bytearray)):
                im_name = im_name.decode('utf-8')
            if not im_name.endswith((".jpg", ".png", ".jpeg")):
                im_name += ".jpg"
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
            # Process
            ft = time.time()
            byte_array1, byte_array2, msg = self.content_process(im_name)
            result["image1"] = byte_array1
            result["image2"] = byte_array2
            result["msg"] = msg
            fe = time.time()
            print(f"Processed with \033[92m{(fe - ft):.2f} seconds\033[0m.")
        else:
            result['msg'] = 'apikey is wrong!'
        # Response
        self.write(json_encode(result))

    def content_process(self, name):
        """
        根据image_content进行相应操作
        :param name: 图片名称
        """
        time.sleep(1)
        try:
            self.model.inference(f"{os.getcwd()}/uploads/tmp/{name}")
            self.model.output(f"{os.getcwd()}/uploads/tmp/{name}")

            im1 = Image.open(f"{os.getcwd()}/server/outputs/detect/detect_{name}")
            im2 = Image.open(f"{os.getcwd()}/server/outputs/mask/mask_{name}")
            by1 = BytesIO()
            im1.save(by1, "JPEG")
            by1 = b64encode(by1.getvalue()).decode('utf-8')

            by2 = BytesIO()
            im2.save(by2, "JPEG")
            by2 = b64encode(by2.getvalue()).decode('utf-8')

        except Exception as e:
            print(traceback.format_exc())
            return str(e), str(e), str(e)

        return by1, by2, "ok"


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
    online_server("18501")

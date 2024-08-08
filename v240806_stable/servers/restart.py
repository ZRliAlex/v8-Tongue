import subprocess
# -*-coding=utf-8 -*-
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
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
import shutil
import numpy as np
importlib.reload(sys)
columns = shutil.get_terminal_size().columns

face_dia_server = "/home/medcv/face/face_dia_server/start.sh"
tong_dia_server = "/home/medcv/tongue/ton_dia_server/start.sh"
tong_seg_server = "/home/medcv/tongue/tongue_server_v8s_24_06_25/start.sh"


def restart(pth):
    subprocess.Popen(["sh", f"{pth}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    servers = [face_dia_server, tong_dia_server, tong_seg_server]
    idx = int(sys.argv[1])
    restart(servers[idx])

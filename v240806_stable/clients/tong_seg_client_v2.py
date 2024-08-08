#!/usr/bin/python
# -*-coding=utf-8 -*-
import os
import json
import urllib
import requests
import pickle
import time
import urllib.request
from PIL import Image
from io import BytesIO
from base64 import b64decode, b64encode
from datetime import datetime
import hashlib


def post(server_url, params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    request = urllib.request.Request(server_url, data)
    return json.loads(urllib.request.urlopen(request, timeout=100).read())


def process_image(server_url, file_path):
    import time
    start_time = time.time()
    image_filename = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, 'rb') as file:
        content = b64encode(file.read())

    params = {"img": content, "imgname": image_filename}
    json_return = post(server_url, params)
    # print(json_return)
    end_time = time.time()
    print(f'end_time - start_time = {end_time - start_time}')
    msg = json_return['msg']
    print(msg)
    image1_bytes = b64decode(json_return["image1"])
    image1 = Image.open(BytesIO(image1_bytes))
   # image1_path = f"/home/medcv/luli/Tongue/TongueSAM_Server/clientReceive/Receive1/{image_filename}.png"
   # image1.save(image1_path, "PNG")

    image2_bytes = b64decode(json_return["image2"])
    image2 = Image.open(BytesIO(image2_bytes))
    #image2_path = f"/home/medcv/luli/Tongue/TongueSAM_Server/clientReceive/Receive2/{image_filename}.png"
   # image2.save(image2_path, "PNG")
    print("process ending!")


def process_folder(server_url, folder_path):
    num = 0
    start_time = time.time()
    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg')):
            num = num + 1
            file_path = os.path.join(folder_path, file_name)
            process_image(server_url, file_path)

    print("The total time is {:.3f} seconds processing all images !".format(time.time() - start_time))
    print("Image num is {}, the average time of per image is {:.3f} seconds.".format(num,
                                                                                     (time.time() - start_time) / num))
    print("Processing all images in the folder completed!")


def local_image(server_url, path):
    """
    本地图片处理
    :param server_url: 服务器端HTTP服务URL
    :param path: 图片本地地址或文件夹路径
    """

    if os.path.isfile(path):
        process_image(server_url, path)
        print("processing one image ending!")
    elif os.path.isdir(path):
        process_folder(server_url, path)
    else:
        print(f"Invalid path:{path}")


def get_url(ip, port):
    current_date = datetime.now()
    yearMonDay = current_date.strftime("%Y%m%d")
    apikey = 'medcv_{}_tongueseg'.format(yearMonDay)
    md5 = hashlib.md5()
    md5.update(apikey.encode('utf-8'))
    md5_hash_value = md5.hexdigest()
    url = 'http://{0}:{1}/med_ai/tong_seg/?apikey={2}&version=1'.format(ip, port, md5_hash_value)
    return url


if __name__ == "__main__":
    url = get_url('192.168.0.10', '18041')
    path = "/home/medcv/tongue/tongue_server_v8s_24_06_25/uploads/tmp"  # 或者是文件夹路径
    local_image(url, path)

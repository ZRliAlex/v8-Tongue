import json
import urllib
import urllib.request
from base64 import b64encode, b64decode
import time
from datetime import datetime
import hashlib


def get_url(ip, port):
    current_date = datetime.now()
    yearMonDay = current_date.strftime("%Y%m%d")
    apikey = "medcv_{}_tonguedia".format(yearMonDay)
    md5 = hashlib.md5()
    md5.update(apikey.encode('utf-8'))
    md5_hash_value = md5.hexdigest()
    url = "http://{0}:{1}/med_ai/tong_dia/?apikey={2}&version=1".format(ip, port, md5_hash_value)
    # url = "http://{0}:{1}/med_ai/tong_seg/?apikey={2}&version=1".format(ip, port, md5_hash_value)
    return url


def post(server_url, params)->dict:
    data = urllib.parse.urlencode(params).encode('utf-8')
    request = urllib.request.Request(server_url, data)
    return json.loads(urllib.request.urlopen(request, timeout=100).read())

import io
from PIL import Image

def getHist(json_return, lab=False):
    rgb_hist_str = json_return["color_hist"][0]["RGB_hist"] if not lab else json_return["color_hist"][0]["LAB_hist"]
    print(rgb_hist_str)
    img_str = b64decode(rgb_hist_str)
    img = Image.open(io.BytesIO(img_str))
    # img.save("./output.png")
    return img

def local_image(server_url, image_path):

    with open(image_path, "rb") as r_file:
        content = b64encode(r_file.read())
    # print(content)
    params = {"img": content,
              "imgname":"testImg"}
    start = time.time()
    json_return = post(server_url, params)
    print(json_return.keys())
    for i in ['tong_dia', 'tong_color', 'tong_shape', 'tong_color2', 'color_space']:
        print(json_return.get(i))
    print(json_return['msg'])
    end = time.time()
    print("using time:{:.3f}".format(end-start))


import os
def get_all_images(directory):
    image_files = []

    # 递归获取所有图片文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(os.path.join(root, file))

    return image_files

if __name__ == "__main__":
    url = get_url("192.168.0.10", "18070")
    im = f"{os.getcwd()}/verification/tong_dia.jpg"
    dir_path = f"{os.getcwd()}/tmp"
    local_image(url, im)
    # 暴力测试
    #for file_path in get_all_images(dir_path):
    #    local_image(url, file_path)

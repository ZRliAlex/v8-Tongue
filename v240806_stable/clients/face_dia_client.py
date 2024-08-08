import json
import urllib
import urllib.request
from base64 import b64encode
import time
from datetime import datetime
import hashlib
import cv2
import numpy as np
import os
from PIL import Image


def get_url(ip, port):
    current_date = datetime.now()
    yearMonDay = current_date.strftime("%Y%m%d")
    apikey = "medcv_{}_facedia".format(yearMonDay)
    md5 = hashlib.md5()
    md5.update(apikey.encode('utf-8'))
    md5_hash_value = md5.hexdigest()
    url = "http://{0}:{1}/med_ai/face_dia/?apikey={2}&version=1".format(
        ip, port, md5_hash_value)
    return url


def post(server_url, params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    request = urllib.request.Request(server_url, data)
    return json.loads(urllib.request.urlopen(request, timeout=1000).read())


def local_image(server_url, image_path):
    with open(image_path, "rb") as r_file:
        content = b64encode(r_file.read())
    params = {"img": content,
              "imgname": "testImg"}
    start = time.time()
    json_return = post(server_url, params)
    
    '''
    with open('json_return.txt',mode='a',encoding='utf-8') as f:
        f.write(str(json_return)+'\n\n')
    '''
    end = time.time()
    print("using time: {:.3f}".format(end-start))
    if json_return['msg'] == 'ok':
        print(json_return['RGB Space distance'])
        return 1, json_return['face_dia']
    else:
        print(json_return['msg'])
        return 0, 'error'

def convert_label(label):
    if label=='black':
        return '面色发黑'
    elif label=='white':
        return '面色发白'
    elif label=='green':
        return '面色发青'
    elif label=='yellow':
        return '面色发黄'
    elif label=='red':
        return '面色发红'
    elif label=='normal':
        return '面色正常'


if __name__ == "__main__":
    url = get_url("192.168.0.10", "18070")
    im = f"{os.getcwd()}/verification/face_dia.jpg"
    dir_path = f"{os.getcwd()}/tmp"
    image_name = im[im.rfind("/"):]
    true_label = image_name[len('image_'):].split(' ')[0]
    true_count = 1
    flag, pred_label = local_image(url, im)
    successful_count = 0
    accurate_count = 0
    if flag:
        successful_count = 1
        if pred_label == convert_label(true_label):
            accurate_count = 1
    print(f'本次共测试{true_count}张人脸图片，其中成功处理图片共{successful_count}张，面色分类预测正确图片共{accurate_count}张。')

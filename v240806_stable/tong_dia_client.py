import json
import urllib
import urllib.request
from base64 import b64encode, b64decode
import time
from datetime import datetime
import hashlib
import openpyxl
import os
import io
from PIL import Image


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
              "imgname": "testImg"}
    start = time.time()
    json_return = post(server_url, params)
    # print(json_return.keys())
    # for i in ['tong_dia', 'tong_color', 'tong_shape', 'tong_color2', 'color_space']:
        # print(json_return.get(i))
    # print(json_return['msg'])
    # end = time.time()
    #print("using time:{:.3f}".format(end-start))
    return json_return



def get_all_images(directory):
    image_files = []

    # 递归获取所有图片文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(os.path.join(root, file))

    return image_files


def process_xlsx(js, keys):
    processed_data = []
    for key in keys[1:]:
        value = js.get(key, "")
        if isinstance(value, list):
            for item in value:
                if len(item) == 2:
                    # 将列表转换为字符串格式
                    value = ', '.join(f"{item.get('name')}: {item.get('pv')}" for item in value)
                    processed_data.append(value)
                if len(item) == 8:
                    k = ["RGB_Space_mean", "RGB_Space_std", "RGB_Space_distance", "RGB_Space_KS-p",
                         "LAB_Space_mean", "LAB_Space_std", "LAB_Space_distance", "LAB_Space_KS-p"]
                    processed_data.extend([f"{key}: {item.get(key)}" for key in k])

    return processed_data


if __name__ == "__main__":
    # 创建一个新的Excel工作簿
    workbook = openpyxl.Workbook()
    # 获取活动的工作表并设置名称
    sheet = workbook.active
    sheet.title = "舌诊服务模块测试结果"
    # 定义表头
    keys = ['文件名', 'tong_dia', 'tong_color', 'tong_shape', 'tong_color2', 'color_space']
    # 写入表头到第一行
    sheet.append(keys)
    # 获取URL
    url = get_url("192.168.0.10", "18070")
    # 定义图片路径
    path = r"C:\Users\lzero\Desktop\TSLZ\tongue-server-v8s-24-06-25\data\test_240805"
    # 遍历文件夹中的所有文件
    for filename in os.listdir(path):
        sheet.append([filename] + process_xlsx(local_image(url, os.path.join(path, filename)), keys))

    # 保存工作簿
    workbook.save("舌诊服务模块测试结果.xlsx")
    print("Excel文件已成功生成并保存！")

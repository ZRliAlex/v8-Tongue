import requests
import time
import hashlib
from datetime import datetime
import urllib
import json 
import random

def get_md5(value):
    md5 = hashlib.md5()
    md5.update(value.encode('utf-8'))
    return md5.hexdigest()

url = "http://localhost:18070/med_ai/tcm_disease/"
current_date = datetime.now().strftime("%Y%m%d")
apikey = get_md5("mednlp_" + current_date + "_tcmdisease")


url += f"?apikey={apikey}&version=1"
# for i in range(100):
count = 0
with open('//home/medcv/monitor/verification/zycf_server_all_single_currentill.json', 'r', encoding='utf-8') as f:
    read_data = json.load(f)

    for i in range(1):
        input_data = read_data[random.randint(0, 10158)]

        start_time = time.time()

        try:
            # response = requests.post(url, json=input_data)
            data = urllib.parse.urlencode(input_data).encode('utf-8')
            request = urllib.request.Request(url, data)
            result = json.loads(urllib.request.urlopen(request, timeout=100).read())
            if result:
                print(result)
                ...
            else:
                print(f"Error")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        count += 1
        end_time = time.time()
        # break
        print(f"第{count}条有using time: ", end_time - start_time)




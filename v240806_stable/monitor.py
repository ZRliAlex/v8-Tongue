import os.path
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
import importlib
import sys
import time
from datetime import datetime
import logging
import shutil
import re
importlib.reload(sys)
columns = shutil.get_terminal_size().columns
# 配置logging模块
logging.basicConfig(filename='monitor_info.log', level=logging.INFO,  format='%(message)s')


def monitor(interval):

    def check(index, clients_list):
        lg = f"\33[91m{current()}\33[0m"
        save_log(lg)
        client = clients_list[index]
        status, details = check_servers(client)
        if status == "normal":
            lg = (f"\33[92m{client[10:].replace("_client.py", " server")}\33[0m "
                  f"has been checked.Status:\33[92m{status}\33[0m")
            save_log(lg)
            if details:
                lg = f"\33[92m{details[0]}\33[0m"
                save_log(lg)
            return False, details

        else:
            lg = (f"\33[91m{client[10:].replace("_client.py", " server")}\33[0m "
                  f"has been checked.Status:\33[91m{status}\33[0m")
            save_log(lg)
            if details:
                lg = f"\33[91m{details[0]}\33[0m"
                save_log(lg)
            return True, details

    def check_servers(pth):
        o = []
        try:
            res = subprocess.Popen([py, pth], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = res.communicate()
            if out == "":
                o.append(err)
                return "error", o

            else:
                if err == "":
                    o.append(out)
                    return "normal", o
                o.append(err)
                return "error", o
        except subprocess.CalledProcessError as e:
            return "error", e
        except FileNotFoundError as e:
            return "error", e
        except Exception as e:
            return "error", e

    def add_top(file, con):
        with open(file, 'r') as tfs:
            c = tfs.read()
        n = con + "\n" + c
        with open(file, 'w', encoding='utf-8') as tfs:
            tfs.write(n)

    # capture top
    def top_capture():
        # 使用 top 命令获取一次系统状态的输出
        command = ['top', '-b', '-n', '1']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return process.communicate()

    def save_clear(inter, st_time, file):
        if time.time() - st_time >= inter:
            with open(file.replace(file[-8:], f"epo{file[-4:]}"), "w") as f:
                with open(file, "r") as fs:
                    data = fs.read()
                    f.write(data)
            with open(file, "w") as f:
                f.truncate(0)
            st_time = time.time()
        return st_time
    print("\n\n")
    eg = "\33[91m ::::::::::     🐅 Server Monitor Start 🐅     ::::::::::\33[0m".center(columns)
    save_log(eg)
    time.sleep(1)
    idx = 0
    py = r"/home/medcv/miniconda3/envs/torch/bin/python"
    clients = ["./clients/face_dia_client.py", "./clients/tong_dia_client.py", "./clients/tong_seg_client.py",
               "./clients/llama2_dis_client.py", "./clients/llama2_drug_client.py", "./clients/llama2_syn_client.py"]
    errs = [0, 0, 0, 0, 0, 0]
    clr = time.time()
    ct = time.time()

    while True:
        st = time.time()                    # 本次循环开始时间
        idx = idx % 6                       # 本次循环测试的客户端索引值
        ers, deta = check(idx, clients)     # 使用客户端代码检查服务器运行状态，ers为错误信息，deta为运行时输出
        if ers:
            errs[idx] += 1                  # 测试服务器出现错误，计数增加
        else:
            if errs[idx] != 0:              # 测试服务器上次出现错误，本次正常运行，将错误计数归零
                errs[idx] = 0

        if errs[idx] == 1 and idx <= 2:      # 测试服务器第一次出现错误，并且为CV模型，尝试重启
            eg = (f"\33[91m{clients[idx][10:].replace("_client.py", " server")}故障 "
                  f"{current()} 正在尝试重启！")
            save_log(eg)
            subprocess.run([py, "/home/medcv/monitor/servers/restart.py"] + [f"{idx}"])

        if errs[idx] > 1:                                           # 测试服务器出现错误超过两次，通知管理员
            s_email(clients[idx][10:].replace("_client.py", ""), deta[0])

        while time.time() - st <= interval:                                 # 等待间隔
            output, _ = top_capture()                                       # 每秒获取top信息
            add_top("top_info.txt", output)                             # 保存top信息
            ct = save_clear(60, ct, r"./top_info.txt")              # 清理top信息,间隔为1分钟
            clr = save_clear(3600, clr, r"./monitor_info.log")      # 清理log信息，间隔为1小时
            time.sleep(1)
        idx += 1                                # 单个服务器测试结束


def s_email(ser, content):
    # 配置发送邮件的基本信息
    sender_email = "yk_med@163.com"
    receiver_email = "zhouchangwei@uhealthtech.cn"
    cc_email = ["lizhaorong@uhealthtech.cn", "tangxiaoming@uhealthtech.cn"]
    subject = f"Server Errors - {current()}"

    # 错误内容
    html_content = f"""
    <html>
    <head>
        <style>
            .code {{
                background-color: #1E1E1E;
                color: #FF6B6B; /* 红色 */
                padding: 10px;
                border-radius: 5px;
                font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.5;
                overflow-x: auto; /* 允许水平滚动 */
                word-wrap: break-word; /* 自动换行 */
                white-space: pre-wrap; /* 保留空格和换行符 */
            }}
            .code pre {{
                margin: 0;
                color: #FF6B6B; /* 红色 */
                font-weight: bold;
            }}
            .code .error {{
                color: #FF6B6B; /* 红色 */
                font-weight: bold;
            }}

        </style>
    </head>
    <body>
        <h2 style="color: #4CAF50;">服务器故障</h2>
        <h3>亲爱的管理员，</h3>
        <h3><span style="color: #FF6B6B;">{ser} 服务器</span>出现故障，请您及时处理，故障代码如下：</h3>
        <pre class="code">
{content}
        </pre>

        <h3>祝好！</h3>
        <h3>益康服务器</h3>
    </body>
    </html>
    """

    # 创建一个MIMEMultipart对象
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Cc"] = ",".join(cc_email)
    message["Subject"] = subject

    # 将邮件内容附加到MIMEMultipart对象中
    part = MIMEText(html_content, "html")
    message.attach(part)

    # 添加附件
    # log_epo = r"./monitor_epo.log"
    log_info = r"./monitor_info.log"
    if os.path.exists(log_info):
        with open(log_info, "rb") as at:
            p = MIMEBase("application", "octet-stream")
            p.set_payload(at.read())
            encoders.encode_base64(p)
            p.add_header("Content-Disposition",
                         f"attachment; filename= {log_info[2:]}")
            message.attach(p)
    # 配置SMTP服务器的信息
    smtp_server = "smtp.163.com"
    """
        使用SSL/TLS：465
        通用端口：587
        """
    smtp_port = 465

    smtp_username = "yk_med@163.com"
    # 授权码
    smtp_password = "PERYLYHANTOAWCGP"

    # 连接SMTP服务器
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, [receiver_email] + cc_email, message.as_string())

    lg = f"\33[91m{ser}故障 {current()} 已成功发送邮件通知管理员！"
    save_log(lg)


def current():
    t = (f"Time:{datetime.now().year}-{datetime.now().month:02}-{datetime.now().day:02} "
         f"{datetime.now().hour:02}:{datetime.now().minute:02}:{datetime.now().second:02}")
    return t


def save_log(log):
    print(log)
    logging.info(re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub("", log))


if __name__ == '__main__':
    monitor(100)



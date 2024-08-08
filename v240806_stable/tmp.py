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


def s_email(ser, content):
    # 配置发送邮件的基本信息
    sender_email = "yk_med@163.com"
    receiver_email = "lizhaorong@uhealthtech.cn"
    cc_email = ["lizhaorong@uhealthtech.cn", "lizhaorong@uhealthtech.cn"]
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


s_email("ashkjahsdk", "sakdhashfiuhfoisgdhfoijasgflajsdgflkjsadgflkjsgfhlsdflkjsgflsdgfjskgfljksdgflskjgfsjhd"
                      "sgdlkjgfjksdgfjksgkjsgfkjdsgfjsdgfjhdsgfjshdgfjkhsdgfjkhsdgfhjsdgfhjsdgfhjsdgfhsdgfhsjdfghjdsgfhjsd"
                      "sdgfjhdsgfjhsdgfhjsgfhjgfhjsdgfhjsdgfhjsdgfhjsdgfhsgdhjfgsdhjfgsdhjgfsdjhgfjhsdgfjhsgdfjhkgsjhdkf"
                      "shfds,fhksdhfkjsdhfkjsdhfkjsdhfkjsdhfjksdhfjksdhfkjsdhfjkshdjkfhsdkjfhskdljfhlkjsdfhkljsdhfjklsdhj"
                      "hpiuSGHIDSHGFIOUJhfiOSDHFIOHSIOHFSDIHFIJSHISDHFISHDFUISHFIJUSDHBFIUSHFIUSDHFKJLSDHFIUSFUISHUSIDOHF")
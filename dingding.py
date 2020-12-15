#!/usr/bin/env python
# coding:utf-8
# zabbix钉钉报警
import hashlib, base64, urllib, hmac, requests, json, sys, os, datetime, time
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import getopt

LOG_DIR = '/tmp'
LOG_FILE = 'dingding.log'
LOG_LEVEL = "INFO"

log_level = getattr(logging, LOG_LEVEL)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, 750)
RecodeLog = logging.getLogger("LOG INFO")
RecodeLog.setLevel(log_level)
# 建立一个filehandler来把日志记录在文件里，级别为debug以上
# 按天分割日志,保留30天
if not RecodeLog.handlers:
    fh = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE), when='D', interval=1, backupCount=30
    )
    ch = logging.StreamHandler()
    fh.setLevel(log_level)
    ch.setLevel(log_level)
    # 设置日志格式
    if LOG_LEVEL == "DEBUG":
        formatter = logging.Formatter(
            "%(asctime)s - Message of File(文件): \
            %(filename)s,Module(类):%(module)s,FuncName(函数):%(funcName)s ,\
            LineNo(行数):%(lineno)d - %(levelname)s - %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # 将相应的handler添加在logger对象中
    RecodeLog.addHandler(fh)
    RecodeLog.addHandler(ch)


def send_webhook(token, secret, subject, message):
    """
    :param token:
    :param secret:
    :param subject:
    :param message:
    :return:
    """
    webhook = "https://oapi.dingtalk.com/robot/send?access_token={0}".format(token)  # 说明：这里改为自己创建的机器人的webhook的值
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "NCCC正线环境报警：{0}".format(subject),
            "text": message
        },
        "at": {
            "isAtAll": True
        }
    }
    headers = {'Content-Type': 'application/json'}
    timestamp = long(round(time.time() * 1000))
    secret_enc = bytes(secret).encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.quote_plus(base64.b64encode(hmac_code))
    url = "{0}&timestamp={1}&sign={2}".format(webhook, timestamp, sign)
    x = requests.post(url=url, data=json.dumps(data), headers=headers)
    if x.json()["errcode"] == 0:
        RecodeLog.info("{0} 发送成功:{1},SendStatus:{2}".format(datetime.datetime.now(), message, x.content))
    else:
        RecodeLog.error("{0} 发送失败:{1},SendStatus:{2}".format(datetime.datetime.now(), message, x.content))


def useage():
    print("%s -h\t#帮助文档" % sys.argv[0])
    print("%s -s 钉钉秘钥 -t 钉钉token  -m 钉钉信息 -l 发送消息的标题\t#发送钉钉消息" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "s:l:t:m:"
        )
    except getopt.GetoptError:
        print("%s -h" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    # 帮助
    if "-h" in command_dict:
        useage()
        sys.exit()
    # 获取监控项数据
    elif '-t' in command_dict and '-s' in command_dict and '-m' in command_dict and '-l' in command_dict:
        command_data = dict()
        command_data['token'] = command_dict.get("-t")
        command_data['secret'] = command_dict.get("-s")
        command_data['message'] = command_dict.get("-m")
        command_data['subject'] = command_dict.get("-l")
        send_webhook(**command_data)
    else:
        RecodeLog.error(msg='输入的参数异常，请检查！')
        useage()
        sys.exit(1)


if __name__ == "__main__":
    main()

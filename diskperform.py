# coding=utf-8
# !/usr/bin/env python
import sys
import simplejson as json
import getopt
import os
import pip
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'


def install(package):
    """
    :param package:安装包名
    :return: 安装的状态和报错信息组成的字典
    """
    try:
        pip.main(['install', package])
        return {"status": True, "msg": "Install successfully"}
    except Exception as e:
        return {"status": False, "msg": e}


def uninstall(package):
    """
    :param package: 卸载包名
    :return: 卸载的状态和报错信息组成的字典
    """
    try:
        pip.main(['uninstall', package])
        return {"status": True, "msg": "Uninstall successfully"}
    except Exception as e:
        return {"status": False, "msg": e}


try:
    import psutil
except:
    print(install('psutil'))


class DiskPerform(object):

    disklist = []

    def get_iostat(self, vfs, item):
        """
        :param vfs: disk-id
        :param item: disk-item
        :return: item data
        """
        for k, v in psutil.disk_io_counters(perdisk=True).items():
            if k != vfs:
                continue
            try:
                print(getattr(v, item))
            except Exception as e:
                print(e)

    {% raw %}
    def get_disk(self):
        """
        :return: disk on linux server
        """
        for i in psutil.disk_partitions():
            self.disklist.append({"{#DEVICE}": i.device, "{#DEVICENAME}": i.device.replace("/dev/", "")})
        return json.dumps({"data": self.disklist}, indent=4)
    {% endraw %}

def useage():
    print("%s -h" % sys.argv[0])
    print("%s -d" % sys.argv[0])
    print("%s -t item -s disk" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "dt:s:"
        )
    except getopt.GetoptError:
        print("%s -H" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    d = DiskPerform()
    # 帮助
    if '-h' in command_dict:
        useage()
        sys.exit()
    # 获取监控项数据
    elif '-d' in command_dict:
        print(d.get_disk())
    elif '-t' in command_dict and '-s' in command_dict:
        i = command_dict.get('-s')
        t = command_dict.get('-t')
        d.get_iostat(i, t)
    else:
        useage()
        sys.exit(1)


if __name__ == '__main__':
    main()

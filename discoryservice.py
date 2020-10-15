# coding=utf-8
# !/usr/bin/env python
import simplejson as json
import sys
import getopt
import psutil


class DiscoryService(object):
    # { % raw %}

    def port_list(self, process):
        """
        :param process:
        :return:
        """
        data = []
        for connect in psutil.net_connections():
            name = self.process_name(connect.pid)
            if name is None or name != process or connect.status != 'LISTEN':
                continue
            datadict = {"{#SERVICE}": name, "{#SERVICEPORT}": connect.laddr.port}
            if datadict in data or (name == "mysqld" and len(connect.laddr.port) == 5):
                continue
            data.append(datadict)
        return json.dumps({"data": data}, indent=4)

    def pid_list(self, process):
        """
        :param process:
        :return:
        """
        data = []
        for connect in psutil.net_connections():
            name = self.process_name(connect.pid)
            if name is None or name != process:
                continue
            datadict = {"{#SERVICE}": name, "{#SERVICEPID}": connect.pid}
            if datadict in data:
                continue
            data.append(datadict)
        return json.dumps({"data": data}, indent=4)

    def process_name(self, pid):
        try:
            p = psutil.Process(pid)
            return p.name()
        except:
            return None


# { % endraw %}

def useage():
    print("%s -h\t#帮助文档" % sys.argv[0])
    print("%s -d\t程序名称\t#返回程序名称和端口" % sys.argv[0])
    print("%s -s\t程序名称\t#返回程序名称和PID" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hd:s:"
        )
    except getopt.GetoptError:
        print("%s -h" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    d = DiscoryService()
    # 帮助
    if '-h' in command_dict:
        useage()
        sys.exit()
    # 获取监控项数据
    elif '-d' in command_dict:
        p = command_dict.get('-d')
        print(d.port_list(p))
    elif '-s' in command_dict:
        i = command_dict.get('-s')
        print(d.pid_list(i))
    else:
        useage()
        sys.exit(1)


if __name__ == '__main__':
    main()

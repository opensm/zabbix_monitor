# -*- coding: UTF-8 -*-
import consul
import sys
import getopt
import simplejson as json


class ConsulQuery(object):
    def __init__(self, **kwargs):
        self.consul = consul.Consul(**kwargs)

    def get_nodes(self, data_center):
        """
        :param data_center:
        :return:
        """
        return self.consul.catalog.nodes(dc=data_center)

    def get_node(self, node, data_center):
        """
        :param node:
        :param data_center:
        :return:
        """
        node_data = self.consul.catalog.node(node=node, dc=data_center)[1]
        return {
            "node_id": node_data["Node"]['ID'],
            "node_name": node_data['Node']['Node'],
            "address": node_data["Node"]["Address"],
            "data_center": data_center,
            "ip_addresses": node_data['Node']['TaggedAddresses'],
            "node_meta": node_data["Node"]['Meta'],
            "services": node_data["Services"]
        }

    def deregister(self, node, dc, service_id=None, check_id=None, token=None):
        """
        :param node:
        :param service_id:
        :param check_id:
        :param dc:
        :param token:
        :return:
        """
        data_kwargs = {
            "node": node,
            "service_id": service_id,
            "check_id": check_id,
            "dc": dc,
            "token": token
        }
        if node is None or dc is None:
            return False
        if service_id is None:
            data_kwargs.pop("service_id")
        if check_id is None:
            data_kwargs.pop("check_id")
        if token is None:
            data_kwargs.pop("token")
        try:
            print(data_kwargs['dc'])
            print(self.consul.catalog.deregister(**data_kwargs))
            return True
        except Exception as error:
            print(error)
            return False

    def register(self, node, address, dc, service=None, check=None, token=None, node_meta=None):
        """
        :param node:
        :param address:
        :param service:
        :param check:
        :param dc:
        :param token:
        :param node_meta:
        :return:
        """
        data_kwargs = {
            "node": node,
            "address": address,
            "service": service,
            "check": check,
            "dc": dc,
            "token": token,
            "node_meta": node_meta
        }
        print(data_kwargs['dc'])
        if node is None or dc is None or address is None:
            return False
        if service is None:
            data_kwargs.pop("service")
        if check is None:
            data_kwargs.pop("check")
        if token is None:
            data_kwargs.pop("token")
        if node_meta is None:
            data_kwargs.pop("node_meta")
        try:
            print(self.consul.catalog.register(**data_kwargs))
            return True
        except Exception as error:
            print(error)
            return False

    def get_service(self, service, data_center):
        """
        :param service:
        :param data_center:
        :return:
        """

        return self.consul.catalog.service(service=service, dc=data_center)

    def get_services(self, data_center):
        """
        :param data_center:
        :return:
        """

        return self.consul.catalog.services(dc=data_center)

    def check_service_health(self, service):
        """
        :param service:
        :return:
        """
        c = self.consul.health.checks(service=service)
        return c

    def list(self, subject):
        """
        :param subject:
        :return:
        """
        assert not hasattr(self.consul, subject)
        obj_getattr = getattr(self.consul, subject)
        return obj_getattr.list()


def get_service_list(host="127.0.0.1", port=8500, token=None):
    """
    :return:
    """
    data = list()
    if token is None:
        params = {
            "host": host,
            "port": port
        }
    else:
        params = {
            "host": host,
            "port": port,
            "token": token
        }

    cq = ConsulQuery(**params)
    for key, value in cq.get_services(data_center="dc1")[1].items():
        for ser in cq.check_service_health(service=key)[1]:
            data.append({"{#SERVICE}": key, "{#NODE}": ser["Node"], "{#NAME}": ser['Name']})
    return json.dumps({"data": data}, indent=4)


def check_service(service, node, host="127.0.0.1", port=8500, token=None):
    """
    :param service:
    :param node:
    :param host:
    :param port:
    :param token:
    :return:
    """
    data = list()
    if token is None:
        params = {
            "host": host,
            "port": port
        }
    else:
        params = {
            "host": host,
            "port": port,
            "token": token
        }

    cq = ConsulQuery(**params)
    for ser in cq.check_service_health(service=service)[1]:
        if ser['Node'] == node and ser['Status'] == 'passing':
            return 1
        elif ser['Node'] == node and ser['Status'] != 'passing':
            return 0
    return 0


def useage():
    print("%s -h\t#帮助文档" % sys.argv[0])
    print("%s -h IP -p端口 -t token（可选） -d\t#返回服务名称列表" % sys.argv[0])
    print("%s -s\t服务名称\t#返回服务状态" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "h:ds:t:Hn:"
        )
    except getopt.GetoptError:
        print("%s -H" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    d = ConsulQuery()
    # 帮助
    if '-H' in command_dict or (('-s' not in command_dict or "-n" not in command_dict) and '-d' not in command_dict):
        useage()
        sys.exit()
    # 获取监控项数据
    elif '-d' in command_dict:
        zabbix_data = dict()
        if "-h" in command_dict:
            zabbix_data['host'] = command_dict.get('-h')
        if "-p" in command_dict:
            zabbix_data['port'] = command_dict.get("-p")
        if "-t" in command_dict:
            zabbix_data['token'] = command_dict.get("-t")

        print(get_service_list(**zabbix_data))
    elif '-s' in command_dict:
        zabbix_data = dict()
        zabbix_data['service'] = command_dict.get('-s')
        zabbix_data['node'] = command_dict.get("-n")
        if "-h" in command_dict:
            zabbix_data['host'] = command_dict.get('-h')
        if "-p" in command_dict:
            zabbix_data['port'] = command_dict.get("-p")
        if "-t" in command_dict:
            zabbix_data['token'] = command_dict.get("-t")
        print(check_service(**zabbix_data))
    else:
        useage()
        sys.exit(1)


if __name__ == "__main__":
    main()

# coding=utf-8
# !/usr/bin/env python
import MySQLdb
import MySQLdb.cursors
import getopt
import sys


class MySQLStatus(object):
    def __init__(self, params):
        if not isinstance(params, dict):
            print("Error params!")
            sys.exit(1)
        params['cursorclass'] = MySQLdb.cursors.DictCursor
        try:
            self.__conn = MySQLdb.connect(**params)
            self.__cursor = self.__conn.cursor()
        except Exception as error_message:
            print(error_message)
            sys.exit(1)

    def format_data(self, data, sql):
        result = '''<?xml version="1.0"?>\n\n<resultset statement="{0}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'''.format(
            sql
        )
        # result = '''<?xml version="1.0"?>\n\n<resultset statement="%s">''' % sql
        for value in data:
            tmp_str = '''<row>\n\t<field name="Variable_name">{0}</field>\n\t<field name="Value">{1}</field>\n  </row>\n'''.format(
                value['Variable_name'], value['Value']
            )
            result = "%s\n%s" % (result, tmp_str)
        result = "{0}</resultset>".format(result)
        return result

    def get_status_variables(self):
        """
        :return: master 下的监控项对应数据
        """

        tuples = str(self.get_verion()).split('.')
        try:
            sql = "show global status"
            self.__cursor.execute(sql)
            data_dict = self.__cursor.fetchall()
            return self.format_data(data_dict, sql)
        except Exception as error_message:
            return error_message

    def get_slave_items(self):
        """
        :return: 获取Slave 的监控项数据
        """
        sql = "show slave status"
        try:
            self.__cursor.execute(sql)
            data_dict = self.__cursor.fetchall()

            return self.format_data(data_dict, sql)
        except:
            return self.format_data({}, sql)

    def get_databases(self):
        """
        :return:
        """
        sql = "show databases;"
        sql = "select SCHEMA_NAME from information_schema.SCHEMATA;"
        self.__cursor.execute(sql)
        for value in self.__cursor.fetchall():
            print(value['SCHEMA_NAME'])

    def get_dbsize(self, schema):
        """
        :param schema:
        :return:
        """
        sql = "SELECT SUM(DATA_LENGTH + INDEX_LENGTH) AS DBSIZE FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{0}'".format(
            schema
        )
        self.__cursor.execute(sql)
        data_dict = self.__cursor.fetchall()
        if not data_dict:
            return 0
        return data_dict[0]['DBSIZE']

    def get_status(self):
        """
        :return:获取MySQL状态
        """
        try:
            self.__conn.ping()
            return "mysqld is alive"
        except:
            return "You can check this by doing 'telnet 127.0.0.1 3307"

    def get_verion(self):
        """
        :return: 获取MySQL版本
        """
        try:
            self.__cursor.execute("select version();")
            return self.__cursor.fetchall()[0]['version()']
        except Exception as e:
            return e


def useage():
    print("%s:" % sys.argv[0])
    print("\t-H\t#帮助说明")
    print("\t-h\t数据库IP\t#选填,默认127.0.0.1")
    print("\t-P\t数据库端口\t#选填 默认3306")
    print("\t-u\t数据库用户名\t#必填")
    print("\t-p\t数据库密码\t#必填")
    print("\t-t\t数据库监控项\t#必填")


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "Hu:p:t:h:P:d:"
        )
    except getopt.GetoptError:
        print("%s -H" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    # 帮助
    if '-H' in command_dict and ('-u' not in command_dict or '-p' not in command_dict or '-t' not in command_dict):
        useage()
        sys.exit()
    # 获取监控项数据
    elif True or ('-h' in command_dict or '-P' in command_dict):
        zabbix_data = dict()
        if '-h' not in command_dict:
            zabbix_data['host'] = '127.0.0.1'
        else:
            zabbix_data['host'] = command_dict.get('-h')
        if '-P' not in command_dict:
            zabbix_data['port'] = 3306
        else:
            zabbix_data['port'] = int(command_dict.get('-P'))
        zabbix_data['user'] = command_dict.get('-u')
        zabbix_data['passwd'] = command_dict.get('-p')
        zabbix_item = command_dict.get('-t')
        m = MySQLStatus(zabbix_data)

        if zabbix_item == "ping":
            print(m.get_status())
        elif zabbix_item == "get_status_variables":
            print(m.get_status_variables())
        elif zabbix_item == "version":
            print(m.get_verion())
        elif zabbix_item == "db_discovery":
            m.get_databases()
        elif zabbix_item == "dbsize":
            if '-d' not in command_dict:
                print("参数错误，请检查")
            schema = command_dict.get('-d')
            print(m.get_dbsize(schema=schema))
        elif zabbix_item == "replication_discovery":
            print(m.get_slave_items())
        elif zabbix_item == "slave_status":
            print(m.get_slave_items())
    else:
        useage()
        sys.exit(1)


if __name__ == '__main__':
    main()

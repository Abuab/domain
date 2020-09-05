import re
import pymysql
from datetime import datetime
import requests
import whois
import subprocess
from warnings import filterwarnings

filterwarnings("ignore", category=pymysql.Warning)


def check_wxgfw(domain, req_url='https://tg-ops.com/tools/checkWx'):
    data = {
        'url': domain,
    }
    response = requests.request("GET", url=req_url, params=data).json()
    if response['data']:
        return False
    else:
        return True


def check_cngfw(url):
    cmd = "/data/pyenv3/bin/python /data/django/domain/mytools/check_gfw.py %s | grep 'is_bfw' | head -n 1 | awk -F':' '{print $2}' | sed 's/,//' | awk '{print $1}'" % url
    state, result = subprocess.getstatusoutput(cmd)
    if result:
        return True
    else:
        return False


def check_beian(udo):
    key = 'bd8356d00cf94cd7b747e7fc4a446a85'
    url = 'http://apidata.chinaz.com/CallAPI/Domain'
    data = {
        'key': key,
        'domainName': udo,
    }
    response = requests.request("POST", url=url, data=data).json()
    if response['Result'] == None:
        return False
    else:
        return True


def getinfo(url):
    try:
        sta, alltime = subprocess.getstatusoutput(
            f'echo | openssl s_client -servername {url} -connect {url}:443 2>/dev/null | openssl x509 -noout -dates')
        if sta == 0:
            alltime = alltime.split('\n')
            stime, etime = alltime[0], alltime[1]
            stime, etime = stime.split('='), etime.split('=')
            stime, etime = stime[1], etime[1]  # 域名证书开始时间和到期时间
            stat, stime = subprocess.getstatusoutput(f"date -d '{stime}' +'%Y-%m-%d %I:%M:%S'")
            state, etime = subprocess.getstatusoutput(f"date -d '{etime}' +'%Y-%m-%d %I:%M:%S'")
            states, nowtime = subprocess.getstatusoutput('date +%s')
            statu, uetime = subprocess.getstatusoutput(f"date +%s -d'{etime}'")
            remain = int(uetime) - int(nowtime)
            remain_days = int(remain / 60 / 60 / 24)  # 域名证书还剩多少天到期
        else:
            stime = '此域名无证书'
            etime = '此域名无证书'
            remain_days = 0
        s, a_notes_cmd = subprocess.getstatusoutput(
            "nslookup -qt=a %s | grep -A1 Name | grep Address | awk '{print $2}'" % url)
        b = ''
        if not a_notes_cmd:
            a_notes_result = a_notes_cmd.split('\n')
            for i in a_notes_result:
                b = b + i + ','
            a_notes = b.rstrip(',')
        else:
            a_notes = '111'
        wxgfw = check_wxgfw(url)
        cngfw = check_cngfw(url)

        dinfo = whois.whois(url)
        hostns = dinfo['name_servers']
        # 域名到期时间
        ctm = dinfo['expiration_date']
        if isinstance(ctm, list):
            ctm = ctm[-1]
        nowt = datetime.now()  # 当前时间
        ctm = ctm - nowt
        dexptime = ctm.days  # 域名到期剩余时间

        hsot_ns_list = []
        for i in hostns:
            wo = i.upper()
            hsot_ns_list.append(wo)

        new_list = []
        for j in hsot_ns_list:
            if j not in new_list:
                new_list.append(j)

        host_ns = ''
        for c in new_list:
            host_ns = host_ns + c + ','  # 域名DNS解析记录
        host_ns = host_ns.rstrip(',')
        ret = {
            'notbefore': stime,
            'notafter': etime,
            'remain_days': remain_days,
            'dns_resolver': host_ns,
            'dexptime': dexptime,
            "a_notes": a_notes,
            'wxwaf': wxgfw,
            'waf': cngfw,
        }
    except:
        return 5
    return ret


def get_par(url):
    try:
        cbeian = check_beian(url)
        rest = getinfo(url)
        rest['beian'] = cbeian
        return rest
    except:
        return 5


class MysqlOps(object):
    def get_conn(self):
        try:
            self.conn = pymysql.connect(host='localhost', user='root', passwd='tgops123..', charset='utf8', db='domain')
        except pymysql.Error as e:
            err = "连接数据库失败:%s" % e
            print(err)

    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except pymysql.Error as e:
            err = "关闭数据库失败:%s" % e
            print(err)

    def get_data_name(self, name):
        try:
            self.get_conn()
            sql = 'select name from app_certs where name=%s'
            cursor = self.conn.cursor()
            cursor.execute(sql, (name))
            new = cursor.fetchone()
            cursor.close()
            self.close_conn()
            return new
        except AttributeError as e:
            print(e)
            return None

    def insert_data(self, data_dict, ud):
        try:
            self.get_conn()
            if ud == 1:
                sql = "insert into app_certs (name,type,dtype,notbefore,notafter,remain_days,last_time,dreamin_days,dnsinfo,a_notes,wxwaf,waf) values('%s','%s','%s','%s','%s',%d,now(),%d,'%s','%s','%s','%s');" % (
                    data_dict['name'], data_dict['type'], data_dict['dtype'], data_dict['notbefore'],
                    data_dict['notafter'],
                    data_dict['remain_days'], data_dict['dreamin_days'], data_dict['dnsinfo'], data_dict['a_notes'],
                    data_dict['wxwaf'], data_dict['waf'])
            else:
                sql = "insert into app_certs (name,type,dtype,notbefore,notafter,remain_days,last_time,dreamin_days,dnsinfo,a_notes,beian,wxwaf,waf) values('%s','%s','%s','%s','%s',%d,now(),%d,'%s','%s','%s','%s',%s);" % (
                    data_dict['name'], data_dict['type'], data_dict['dtype'], data_dict['notbefore'],
                    data_dict['notafter'], int(data_dict['remain_days']), int(data_dict['dreamin_days']),
                    data_dict['dnsinfo'],
                    data_dict['a_notes'], data_dict['beian'], data_dict['wxwaf'], data_dict['waf'])
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            self.close_conn()
            return 1
        except AttributeError as e:
            print(e)
            return 0
        except TypeError as e:
            print(e)
            return 0


def main(file):
    type_list = [
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx',
        'xx'
    ]
    dtype_list = [
        '主域名',
        '落地页',
        '渠道'
    ]
    data_dict = {}
    news = MysqlOps()
    with open(file, 'r') as rstream:
        container = rstream.read().splitlines()
        try:
            for data in container:
                data_result = data.split('|')
                data_dict['name'] = data_result[0]
                data_dict['type'] = data_result[1]
                data_dict['dtype'] = data_result[2]
                if not re.match(r'[a-zA-Z0-9].+\.[a-zA-Z0-9].+$', data_dict['name']):
                    print('域名: %s格式错误' % data_dict['name'])
                    continue
                get_one = news.get_data_name(data_dict['name'])
                if get_one:
                    print('该域名:%s已经存在' % data_dict['name'])
                    continue
                if data_dict['type'] not in type_list:
                    print('没有此平台: %s' % data_dict['type'])
                    continue
                if data_dict['dtype'] not in dtype_list:
                    print('没有此类型的域名: %s' % data_dict['dtype'])
                    continue
                if data_dict['dtype'] != dtype_list[0]:
                    dinfo = getinfo(data_dict['name'])
                    if dinfo != 5:
                        data_dict['notbefore'] = dinfo['notbefore']
                        data_dict['notafter'] = dinfo['notafter']
                        data_dict['remain_days'] = dinfo['remain_days']
                        data_dict['dnsinfo'] = dinfo['dns_resolver']
                        data_dict['dreamin_days'] = dinfo['dexptime']
                        data_dict['a_notes'] = dinfo['a_notes']
                        data_dict['wxwaf'] = dinfo['wxwaf']
                        data_dict['waf'] = dinfo['waf']
                        ud = 1
                        insertdata = news.insert_data(data_dict, ud)
                        if insertdata:
                            print('域名：%s添加成功' % data_dict['name'])
                    else:
                        print('域名解析错误%s' % data_dict['name'])
                        continue
                else:
                    sinfo = get_par(data_dict['name'])
                    if sinfo != 5:
                        data_dict['notbefore'] = sinfo['notbefore']
                        data_dict['notafter'] = sinfo['notafter']
                        data_dict['remain_days'] = sinfo['remain_days']
                        data_dict['dnsinfo'] = sinfo['dns_resolver']
                        data_dict['dreamin_days'] = sinfo['dexptime']
                        data_dict['a_notes'] = sinfo['a_notes']
                        data_dict['beian'] = sinfo['beian']
                        data_dict['wxwaf'] = sinfo['wxwaf']
                        data_dict['waf'] = sinfo['waf']
                        ud = 0
                        insertdata = news.insert_data(data_dict, ud)
                        if insertdata:
                            print('域名添加成功%s' % data_dict['name'])
                    else:
                        print('域名解析错误%s' % data_dict['name'])
                        continue
        except Exception as e:
            print(e)


if __name__ == '__main__':
    file = '../input_data.txt'
    main(file)

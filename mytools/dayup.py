import pymysql
from datetime import datetime
import requests
import whois
import subprocess


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
    except Exception as e:
        return 5
    return ret


def get_par(url):
    try:
        cbeian = check_beian(url)
        rest = getinfo(url)
        rest['beian'] = cbeian
        return rest
    except Exception as e:
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

    def get_data_name(self):
        try:
            self.get_conn()
            sql = "select id,name,type,dtype from app_certs;"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            new = cursor.fetchall()
            new_list = [dict(zip([x[0] for x in cursor.description], row)) for row in new]
            cursor.close()
            self.close_conn()
            return new_list
        except AttributeError as e:
            print(e)

    def update_data(self, data_dict, ud):
        try:
            self.get_conn()
            if ud == 1:
                sql = "update app_certs set name='%s',type='%s',notbefore='%s',notafter='%s',remain_days=%d,last_time=now(),dreamin_days=%d,dnsinfo='%s',a_notes='%s',wxwaf=%d,waf=%d where id=%d;" % (
                    data_dict['name'], data_dict['type'], data_dict['notbefore'],
                    data_dict['notafter'], data_dict['remain_days'], data_dict['dexptime'], data_dict['dns_resolver'],
                    data_dict['a_notes'], data_dict['wxwaf'], data_dict['waf'],
                    data_dict['id'])
            else:
                sql = "update app_certs set name='%s',type='%s',notbefore='%s',notafter='%s',remain_days=%d,last_time=now(),dreamin_days=%d,dnsinfo='%s',a_notes='%s',beian=%d,wxwaf=%d,waf=%d where id=%d;" % (
                    data_dict['name'], data_dict['type'], data_dict['notbefore'],
                    data_dict['notafter'], data_dict['remain_days'], data_dict['dexptime'], data_dict['dns_resolver'],
                    data_dict['a_notes'], data_dict['beian'], data_dict['wxwaf'], data_dict['waf'],
                    data_dict['id'])
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            self.close_conn()
            return 1
        except AttributeError as e:
            print(e)
            self.conn.rollback()
            return 0
        except TypeError as e:
            print(e)
            self.conn.rollback()
            return 0


def main():
    news = MysqlOps()
    new = news.get_data_name()
    if new:
        for i in range(len(new)):
            url = new[i]['name']
            u_dtype = new[i]['dtype']
            if u_dtype != '主域名':
                url_data = getinfo(url)
                if url_data != 5:
                    print(url, u_dtype)
                    data_dict = {
                        "id": new[i]['id'],
                        "name": new[i]['name'],
                        "type": new[i]['type'],
                        "dtype": new[i]['dtype'],
                        "notbefore": url_data['notbefore'],
                        "notafter": url_data['notafter'],
                        "remain_days": url_data['remain_days'],
                        "dns_resolver": url_data['dns_resolver'],
                        "dexptime": url_data['dexptime'],
                        "a_notes": url_data['a_notes'],
                        'wxwaf': url_data['wxwaf'],
                        'waf': url_data['waf'],
                    }
                    up_data = news.update_data(data_dict, 1)
                    if up_data:
                        print('更新数据成功')
                    else:
                        print('发生异常，请检查')
                else:
                    print('更新域名字段失败')
            else:
                url = new[i]['name']
                url_data = get_par(url)
                if url_data != 5:
                    print(url, u_dtype)
                    data_dict = {
                        "id": new[i]['id'],
                        "name": new[i]['name'],
                        "type": new[i]['type'],
                        "dtype": new[i]['dtype'],
                        "notbefore": url_data['notbefore'],
                        "notafter": url_data['notafter'],
                        "remain_days": url_data['remain_days'],
                        "dns_resolver": url_data['dns_resolver'],
                        "dexptime": url_data['dexptime'],
                        "a_notes": url_data['a_notes'],
                        'beian': url_data['beian'],
                        'wxwaf': url_data['wxwaf'],
                        'waf': url_data['waf'],
                    }
                    up_data = news.update_data(data_dict, 0)
                    if up_data:
                        print('更新数据成功')
                    else:
                        print('发生异常，请检查')
                else:
                    print('更新域名字段失败')


if __name__ == '__main__':
    main()

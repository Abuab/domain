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

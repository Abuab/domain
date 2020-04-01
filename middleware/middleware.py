import json
from datetime import datetime
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

REQUEST_PATH = [
    '/login/',
    '/logout/',
    '/domaininfo/',
    '/adddomain/',
    '/search/',
    '/delete/',
    '/palcesort/',
    '/typesort/',
    '/label/',
    '/sort291/',
    '/sort646/',
    '/sortjj/',
    '/sortty1/',
    '/sortty2/',
    '/sorttc/',
    '/sorttcgj/',
    '/sorttcss/',
    '/sortycgj/',
    '/sortscgj/',
    '/sortqcgj/',
    '/sortmcgj/',
    '/sorttc6/',
    '/sortmd/',
    '/sortldy/',
    '/sortqd/',
    '/labeldreamin/',
    '/labelremain/',
    '/labelwxwaf/',
    '/labelwaf/',
    '/labelbeian/',
    '/update/',
    '/addinbulk/',
]

IP_WHITE_LIST_FILE = '.env'
ACCESS_LOG = 'log/access.log'
ERROR_LOG = 'log/error.log'


def ip_white(file):
    IP_WHITE_LIST = []
    with open(file, 'r') as rstream:
        container = rstream.read().splitlines()
        for ip in container:
            IP_WHITE_LIST.append(ip)
            return IP_WHITE_LIST


class WriteLog:
    def __init__(self, req_path, client_ip):
        self.req_path = req_path
        self.client_ip = client_ip

    def write_acces_log(self, acc_log):
        req_time = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
        req_dict = {
            'request_tiem': req_time,
            'request_path': self.req_path,
            'client_ip': self.client_ip,
        }
        with open(acc_log, 'a+') as f:
            f.write(json.dumps(req_dict) + '\n')

    def write_error_log(self, err_log, error_body):
        req_time = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
        req_dict = {
            'request_tiem': req_time,
            'request_path': self.req_path,
            'client_ip': self.client_ip,
            'error_body': error_body
        }
        with open(err_log, 'a+') as f:
            f.write(json.dumps(req_dict) + '\n')


class CatchErr(MiddlewareMixin):
    def process_request(self, request):
        if request.path not in REQUEST_PATH:
            return redirect(reverse('app:login'))
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if not x_forwarded_for:
            x_forwarded_for = request.META.get('REMOTE_ADDR', "")
        client_ip = x_forwarded_for.split(",")[-1].strip() if x_forwarded_for else ""
        access_ip = ip_white(IP_WHITE_LIST_FILE)
        writelog = WriteLog(request.path, access_ip)
        if client_ip in access_ip:
            writelog.write_acces_log(ACCESS_LOG)
        else:
            if request.path != REQUEST_PATH[0]:
                return render(request, 'page_jump.html')

    def process_exception(self, request, exception):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if not x_forwarded_for:
            x_forwarded_for = request.META.get('REMOTE_ADDR', "")
        client_ip = x_forwarded_for.split(",")[-1].strip() if x_forwarded_for else ""
        writelog = WriteLog(request.path, client_ip)
        writelog.write_error_log(ERROR_LOG, exception)
        return redirect(reverse('app:domain_info'))

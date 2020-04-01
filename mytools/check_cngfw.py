import json
import sys
import requests


def check_cngfw(domain, req_url='http://ce8.com/check'):
    try:
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        client = requests.session()
        client.get(url=req_url, headers=header, timeout=3)
        csrftoken = client.cookies['XSRF-TOKEN']

        post_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'http://ce8.com',
            'Referer': req_url,
            'X-CSRF-TOKEN': csrftoken,
        }

        q_post_url = 'http://check1.ce8.com:3034/api/check/bfw_full'
        data = {'url': domain}
        res = client.post(url=q_post_url, data=json.dumps(data), headers=post_header, timeout=3).text
        return res
    except:
        return '111'


if __name__ == '__main__':
    checkgfw = check_cngfw(sys.argv[1])
    print(checkgfw)

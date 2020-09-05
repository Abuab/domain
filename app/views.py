import os
import re

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from app.forms import AddUrlForm
from mytools.helper import getinfo, get_par
from app.models import Certs


def login(request):
    data = {
        "title": "登录",
    }
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            request.session['user'] = username
            if request.user.is_authenticated():
                return HttpResponseRedirect('/domaininfo/')
        else:
            data = {
                "title": "登录",
                "error": "用户名或密码错误!"
            }
            return render(request, 'login.html', context=data)
    else:
        return render(request, 'login.html', context=data)


def user_logout(request):
    logout(request)
    return redirect(reverse('app:login'))


@login_required(login_url='app:login', redirect_field_name='')
def domain_info(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    certs = Certs.objects.all().order_by("id")
    paginator = Paginator(certs, per_page)
    page_object = paginator.page(page)
    data = {
        "title": "域名管理",
        "certs": certs,
        "page_object": page_object,
        "page_range": paginator.page_range,
    }
    return render(request, 'domainmanager.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def add_domain(request):
    if request.method == "GET":
        form = AddUrlForm()
        data = {
            "title": "添加域名",
            'form': form
        }
        return render(request, 'adddomain.html', context=data)
    if request.method == "POST":
        form = AddUrlForm(request.POST, request.FILES)
        type_list = (
            (0, 'xx'),
            (1, 'xx'),
            (2, 'xx'),
            (3, 'xx'),
            (4, 'xx'),
            (5, 'xx'),
            (6, 'xx'),
            (7, 'xx'),
            (8, 'xx'),
            (9, 'xx'),
            (10, 'xx'),
            (11, 'xx'),
            (12, 'xx'),
        )
        dtype_list = (
            (0, "主域名"),
            (1, "落地页"),
            (2, "渠道"),
        )
        if form.is_valid():
            alldata = form.clean()
            url = alldata['Form_url'].strip()
            type = type_list[alldata['Form_type']][1]
            dtype = dtype_list[alldata['Form_dtype']][1]
            certs = Certs()
            name = url
            cname = Certs.objects.all().filter(name=name)
            if cname.exists():
                error = '%s此域名已经存在' % name
                data = {
                    'error': error
                }
                return render(request, 'page_jump_add.html', context=data)
            else:
                if dtype != '主域名':
                    dinfo = getinfo(name)
                    if dinfo != 5:
                        certs.notbefore = dinfo['notbefore']
                        certs.notafter = dinfo['notafter']
                        certs.remain_days = dinfo['remain_days']
                        certs.dnsinfo = dinfo['dns_resolver']
                        certs.dreamin_days = dinfo['dexptime']
                        certs.a_notes = dinfo['a_notes']
                        certs.wxwaf = dinfo['wxwaf']
                        certs.waf = dinfo['waf']
                        certs.name = name
                        certs.type = type
                        certs.dtype = dtype
                        certs.save()
                        return HttpResponseRedirect('/domaininfo/')
                    else:
                        error = '%s此域名解析出现错误' % name
                        data = {
                            'error': error
                        }
                        return render(request, 'page_jump_add.html', context=data)
                else:
                    sinfo = get_par(name)
                    if sinfo != 5:
                        certs.notbefore = sinfo['notbefore']
                        certs.notafter = sinfo['notafter']
                        certs.remain_days = sinfo['remain_days']
                        certs.dnsinfo = sinfo['dns_resolver']
                        certs.dreamin_days = sinfo['dexptime']
                        certs.a_notes = sinfo['a_notes']
                        certs.beian = sinfo['beian']
                        certs.wxwaf = sinfo['wxwaf']
                        certs.waf = sinfo['waf']
                        certs.name = name
                        certs.type = type
                        certs.dtype = dtype
                        certs.save()
                        return HttpResponseRedirect('/domaininfo/')
                    else:
                        error = '%s此域名解析出现错误' % name
                        data = {
                            'error': error
                        }
                        return render(request, 'page_jump_add.html', context=data)
        else:
            error = form.errors
            data = {
                "title": "添加域名",
                'form': form,
                'error': error
            }
            return render(request, 'adddomain.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def search(request):
    if request.method == "GET":
        return render(request, 'domainmanager.html')
    elif request.method == "POST":
        sear = request.POST.get('sear')
        if sear:
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
            certs = Certs.objects.all().order_by("id")
            paginator = Paginator(certs, per_page)
            page_object = paginator.page(page)
            try:
                s_name = Certs.objects.all().filter(name=sear)
                s_type = Certs.objects.all().filter(type=sear)
                s_dtype = Certs.objects.all().filter(dtype=sear)
                s_dnsinfo = Certs.objects.all().filter(dnsinfo=sear)
                s_a_notes = Certs.objects.all().filter(a_notes=sear)
                stype = s_name or s_type or s_dtype or s_dnsinfo or s_a_notes
                if stype.exists():
                    data = {
                        "title": '搜索',
                        'stype': stype,
                        "page_object": page_object,
                        "page_range": paginator.page_range,
                    }
                    return render(request, 'search.html', context=data)
                else:
                    return redirect(reverse('app:search'))
            except:
                return redirect(reverse('app:search'))
        else:
            return redirect(reverse('app:domain_info'))


@login_required(login_url='app:login', redirect_field_name='')
@csrf_exempt
def delete_date(request):
    if request.method == "POST":
        try:
            cert_id = request.POST.get('cert_id')
            cert = Certs.objects.get(id=cert_id)
            cert.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("2")


@login_required(login_url='app:login', redirect_field_name='')
def place_sort(request):
    if request.method == "GET":
        certs291 = Certs.objects.all().filter(type='xx')
        certs646 = Certs.objects.all().filter(type='xx')
        certsty1 = Certs.objects.all().filter(type='xx')
        certsty2 = Certs.objects.all().filter(type='xx')
        certstc = Certs.objects.all().filter(type='xx')
        certsjj = Certs.objects.all().filter(type='JJ')
        certstcgj = Certs.objects.all().filter(type='xx')
        certstcss = Certs.objects.all().filter(type='xx')
        certsycgj = Certs.objects.all().filter(type='xx')
        certsscgj = Certs.objects.all().filter(type='xx')
        certsqcgj = Certs.objects.all().filter(type='xx')
        certsmcgj = Certs.objects.all().filter(type='xx')
        certstc6 = Certs.objects.all().filter(type='xx')
        data = {
            'title': "平台分类",
            'certs291': certs291.count(),
            'certs646': certs646.count(),
            'certsty1': certsty1.count(),
            'certsty2': certsty2.count(),
            'certstc': certstc.count(),
            'certsjj': certsjj.count(),
            'certstcgj': certstcgj.count(),
            'certstcss': certstcss.count(),
            'certsycgj': certsycgj.count(),
            'certsscgj': certsscgj.count(),
            'certsqcgj': certsqcgj.count(),
            'certsmcgj': certsmcgj.count(),
            'certstc6': certstc6.count(),
        }
        return render(request, 'place_sort.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def type_sort(request):
    certs_zym = Certs.objects.all().filter(dtype='主域名')
    certs_ldy = Certs.objects.all().filter(dtype='落地页')
    certs_qudao = Certs.objects.all().filter(dtype='渠道')
    data = {
        'title': "域名分类",
        "certs_zym": certs_zym.count(),
        "certs_ldy": certs_ldy.count(),
        "certs_qudao": certs_qudao.count(),
    }
    return render(request, 'type_sort.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_data(request):
    ldreamin = Certs.objects.all().filter(dreamin_days__lte=7).count()
    lremain = Certs.objects.all().filter(remain_days__lte=7).count()
    lwxwaf = Certs.objects.all().filter(wxwaf=True).count()
    lwaf = Certs.objects.all().filter(waf=True).count()
    lbeian = Certs.objects.all().filter(dtype='主域名').filter(beian=False).count()
    data = {
        'title': "标签",
        'ldreamin': ldreamin,
        'lremain': lremain,
        'lwxwaf': lwxwaf,
        'lwaf': lwaf,
        'lbeian': lbeian
    }
    return render(request, 'label.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_291(request):
    if request.method == "GET":
        cert291 = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "291分类",
            "cert291": cert291,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sort291.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_646(request):
    if request.method == "GET":
        cert646 = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "646分类",
            "cert646": cert646,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sort646.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_jj(request):
    if request.method == "GET":
        certjj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "jj分类",
            "cert291": certjj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortjj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_mcgj(request):
    if request.method == "GET":
        certmcgj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "mcgj分类",
            "certmcgj": certmcgj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortmcgj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_qcgj(request):
    if request.method == "GET":
        certqcgj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "qcgj分类",
            "certqcgj": certqcgj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortqcgj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_scgj(request):
    if request.method == "GET":
        certscgj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "scgj分类",
            "certscgj": certscgj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortscgj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_tc6(request):
    if request.method == "GET":
        certtc6 = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "tc6分类",
            "certtc6": certtc6,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sorttc6.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_tcgj(request):
    if request.method == "GET":
        certtcgj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "tcgj分类",
            "certtcgj": certtcgj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sorttcgj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_tc(request):
    if request.method == "GET":
        certtc = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "tc分类",
            "certtc": certtc,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sorttc.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_tcss(request):
    if request.method == "GET":
        certtcss = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "tcss分类",
            "certtcss": certtcss,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sorttcss.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_ty1(request):
    if request.method == "GET":
        certty1 = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "ty1分类",
            "certty1": certty1,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortty1.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_ty2(request):
    if request.method == "GET":
        certty2 = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "ty2分类",
            "certty2": certty2,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortty2.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_ycgj(request):
    if request.method == "GET":
        certycgj = Certs.objects.all().filter(type='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "ycgj分类",
            "certycgj": certycgj,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'place/sortycgj.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_master_domain(request):
    if request.method == "GET":
        certmd = Certs.objects.all().filter(dtype='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "主域名分类",
            "certmd": certmd,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'domain_type/sortmd.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_ldy(request):
    if request.method == "GET":
        certldy = Certs.objects.all().filter(dtype='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "落地页分类",
            "certldy": certldy,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'domain_type/sortldy.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def sort_qd(request):
    if request.method == "GET":
        certqd = Certs.objects.all().filter(dtype='xx')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "渠道域名分类",
            "certqd": certqd,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'domain_type/sortqd.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_dreamin(request):
    if request.method == "GET":
        dreamin = Certs.objects.all().filter(dreamin_days__lte=7)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "将到期域名",
            "dreamin": dreamin,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'label/dreamain.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_remain(request):
    if request.method == "GET":
        remain = Certs.objects.all().filter(remain_days__lte=7)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "证书将到期",
            "remain": remain,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'label/remain.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_wxwaf(request):
    if request.method == "GET":
        wxwaf = Certs.objects.all().filter(wxwaf=True)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "微信拦截域名",
            "wxwaf": wxwaf,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'label/wxwaf.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_waf(request):
    if request.method == "GET":
        waf = Certs.objects.all().filter(waf=True)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "被墙域名",
            "waf": waf,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'label/waf.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
def label_beian(request):
    if request.method == "GET":
        beian = Certs.objects.all().filter(dtype='主域名').filter(beian=False)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        certs = Certs.objects.all().order_by("id")
        paginator = Paginator(certs, per_page)
        page_object = paginator.page(page)
        data = {
            'title': "掉备案域名",
            "beian": beian,
            "page_object": page_object,
            "page_range": paginator.page_range,
        }
        return render(request, 'label/beian.html', context=data)


@login_required(login_url='app:login', redirect_field_name='')
@csrf_exempt
def update(request):
    if request.method == "POST":
        try:
            cert_id = request.POST.get('cert_id')
            cert = Certs.objects.get(id=cert_id)
            d_name = cert.name
            d_type = cert.type
            d_dtype = cert.dtype
            cert.delete()
            certs = Certs()
            dinfo = getinfo(d_name)
            if dinfo != 5:
                certs.notbefore = dinfo['notbefore']
                certs.notafter = dinfo['notafter']
                certs.remain_days = dinfo['remain_days']
                certs.dnsinfo = dinfo['dns_resolver']
                certs.dreamin_days = dinfo['dexptime']
                certs.a_notes = dinfo['a_notes']
                certs.wxwaf = dinfo['wxwaf']
                certs.waf = dinfo['waf']
                certs.name = d_name
                certs.type = d_type
                certs.dtype = d_dtype
                certs.save()
                return HttpResponse("1")
        except:
            return HttpResponse("2")


@login_required(login_url='app:login', redirect_field_name='')
def add_in_bulk(request):
    if request.method == "GET":
        d_count = 8
        data = {
            "title": "批量添加域名",
            "d_count": d_count,
        }
        return render(request, 'add_in_bulk.html', context=data)
    if request.method == "POST":
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
        domain_data = request.POST.get("domain_data")
        try:
            certs = Certs()
            file = 'domain_tmp.txt'
            with open(file, 'a+') as f:
                f.write(domain_data)
            new_list = []
            with open(file, 'r') as rstream:
                container = rstream.read().splitlines()
                for ip in container:
                    new_list.append(ip)
            os.remove(file)
            new_dict = {}
            for i in new_list:
                i = i.split('|')
                new_dict['name'] = i[0]
                if not re.match(r'[a-zA-Z0-9].+\.[a-zA-Z0-9].+$', new_dict['name']):
                    d_count = 7
                    data = {
                        "title": "批量添加域名",
                        "d_count": d_count,
                    }
                    return render(request, 'add_in_bulk.html', context=data)
                cname = Certs.objects.all().filter(name=new_dict['name'])
                if cname.exists():
                    error = '此域名已经存在:%s' % new_dict['name']
                    data = {
                        "error": error,
                    }
                    return render(request, 'add_page_jump.html', context=data)
                new_dict['type'] = i[1]
                if new_dict['type'] not in type_list:
                    error = '平台名称错误，没有此平台 %s' % new_dict['type']
                    data = {
                        "error": error,
                    }
                    return render(request, 'add_page_jump.html', context=data)
                new_dict['dtype'] = i[2]
                if new_dict['dtype'] not in dtype_list:
                    error = '域名类型错误，没有此字段 %s' % new_dict['dtype']
                    data = {
                        "error": error,
                    }
                    return render(request, 'add_page_jump.html', context=data)
                certs.name = new_dict['name']
                certs.type = new_dict['type']
                certs.dtype = new_dict['dtype']
                if certs.dtype != '主域名':
                    dinfo = getinfo(certs.name)
                    if dinfo != 5:
                        certs.notbefore = dinfo['notbefore']
                        certs.notafter = dinfo['notafter']
                        certs.remain_days = dinfo['remain_days']
                        certs.dnsinfo = dinfo['dns_resolver']
                        certs.dreamin_days = dinfo['dexptime']
                        certs.a_notes = dinfo['a_notes']
                        certs.wxwaf = dinfo['wxwaf']
                        certs.waf = dinfo['waf']
                        certs.save()
                    else:
                        error = '域名解析错误，请重试 %s' % new_dict['name']
                        data = {
                            "error": error,
                        }
                        return render(request, 'add_page_jump.html', context=data)
                else:
                    sinfo = get_par(certs.name)
                    if sinfo != 5:
                        certs.notbefore = sinfo['notbefore']
                        certs.notafter = sinfo['notafter']
                        certs.remain_days = sinfo['remain_days']
                        certs.dnsinfo = sinfo['dns_resolver']
                        certs.dreamin_days = sinfo['dexptime']
                        certs.a_notes = sinfo['a_notes']
                        certs.beian = sinfo['beian']
                        certs.wxwaf = sinfo['wxwaf']
                        certs.waf = sinfo['waf']
                        certs.save()
                    else:
                        error = '域名解析错误，请重试 %s' % new_dict['name']
                        data = {
                            "error": error,
                        }
                        return render(request, 'add_page_jump.html', context=data)
            return redirect(reverse('app:domain_info'))
        except:
            error = '您输入的格式有误，请重新输入'
            data = {
                "error": error,
            }
            return render(request, 'add_page_jump.html', context=data)

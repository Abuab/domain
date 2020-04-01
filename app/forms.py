import re
from django.core.exceptions import ValidationError
from django import forms
from mytools.helper import getinfo
from app.models import Certs


def url_valinum(value):
    if not re.match(r'[a-zA-Z0-9].+\.[a-zA-Z0-9].+$', value):
        raise ValidationError('域名格式错误，请重新输入')
    elif getinfo(value) == 5:
        raise ValidationError('域名解析错误')


class AddUrlForm(forms.Form):
    model = Certs
    type_list = (
        (0, '291'),
        (1, '646'),
        (2, '兔牙1'),
        (3, '兔牙2'),
        (4, '唐朝'),
        (5, 'JJ'),
        (6, '唐朝国际'),
        (7, '唐朝盛世'),
        (8, '元朝国际'),
        (9, '宋朝国际'),
        (10, '秦朝国际'),
        (11, '明朝国际'),
        (12, '唐朝646'),
    )
    dtype_list = (
        (0, "主域名"),
        (1, "落地页"),
        (2, "渠道"),
    )
    Form_url = forms.CharField(max_length=124, strip=True, validators=[url_valinum, ],
                               error_messages={'required': u'域名不能为空'},
                               widget=forms.TextInput(
                                   attrs={'class': "form-contorl", 'placeholder': u'请输入域名', 'style': "color: red"}))
    Form_type = forms.IntegerField(widget=forms.widgets.Select(choices=type_list, attrs={'class': 'form-control'}))
    Form_dtype = forms.IntegerField(widget=forms.widgets.Select(choices=dtype_list, attrs={'class': 'form-control'}))

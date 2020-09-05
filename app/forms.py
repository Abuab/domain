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
    Form_url = forms.CharField(max_length=124, strip=True, validators=[url_valinum, ],
                               error_messages={'required': u'域名不能为空'},
                               widget=forms.TextInput(
                                   attrs={'class': "form-contorl", 'placeholder': u'请输入域名', 'style': "color: red"}))
    Form_type = forms.IntegerField(widget=forms.widgets.Select(choices=type_list, attrs={'class': 'form-control'}))
    Form_dtype = forms.IntegerField(widget=forms.widgets.Select(choices=dtype_list, attrs={'class': 'form-control'}))

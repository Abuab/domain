from django.db import models


class Certs(models.Model):
    name = models.CharField(max_length=45, verbose_name=("域名名称"), null=False, unique=True)
    type = models.CharField(max_length=126, verbose_name=('平台名称'))
    dtype = models.CharField(max_length=256, null=True, blank=True, verbose_name='域名类型')
    notbefore = models.CharField(max_length=24, null=True, blank=True, verbose_name=('开始时间'))
    notafter = models.CharField(max_length=24, null=True, blank=True, verbose_name=('到期时间'))
    remain_days = models.IntegerField(default=4, null=True, blank=True, verbose_name=('剩余天数'))
    last_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=('最后检查时间'))
    dreamin_days = models.IntegerField(default=4, null=True, blank=True, verbose_name="域名到期剩余天数")
    dnsinfo = models.CharField(max_length=256, verbose_name=("域名DNS详情"), null=False)
    a_notes = models.CharField(max_length=256, null=False, verbose_name='域名A记录')
    beian = models.BooleanField(default=False, verbose_name='有无备案')
    wxwaf = models.BooleanField(default=False, verbose_name='是否被微信拦截')
    waf = models.BooleanField(default=False, verbose_name='是否被墙')

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_dtype(self):
        return self.dtype

    def get_beian(self):
        return self.beian

    def get_wxwaf(self):
        return self.wxwaf

    def get_waf(self):
        return self.waf

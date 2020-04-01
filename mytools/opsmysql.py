import pymysql
import telegram


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

    def get_data_remain_days(self):
        try:
            self.get_conn()
            sql = "select * from app_certs where remain_days BETWEEN -2 and 7;"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            new = cursor.fetchall()
            new_list = list(map(lambda x: dict(zip([x[0] for x in cursor.description], [d for d in x])), new))
            new_list = [dict(zip([x[0] for x in cursor.description], row)) for row in new]
            cursor.close()
            self.close_conn()
            return new_list
        except AttributeError as e:
            print(e)

    def get_data_dreamin_days(self):
        try:
            self.get_conn()
            sql = "select * from app_certs where dreamin_days BETWEEN -50 and 7;"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            new = cursor.fetchall()
            new_list = [dict(zip([x[0] for x in cursor.description], row)) for row in new]
            cursor.close()
            self.close_conn()
            return new_list
        except AttributeError as e:
            print(e)

    def get_data_beian(self):
        try:
            self.get_conn()
            sql = "select name,type,dtype,beian from app_certs where dtype='主域名' and beian<1;"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            new = cursor.fetchall()
            new_list = [dict(zip([x[0] for x in cursor.description], row)) for row in new]
            cursor.close()
            self.close_conn()
            return new_list
        except AttributeError as e:
            print(e)

    def get_data_wxwaf(self):
        try:
            self.get_conn()
            sql = "select name,type,wxwaf from app_certs where dtype!='主域名' and wxwaf<1;"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            new = cursor.fetchall()
            new_list = [dict(zip([x[0] for x in cursor.description], row)) for row in new]
            cursor.close()
            self.close_conn()
            return new_list
        except AttributeError as e:
            print(e)


def main():
    chat_id = "-250182564"
    bot = telegram.Bot(token='1006108054:AAFo47eytOVgEDt9BHQ-Y3gvwEpJGoUQMGs')
    news = MysqlOps()
    new = news.get_data_remain_days()
    if new:
        for i in range(len(new)):
            name = new[i]['name']
            type = new[i]['type']
            notbefore = new[i]['notbefore']
            notafter = new[i]['notafter']
            remain_days = new[i]['remain_days']
            dreamin_days = new[i]['dreamin_days']
            msg = u'故障信息:域名证书到期告警\n域名:%s\n平台名称:%s\n证书开始时间:%s\n证书到期时间:%s\n证书剩余时间:%s天\n域名到期剩余时间:%s天' % (
                name, type, notbefore, notafter, remain_days, dreamin_days)
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        print('get_data_remain_days operation field')

    news = MysqlOps()
    new = news.get_data_dreamin_days()
    if new:
        for i in range(len(new)):
            name = new[i]['name']
            type = new[i]['type']
            notbefore = new[i]['notbefore']
            notafter = new[i]['notafter']
            remain_days = new[i]['remain_days']
            dreamin_days = new[i]['dreamin_days']
            msg = u'故障信息:域名到期告警\n域名:%s\n平台名称:%s\n证书开始时间:%s\n证书到期时间:%s\n证书剩余时间:%s天\n域名到期剩余时间:%s天' % (
                name, type, notbefore, notafter, remain_days, dreamin_days)
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        print('get_data_dreamin_days operation field')

    news = MysqlOps()
    new = news.get_data_beian()
    if new:
        for i in range(len(new)):
            name = new[i]['name']
            type = new[i]['type']
            dtype = new[i]['dtype']
            msg = u'故障信息:域名掉备案\n域名:%s\n域名类型:%s\n平台名称:%s\n' % (name, dtype, type,)
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        print('get_data_dreamin_days operation field')

    news = MysqlOps()
    new = news.get_data_wxwaf()
    if new:
        for i in range(len(new)):
            name = new[i]['name']
            type = new[i]['type']
            msg = u'故障信息:域名被微信拦截\n域名:%s\n平台名称:%s\n' % (name, type,)
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        print('get_data_dreamin_days operation field')


if __name__ == '__main__':
    main()

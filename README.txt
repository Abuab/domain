



# 计划任务crontab    
    # 域名告警脚本
    10 */5 * * * /data/pyenv/bin/python /data/domain/mytools/opsmysql.py

    # 域名各字段更新脚本
    1 */5 * * * /data/pyenv/bin/python /data/domain/mytools/dayup.py



# 在服务器上进行批量添加域名的方法：
    # 手动输入域名至 /data/domain/input_data.txt 如果文件不存在则手动创建 
    请遵循以下格式，一行一个，以 | 来进行分隔
    baidu.com|唐朝国际|主域名

    输入完之后执行脚本：
        /data/domain/mytools/manual_script.py
    等待脚本执行完毕即可批量添加

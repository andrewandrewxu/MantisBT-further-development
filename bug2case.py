# -*- coding: utf-8 -*-

import mysql.connector
import os
import sys
import csv
import datetime
import mailService


reload(sys)
sys.setdefaultencoding('utf-8')

print "************************ STEP 0 ************************"
print "init data ......"
# Project ID to Project Name Map in DB
project_dic = {
    "11" : "ChatGame", "13" : "大牙", "17" : "想玩"，    
}

# Category ID to Category Name Map in DB
category_dic = {
    "1" : "general", "49" : "安卓", "50" : "general", "51" : "IOS", "52" : "服务端",
    "56" : "音视频", "57" : "客户端网络", "58" : "游戏", "72" : "测试组",
    "60" : "general", "59" : "安卓", "61" : "IOS", "62" : "服务端"， "86" : "IOS",
    "87" : "安卓"， "88" : "服务器"
}

# User ID to User Name Map in DB
user_dic = {
    "117": "王燕", "48": "刘冬", "52": "刘洁", "116": "钟舒妍", "61": "王超穆",
    "67": "曹玲", "99": "陈樱", "111": "田应贵", "85": "戴娟娟", "122": "陈兰",
    "109": "韩星", "115": "杨磊", "129": "郝先超", "131": "徐赵烜", "91": "冯炽",
}

# Mantis db configs
print "init mysql configs"
config = {
        'user': 'mantis',
        'password': 'handwin1',
        'host': '192.168.1.181',
        'database': 'mantis',
        'raise_on_warnings': True,
        'use_pure': False,
}

#取出脚本运行日期
print "init script time"
time = datetime.datetime.now()
date = str(time)[0:10]

# Connect to Mantis db and create an object
print "init mysql object for python"
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# DB actions
print "init sql statements"
get_tests = ("select project_id,category_id,id,summary,reporter_id from mantis_bug_table where"
         " id in (select bug_id from mantis_custom_field_string_table where value='是' and field_id=2);")
update_custom_field_string_table = ("update mantis_custom_field_string_table set value='否' where field_id=2 and bug_id=%s;")
add_tag_for_bug = ("insert into mantis_bug_tag_table values(%s, 2, 129, unix_timestamp());")

#判断是否存在 bug2case.csv 如果不存在则创建
print "************************ STEP 1 ************************"
csvfilename = "bug2case.csv"
isfileExists = os.path.isfile(csvfilename)
if False == isfileExists:
    print "---csv file not exists, now creating the file---"
    f = open(csvfilename,'w')
    f.close()
else:
        print "---csv file exists---"

#打印已存在的bug  id
print "************************ STEP 2 ************************"
csvfile = file(csvfilename, "r")
content = csv.reader(csvfile)
existing_ids = []
for existing_bug in content:
    existing_ids.append(existing_bug[2])
if existing_ids == []:
    print "---there is no existed bug in csv file---"
else:
    print "---The existing ids are: %s ---" % existing_ids
csvfile.close()

# Export the outputs into csv files
print "************************ STEP 3 ************************"
csvfile = file(csvfilename, "a")
writer = csv.writer(csvfile)

id_list_to_update = []


cursor.execute(get_tests)
for line in cursor:
    bug_id = str(line[2])
    if bug_id not in existing_ids:
        print "The bug id %s not in file, processing..." % bug_id
        project_name = "Unknown"
        if str(line[0]) in project_dic.keys():
            project_name = project_dic[str(line[0])]

        category_name = "Unknown"
        if str(line[1]) in category_dic.keys():
            category_name = category_dic[str(line[1])]

        reporter = "A girl has no name"
        if str(line[4]) in user_dic.keys():
            reporter = user_dic[str(line[4])]

        summary = line[3]
        print "Writing row... 项目: %s, 分类: %s, id: %s, \n摘要: %s, 提单人：%s " % \
              (project_name, category_name, bug_id, summary, reporter)
        writer.writerow([project_name, category_name, bug_id, summary, date, reporter])
    else:
        print "The bug %s is already in the CSV file, skipping..." % bug_id
    id_list_to_update.append(bug_id)
csvfile.close()

print "************************ STEP 4 ************************"
print "NOW we write data into mysql"
for single_id in id_list_to_update:
    # Set value=否 where field id=2 and previous value=是
    try:    
        print "Updating the bug_id %s in database" % single_id
        cursor.execute(update_custom_field_string_table % single_id)
    except:
        print "[WARNNING] write data into table mantis_custom_field_string_table Failed, please check"
    # Add tags for bugs that were added into CSV
    try:
        print "Adding tag for bug %s in database" % single_id
        cursor.execute(add_tag_for_bug % single_id)
    except:
        print "maybe the bug %s has tag in database" % single_id

cursor.close()
cnx.close()

print "************************ STEP 5 ************************"
print "NOW we send email if exists updated bugs"
# Send the email
if len(id_list_to_update):
    email_to = [ 'xchao@v5.cn', 'leiyang@v5.cn', 'jieliu@v5.cn', 'cmwang@v5.cn', 'zfeng@v5.cn',
                 'jjdai@v5.cn', 'dliu@v5.cn', 'ywang@v5.cn', 'lcao@v5.cn', 'zxxu@v5.cn', 'xhan@v5.cn',
                 'yingchen@v5.cn', 'lchen@v5.cn', 'syzhong@v5.cn', 'ygtian@v5.cn' ]
    email_subject = "Notice for bug2case %s" % str(time)
    email_content = """
        %d bugs have been added in the CSV file as the new test case, the IDs are:
        %s
    """ % (len(id_list_to_update), id_list_to_update)
    mailService.sendMail(email_to, email_subject, email_content, csvfilename)
print "Finished."


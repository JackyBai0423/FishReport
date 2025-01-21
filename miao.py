from urllib import request, parse
import os
import tkinter as tk
from tkinter import filedialog
import datetime, time, re
import csv

# initialize setting
if not os.path.exists("./setting.txt"):
    with open("./setting.txt", "w") as setting:
        root = tk.Tk()
        root.withdraw()
        miao_code = input("请输入喵码：")
        print("选择蓑笠翁log文件夹：")
        log_path = filedialog.askdirectory(
            title="Select a folder"  # Customize the dialog title
        )
        functions = input("选择推送消息种类：1.全部，2.上星/蓝，3.稀有（紫标，粉标，星蓝）此功能测试中：")
        onhook_weight_alert = int(input('请输入上钩重量警报：'))
        setting.write("miao_code="+miao_code+'\n')
        setting.write("log_path="+log_path+'\n')
        setting.write("function="+functions+'\n')
        setting.write('onhook_weight_alert='+str(onhook_weight_alert))
else:
    with open("./setting.txt") as setting:
        setting_file = setting.read().split('\n')
        miao_code = setting_file[0].split('=')[1]
        log_path = setting_file[1].split('=')[1]
        functions = setting_file[2].split('=')[1]
        onhook_weight_alert = int(setting_file[3].split('=')[1])
print('开始监控日志文件，如需退出请按CTRL+c')

# 渔获记录表格

current_log_date = datetime.date.today().strftime("%Y-%m-%d")
# catch_per_lure = {} # 记录渔获的dict
# if os.path.exists(current_log_date+'fish.csv'):
#     with open(current_log_date+'fish.csv', 'r') as current_fish_record:
#         reader = csv.reader(current_fish_record)
#         if reader.line_num>0:
#             fish_species=next(reader)[0].split('\t')[1:]
#         else:
#             fish_species = []
#         # 获取当日渔获统计
#         for row in reader:
#             row_data = row.split('\t')
#             lure_name = row_data[0]
#             lure_dict = {}
#             for i in range(1,len(row_data)):
#                 lure_dict[fish_species] = {'pass':row_data[i].split('|')[0],'nopass':row_data[i].split('|')[1]}
#             catch_per_lure[lure_name] = lure_dict
# else:
#     fish_species = []
# print(catch_per_lure)
current_log = open(log_path+'/'+datetime.date.today().strftime("%Y-%m-%d")+".txt")
# move the reading position to the end of the file
last_pos = 0
current_log.seek(last_pos)
current_log.read()
last_pos = current_log.tell()
# 写入渔获分析
# current_fish_record = open(current_log_date+'fish.csv', 'w')
while True:
    # 更新当前读取的日志文件，如果到了次日
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    if current_date != current_log_date:
        if os.path.exists(log_path+'/'+current_date+".txt"):
            current_log.close()
            current_log = open(log_path+'/'+current_date+".txt") #+'Flog'
            last_pos = 0
        if not os.path.exists(current_date+'fish.csv'):
            current_fish_record.close()
            current_fish_record = open(current_date+'fish.csv', 'w')

    current_log.seek(last_pos)
    line = current_log.readline()
    last_pos = current_log.tell()
    time.sleep(1)
    if len(line)>0:
        onhook_match = re.search(r"鱼上钩了！鱼信息:【(.+?)】(\d+(?:\.\d+)?)([kg|g]+)",line)
        capture_match = re.search(r"捕获：(?:[^【]*?)【(.+?)】【(.+?)】(?:【(.+?)】)?(\d+(?:\.\d+)?)([公斤|克]+).+?鱼饵:(.[^,]+)",line)
        if onhook_match or capture_match:
            print(line)
        if onhook_match:
            onhook_weight = float(onhook_match.group(2)) if onhook_match.group(3) == 'kg' else float(onhook_match.group(2))/1000
            if onhook_weight >= onhook_weight_alert:
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'巨大的'+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！'}))
        if capture_match:
        #     # 记录渔获
        #     if capture_match.group(1) not in fish_species:
        #         fish_species.append(capture_match.group(1))
        #     if capture_match.group(6)[:-1] not in catch_per_lure:
        #         catch_per_lure[capture_match.group(6)[:-1]] = {}
        #         catch_per_lure[capture_match.group(6)[:-1]]['All'] = {'pass':0, 'nopass':0}
        #     if capture_match.group(1) not in catch_per_lure[capture_match.group(6)[:-1]]:
        #         catch_per_lure[capture_match.group(6)[:-1]][capture_match.group(1)] = {'pass':0, 'nopass':0}
        #     if capture_match.group(2) != '普通':
        #         catch_per_lure[capture_match.group(6)[:-1]][capture_match.group(1)]['pass'] += 1
        #         catch_per_lure[capture_match.group(6)[:-1]]['All']['pass'] += 1
        #     else: 
        #         catch_per_lure[capture_match.group(6)[:-1]][capture_match.group(1)]['nopass'] += 1
        #         catch_per_lure[capture_match.group(6)[:-1]]['All']['nopass'] += 1

            if functions == '1' and capture_match.group(2) != '普通':
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'}))
            elif functions == '2' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠'):
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'上星/蓝了！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'}))
            elif functions == '3' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠' or capture_match.group(3) is not None):
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'稀有鱼！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'+('['+capture_match.group(3)+']') if capture_match.group(3) is not None else ''}))
        # if functions == '1' and line.split('【')[2][:2]=='达标':
        #     request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":line}))
        # elif (functions == '2' or functions == '3') and (line.split('【')[2][:2]=='星级' or line.split('【')[2][:2]=='蓝冠'):
        #     request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":line}))
    
#/捕获：(?:[^【]*?)【(.+?)】【(.+?)】(?:【(.+?)】)?(\d+(?:\.\d+)?)([公斤|克]+).+?鱼饵:(.[^,]+)/
# request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":text}))

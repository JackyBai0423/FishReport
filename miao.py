from urllib import request, parse
import os
import tkinter as tk
from tkinter import filedialog
import datetime, time, re
from win10toast import ToastNotifier
import csv

n = ToastNotifier()

def csv_to_dict(csv_file_path, skip_header=True, encoding="utf-8"):
    data_dict = {}
    
    with open(csv_file_path, mode="r", newline="", encoding=encoding) as f:
        reader = csv.reader(f)
        
        if skip_header:
            next(reader, None)
        
        for row in reader:
            if not row:
                continue  
            key = row[0]      
            value = row[1:]   # [trophy_weight, super_trophy_weight, max_weight, rarity]
            data_dict[key] = value
    
    return data_dict

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
        trophy_onhook = int(input("是否打开星级上钩提示（1开，0关）功能测试中："))
        setting.write("miao_code="+miao_code+'\n')
        setting.write("log_path="+log_path+'\n')
        setting.write("function="+functions+'\n')
        setting.write('onhook_weight_alert='+str(onhook_weight_alert))
        setting.write('trophy_onhook='+str(trophy_onhook))
else:
    with open("./setting.txt") as setting:
        setting_file = setting.read().split('\n')
        miao_code = setting_file[0].split('=')[1]
        log_path = setting_file[1].split('=')[1]
        functions = setting_file[2].split('=')[1]
        onhook_weight_alert = int(setting_file[3].split('=')[1])
        trophy_onhook = int(setting_file[4].split('=')[1])
print('开始监控日志文件，如需退出请按CTRL+c')

current_log_date = datetime.date.today().strftime("%Y-%m-%d")

fish_data = csv_to_dict('./fish_data.csv')

# 渔获记录表格
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
            current_log_date = current_date
            current_log.close()
            current_log = open(log_path+'/'+current_date+".txt")
            last_pos = 0
            current_log.seek(last_pos)
            current_log.read()
            last_pos = current_log.tell()
        # if not os.path.exists(current_date+'fish.csv'):
        #     current_fish_record.close()
        #     current_fish_record = open(current_date+'fish.csv', 'w')

    current_log.seek(last_pos)
    line = current_log.readline()
    last_pos = current_log.tell()
    time.sleep(1)
    if len(line)>0:
        onhook_match = re.search(r"鱼上钩了.+?鱼信息:【(.+?)】(\d+(?:\.\d+)?)([kg|g]+)",line)
        capture_match = re.search(r"捕获：(?:[^【]*?)【(.+?)】【(.+?)】(?:【(.+?)】)?(\d+(?:\.\d+)?)([公斤|克]+).+?鱼饵:(.[^,]+)",line)
        if onhook_match or capture_match:
            print(line)
        if onhook_match:
            onhook_weight = float(onhook_match.group(2)) if onhook_match.group(3) == 'kg' else float(onhook_match.group(2))/1000
            if trophy_onhook == 1 and onhook_match.group(1) in fish_data and onhook_weight*1000 >= fish_data[onhook_match.group(1)][0]:
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'你的'+('【星级】' if (onhook_weight*1000 >= fish_data[onhook_match.group(1)][0] and onhook_weight*1000 < fish_data[onhook_match.group(1)][1]) else '【蓝冠】')+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！'}))
                n.show_toast("上大鱼了",'你的'+('【星级】' if (onhook_weight*1000 >= fish_data[onhook_match.group(1)][0] and onhook_weight*1000 < fish_data[onhook_match.group(1)][1]) else '【蓝冠】')+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！')
            elif onhook_weight >= onhook_weight_alert:
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'巨大的'+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！'}))
                n.show_toast("上大鱼了",'巨大的'+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！',icon_path="./fish_icons/"+onhook_match.group(1)+".ico")
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
                n.show_toast("捕获了",'渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']',"./fish_icons/"+capture_match.group(1)+".ico")
            elif functions == '2' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠'):
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'上星/蓝了！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'}))
                n.show_toast("捕获了",'上星/蓝了！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']',"./fish_icons/"+capture_match.group(1)+".ico")
            elif functions == '3' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠' or capture_match.group(3) is not None):
                request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":miao_code, "text":'稀有鱼！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'+(('['+capture_match.group(3)+']') if capture_match.group(3) is not None else '')}))
                n.show_toast("捕获了",'稀有鱼！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'+(('['+capture_match.group(3)+']') if capture_match.group(3) is not None else ''),"./fish_icons/"+capture_match.group(1)+".ico")

import os
import tkinter as tk
from tkinter import filedialog
import datetime, time
from win10toast import ToastNotifier
import csv
import matcher
import logging

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
            value = [int(i) for i in row[1:]]   # [trophy_weight, super_trophy_weight, max_weight, rarity]
            data_dict[key] = value
    
    return data_dict

global setting_file
global uid
global log_path
global functions
global onhook_weight_alert
global trophy_onhook

def push():
    logging.basicConfig(filename='./error.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)
    n = ToastNotifier()
    # initialize setting
    if not os.path.exists("./setting.txt"):
        with open("./setting.txt", "w") as setting:
            root = tk.Tk()
            root.withdraw()
            uid = input("请输入uid：")
            print("选择蓑笠翁log文件夹：")
            log_path = filedialog.askdirectory(
                title="Select a folder"  # Customize the dialog title
            )
            functions = input("选择推送消息种类：1.全部，2.上星/蓝，3.稀有（紫标，粉标，星蓝）：")
            onhook_weight_alert = int(input('请输入上钩重量警报：'))
            trophy_onhook = int(input("是否打开星级上钩提示（1开，0关）功能测试中："))
            setting.write("uid="+uid+'\n')
            setting.write("log_path="+log_path+'\n')
            setting.write("function="+functions+'\n')
            setting.write('onhook_weight_alert='+str(onhook_weight_alert))
            setting.write('trophy_onhook='+str(trophy_onhook))
    else:
        with open("./setting.txt") as setting:
            setting_file = setting.read().split('\n')
            uid = setting_file[0].split('=')[1]
            log_path = setting_file[1].split('=')[1]
            functions = setting_file[2].split('=')[1]
            onhook_weight_alert = int(setting_file[3].split('=')[1])
            trophy_onhook = int(setting_file[4].split('=')[1])

    print('开始监控日志文件')

    current_log_date = datetime.date.today().strftime("%Y-%m-%d")

    fish_data = csv_to_dict('./fish_data.csv')


    current_log = open(log_path+'/'+datetime.date.today().strftime("%Y-%m-%d")+".txt")
    last_pos = 0
    current_log.seek(last_pos)
    current_log.read()
    last_pos = current_log.tell()
    cur_matcher = matcher.matcher(uid,functions, onhook_weight_alert, trophy_onhook)
    while True:
        try:
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
            if datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 0:
                cur_matcher.report_fish_amount()
            current_log.seek(last_pos)
            line = current_log.readline()
            last_pos = current_log.tell()
            time.sleep(1)
            if len(line)>0:
                cur_matcher.fish_on_hook_match(line)
                cur_matcher.fish_capture_match(line)
                cur_matcher.missing_parts_match(line)
                cur_matcher.fish_sale_match(line)
        except Exception as e:
            logger.error(e)

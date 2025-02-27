import re
import csv
import requests
from win10toast import ToastNotifier


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



class matcher:
    def __init__(self, uid,function, onhook_weight_alert, trophy_onhook):
        self.fish_data = csv_to_dict('./fish_data.csv')
        self.uid = uid
        self.function = function
        self.onhook_weight_alert = onhook_weight_alert
        self.trophy_onhook = trophy_onhook
        self.n = ToastNotifier()
        self.n.show_toast("启动成功","启动成功，开始监听中...")
        self.fish_amount = {}
        self.appToken = "AT_qAOhemlf0Fg9EIsdcjmRSKuqH6digxMS"


    def fish_on_hook_match(self, line):
        fish_data = self.fish_data
        uid = self.uid
        onhook_weight_alert = self.onhook_weight_alert
        trophy_onhook = self.trophy_onhook
        onhook_match = re.search(r"鱼上钩了.+?鱼信息:【(.+?)】(\d+(?:\.\d+)?)([kg|g]+)",line)
        if onhook_match:
            print(line)
            onhook_weight = float(onhook_match.group(2)) if onhook_match.group(3) == 'kg' else float(onhook_match.group(2))/1000
            if trophy_onhook == 1 and onhook_match.group(1) in fish_data and onhook_weight*1000 >= fish_data[onhook_match.group(1)][0]:
                self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("上"+('【星级】' if (onhook_weight*1000 >= fish_data[onhook_match.group(1)][0] and onhook_weight*1000 < fish_data[onhook_match.group(1)][1]) else '【蓝冠】')+"鱼了,"+onhook_match.group(1)+' '+onhook_match.group(2)+onhook_match.group(3),'你的'+('【星级】' if (onhook_weight*1000 >= fish_data[onhook_match.group(1)][0] and onhook_weight*1000 < fish_data[onhook_match.group(1)][1]) else '【蓝冠】')+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！'))
                self.n.show_toast("上星鱼了",'你的'+('【星级】' if (onhook_weight*1000 >= fish_data[onhook_match.group(1)][0] and onhook_weight*1000 < fish_data[onhook_match.group(1)][1]) else '【蓝冠】')+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！')
            elif onhook_weight >= onhook_weight_alert:
                self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("上大鱼了,"+onhook_match.group(1)+' '+onhook_match.group(2)+onhook_match.group(3),'巨大的'+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！'))
                self.n.show_toast("上大鱼了",'巨大的'+onhook_match.group(1)+'上钩了，重达'+onhook_match.group(2)+onhook_match.group(3)+'，快上号拉鱼！',icon_path="./fish_icons/"+onhook_match.group(1)+".ico")

    def fish_capture_match(self, line):
        uid = self.uid
        functions = self.function
        capture_match = re.search(r"捕获：(?:[^【]*?)【(.+?)】【(.+?)】(?:【(.+?)】)?(\d+(?:\.\d+)?)([公斤|克]+).+?鱼饵:(.[^,]+)",line)
        if capture_match:
            print(line)
            self.fish_amount_stat_update(capture_match.group(1), float(capture_match.group(4)) if capture_match.group(5) == '公斤' else round(float(capture_match.group(4))/1000,3), capture_match.group(6)(-1))
            if functions == '1' and capture_match.group(2) != '普通':
                self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("捕获了 "+capture_match.group(1)+' '+capture_match.group(4)+capture_match.group(5),'渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'))
                self.n.show_toast("捕获了",'渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']',"./fish_icons/"+capture_match.group(1)+".ico")  
            elif functions == '2' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠'):
                self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("捕获了 "+capture_match.group(1)+' '+capture_match.group(4)+capture_match.group(5),'上星/蓝了！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'))
                self.n.show_toast("捕获了",'上星/蓝了！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']',"./fish_icons/"+capture_match.group(1)+".ico")
            elif functions == '3' and (capture_match.group(2) == '星级' or capture_match.group(2) == '蓝冠' or capture_match.group(3) is not None):
                self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("捕获了 "+capture_match.group(1)+' '+capture_match.group(4)+capture_match.group(5),'稀有鱼！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'+(('['+capture_match.group(3)+']') if capture_match.group(3) is not None else '')))
                self.n.show_toast("捕获了",'稀有鱼！渔夫使用了'+capture_match.group(6)[:-1]+'抓住了'+capture_match.group(4)+capture_match.group(5)+'的'+capture_match.group(1)+'['+capture_match.group(2)+']'+(('['+capture_match.group(3)+']') if capture_match.group(3) is not None else ''),"./fish_icons/"+capture_match.group(1)+".ico")
            
    def missing_parts_match(self, line):
        uid = self.uid
        missing_component_match = re.search(r"没有多余的【(.+?)】组件，尝试使用星标组件", line)
        if missing_component_match:
            self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("缺少组件: "+missing_component_match.group(1),"背包里的【"+missing_component_match.group(1)+"】用完了，快去看看吧。"))
            self.n.show_toast("缺少组件","背包里的【"+missing_component_match.group(1)+"】用完了，快去看看吧。")

    def fish_sale_match(self, line):
        uid = self.uid
        fish_sale_match = re.search(r"卖鱼收入：(\d+.\d+)",line)
        if fish_sale_match:
            self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("售出了 "+fish_sale_match.group(1)+'银币',"渔夫售出了"+fish_sale_match.group(1)+"银币"))
            self.n.show_toast("售出了","渔夫售出了"+fish_sale_match.group(1)+"银币")
        self.report_fish_amount()

    def fish_amount_stat_update(self, fish_name, weight, lure):
        fish_amount = self.fish_amount
        if fish_name in fish_amount:
            if lure in fish_amount[fish_name]:
                fish_amount[fish_name][lure][0] += weight
                fish_amount[fish_name][lure][1] += 1
            else:
                fish_amount[fish_name][lure] = [weight, 1]
        else:
            fish_amount[fish_name] = {lure:[weight, 1]}
    def report_fish_amount(self):
        fish_amount = self.fish_amount
        if fish_amount:
            # generate a html bar chart
            script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>'
            script += '<canvas id="myChart" width="400" height="400"></canvas>'
            script += '<script>var ctx = document.getElementById("myChart").getContext("2d");'
            script += 'var myChart = new Chart(ctx, {type: "bar",data: {labels: ['
            for fish in fish_amount:
                script += '"'+fish+'",'
                script = script[:-1]
                script += '],datasets: [{label: "公斤",data: ['
            for fish in fish_amount:
                script += str(sum(fish_amount[fish][lure][0] for lure in fish_amount[fish]))+','
                script = script[:-1]
                script += '],backgroundColor: "rgba(255, 99, 132, 0.2)",borderColor: "rgba(255, 99, 132, 1)",borderWidth: 1},{label: "数量",data: ['
            for fish in fish_amount:
                script += str(sum(fish_amount[fish][lure][1] for lure in fish_amount[fish]))+','
                script = script[:-1]
                script += '],backgroundColor: "rgba(54, 162, 235, 0.2)",borderColor: "rgba(54, 162, 235, 1)",borderWidth: 1}]}'
            script += '});</script>'
            # send report
            self.__post(url="https://wxpusher.zjiecode.com/api/send/message",json=self.__build_json("捕获统计",report))

        # clear fish_amount
        fish_amount.clear()

    def __build_json(self, summary, content):
        return {
                "appToken":self.appToken,#必传
                "content":content,#必传
                #消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度20(微信只能显示20)，可以不传，不传默认截取content前面的内容。
                "summary":summary,
                #内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签，推荐使用这种) 3表示markdown 
                "contentType":2,
                #发送目标的topicId，是一个数组！！！，也就是群发，使用uids单发的时候， 可以不传。
                #发送目标的UID，是一个数组。注意uids和topicIds可以同时填写，也可以只填写一个。
                "uids":[
                    self.uid
                ],
                #是否验证订阅时间，true表示只推送给付费订阅用户，false表示推送的时候，不验证付费，不验证用户订阅到期时间，用户订阅过期了，也能收到。
                #verifyPay字段即将被废弃，请使用verifyPayType字段，传verifyPayType会忽略verifyPay
                "verifyPay":False, 
                #是否验证订阅时间，0：不验证，1:只发送给付费的用户，2:只发送给未订阅或者订阅过期的用户
                "verifyPayType":0 
                }
    
    def __post(self, url, json, max_attempt=5):
        res = {"code":0}
        curr_attempt = 0
        while res["code"] != 1000 and curr_attempt < max_attempt:
            res = requests.post(url=url,json=json).json()
            curr_attempt += 1
        if res["code"] != 1000:
            self.n.show_toast("发送失败","发送失败，请检查网络连接或联系开发人员！")
        return res
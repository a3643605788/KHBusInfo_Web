# https://ibus.tbkc.gov.tw/cms/driving-map

import urllib.request as req
import json
import datetime

# 抓取全部公車資料json檔
def get_bus_json():
    url = "https://ibus.tbkc.gov.tw/cms/api/route"
    re = req.Request(url , headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    })
    with req.urlopen(re) as response:
        BusData = response.read().decode("utf-8")
    BusData = json.loads(BusData)                 #把原始的 JSON 資料解析成字典/列表形式
    return BusData


# 抓取搜尋到的公車資訊
def get_bus_name(BusData,InputBusName):
    busname=[]
    for Get_BusURL in BusData:
        nameZh = ""
        DepartureZh = ""
        DestinationZh = ""
        busURL = "" 
        
        # 公車名稱
        nameZh = "[" + Get_BusURL["NameZh"] + "]"
        nameZh = nameZh + Get_BusURL["ddesc"]

        if InputBusName in nameZh:
            # 公車出發站  
            DepartureZh = Get_BusURL["DepartureZh"]
            # 公車目的地站
            DestinationZh = Get_BusURL["DestinationZh"]
            # 公車代碼(像人的身分證)
            Id = str(Get_BusURL["Id"])
            # 公車 url
            busURL = "https://ibus.tbkc.gov.tw/cms/api/route/" + Id + "/estimate"
            
            busname.append({"nameZh":nameZh,"Id":Id,"BusURL":busURL,"DepartureZh":DepartureZh,"DestinationZh":DestinationZh,"Favorite":0})
    return busname


# 抓取特定一個列表的公車資訊
def get_bus_info(BusURL):

    re = req.Request(BusURL , headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    })
    with req.urlopen(re) as response:
        BusData = response.read().decode("utf-8")
    BusData = json.loads(BusData)                 #把原始的 JSON 資料解析成字典/列表形式    


    bus_timetable = []
    for Get_Bus_Info in BusData:
        ComeTime = ""
        drive = ""
        GoBack = ""
        Ivron = ""
        StopName = ""
        
        # 公車預計到站時間
        ComeTime = Get_Bus_Info["ComeTime"]
        if ComeTime == "":
            ComeTime = "末班離駛"
        # 公車距離站點車程時間
        drive = time_calculate(ComeTime)
        # 判斷公車出發還是回程
        GoBack = Get_Bus_Info["GoBack"]
        # 站牌代碼
        Ivron = Get_Bus_Info["IVRNO"]
        # 公車站名  
        StopName = Get_Bus_Info["StopName"]
        
        bus_timetable.append({"ComeTime":ComeTime,"drive":drive,"GoBack":GoBack,"IVRNO":Ivron,"StopName":StopName})

    return bus_timetable
    
# 計算公車距離站點車程時間
def time_calculate(ComeTime):

    if ComeTime == "末班離駛":
        return "末班離駛"

    # 取得目前時間
    now = datetime.datetime.today().strftime("%H:%M")
    # 將目前時間轉成 datetime.datetime 資料類別
    now = datetime.datetime.strptime(now, "%H:%M")
    # 將公車進站時間轉成 datetime.datetime 資料類別
    ComeTime = datetime.datetime.strptime(ComeTime, "%H:%M")
    
    # 目前距離進站時間還有多久
    ans = ComeTime-now
    # 取商值
    minute = ans.seconds//60

    return minute



# # 輸入公車名稱
# BusName = input()

# # 得到公車原始json檔
# BusData = get_bus_json()

# businfo = get_bus_info("https://ibus.tbkc.gov.tw/cms/api/route/217/estimate")
# for info in businfo:
#     print(info["ComeTime"])
#     print(info["GoBack"])
#     print(info["IVRNO"])
#     print(info["StopName"])
#     print("\n\n")
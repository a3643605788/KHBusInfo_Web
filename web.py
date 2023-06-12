import khbus
import pymongo
from flask import *




# 初始化資料庫連線
client = pymongo.MongoClient("mongodb+srv://root:ap890411@library.gpnikng.mongodb.net/?retryWrites=true&w=majority")
db = client.python_KHbus                   #選擇操作 python_KHbus 資料庫
# 初始化 Flask 伺服器
app = Flask(__name__)
app.secret_key = "any string but secret"

# 首頁(導向搜尋頁面)
@app.route("/")
def home():
    if "email" not in session:
        return render_template("search.html", html_status=0)
    
    collection = db.user
    result = collection.find_one({"email":session["email"]})
    nickname = result["nickname"]
    return render_template("search.html", html_status=1, html_nickname=nickname)

# 導向註冊頁面
@app.route("/btn_signup")
def btn_signup():
    return render_template("signup.html")

# 導向登入頁面
@app.route("/btn_login")
def btn_login():
    return render_template("login.html")

# 判斷是否有登入
@app.route("/member")
def member():
    if "email" in session:
        collection = db.user
        result = collection.find_one({"email":session["email"]})
        nickname = result["nickname"]
        return render_template("member.html", html_nickname=nickname)
    else:
        return redirect("/")

# 註冊
@app.route("/signup", methods=["POST"])
def signup():
    # 從前端接收資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    # 根據接收到的資料，和資料庫互動
    collection = db.user                    #選擇操作 user 集合
    # 檢查會員集合中是否有相同 email 的文件資料
    result = collection.find_one({
        "email":email
    })
    if result != None:
        return redirect("/error?msg=此信箱已被註冊")
    # 把資料放進資料庫完成註冊
    collection.insert_one({
        "nickname":nickname,
        "email":email,
        "password":password
    })
    return redirect("/")

# 登入
@app.route("/login", methods=["POST"])
def login():
    
    # 登入到服務器，獲取用戶名&密碼，然後對比，再記錄訊息，再返回後台頁面。
    email = request.form.get("email")
    password = request.form.get("password")

    # 獲取用戶名&密碼，然後對比，再記錄訊息
    collection = db.user
    result = collection.find_one({
        "$and":[
        {"email":email},
        {"password":password}
        ]
    })
    # 找不到對應的資料，登入失敗，導向到錯誤頁面
    if result==None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    # 登入成功返回後台頁面
    nickname = result["nickname"]
    session["email"] = result["email"]
    return render_template("member.html", html_nickname=nickname)

# 我的最愛
@app.route("/myfavorite")
def myfavorite():

    global bus_list

    bus_list = []

    collection = db.user
    result = collection.find_one({"email":session["email"]})
    nickname = result["nickname"]

    collection = db.favorite

    # 一次取得多筆資料
    cursor = collection.find()
    
    for doc in cursor:
        if doc["email"] == session["email"]:
            nameZh = doc["nameZh"]
            Id = doc["Id"]
            BusURL = doc["BusURL"]
            DepartureZh = doc["DepartureZh"]
            DestinationZh = doc["DestinationZh"]
            Favorite = doc["Favorite"]
            
            bus_list.append({"nameZh":nameZh,"Id":Id,"BusURL":BusURL,"DepartureZh":DepartureZh,"DestinationZh":DestinationZh,"Favorite":Favorite})

    # print("---------------\n",bus_list,"\n\n")
    return render_template("bus_list.html", html_bus_list=bus_list, html_status=1, html_nickname=nickname)



# 取消我的最愛
@app.route("/dislike/<Id>")
def dislike(Id):
    
    global bus_list

    if "email" not in session:
        return redirect("/error?msg=請登入帳號解鎖我的最愛功能")
    
    collection = db.user
    result = collection.find_one({"email":session["email"]})
    nickname = result["nickname"]

    collection = db.favorite

    # 為了更新下面bus_list，所以搜尋剛剛加進資料庫的資料
    result = collection.find_one({
            "$and":[
                {"Id":Id},
                {"email":session["email"]}
            ]
        })

    for index in range(len(bus_list)):
        if result["Id"] == bus_list[index]["Id"]:
            bus_list[index]["Favorite"] = 0
            break
    
    # 刪除集合中的一筆文件資料
    result = collection.delete_one({
            "$and":[
                {"Id":Id},
                {"email":session["email"]}
            ]
        })
    # print("\n\nDislike\n\n",bus_list,"\n")
    return render_template("bus_list.html", html_bus_list=bus_list, html_status=1, html_nickname=nickname)

# 新增我的最愛
@app.route("/like/<Id>")
def like(Id):

    global bus_list

    if "email" not in session:
        return redirect("/error?msg=請登入帳號解鎖我的最愛功能")

    collection = db.user
    result = collection.find_one({"email":session["email"]})
    nickname = result["nickname"]

    # 先添加Id和會員email到資料庫，下面才可以讓本地bus_list找，有沒有加進最愛
    collection = db.favorite
    collection.insert_one({
        "email":session["email"],
        "Id":Id
    })
    
    # 為了更新下面bus_list，所以搜尋剛剛加進資料庫的資料
    result = collection.find_one({
            "$and":[
                {"Id":Id},
                {"email":session["email"]}
            ]
        })
    

    # 把資料庫跟本地bus_list都新增我的最愛
    for index in range(len(bus_list)):
        if result["Id"] == bus_list[index]["Id"]:

            collection.update_one(
                # 篩選條件
                {
                    "$and":[
                        {"Id":Id},
                        {"email":session["email"]}
                    ]
                },
                # 更新的資訊  $set為修改器，修改某筆資料的某幾個值
                {
                    "$set":{
                        "nameZh":bus_list[index]["nameZh"],
                        "BusURL":bus_list[index]["BusURL"],
                        "DepartureZh":bus_list[index]["DepartureZh"],
                        "DestinationZh":bus_list[index]["DestinationZh"],
                        "Favorite":1
                    }
            })

            bus_list[index]["Favorite"] = 1
            break
    # print("\n\nLike\n\n",bus_list,"\n")
    return render_template("bus_list.html", html_bus_list=bus_list, html_status=1, html_nickname=nickname)
        
    

# 輸入資訊異常(error?msg="錯誤訊息")
@app.route("/error")
def error():
    message =  request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", html_message=message)

# 登出
@app.route("/signout")
def signout():
    # 移除 Session 中的會員資訊
    del session["email"]
    return redirect("/")





# 搜尋公車
@app.route("/search")
def search():

    global bus_list

    # 判斷有沒有登入(html_status=0是未登入)
    if "email" not in session:
        BusName = str(request.args.get("BusName"))
        BusData = khbus.get_bus_json()
        bus_list = khbus.get_bus_name(BusData,BusName)
        return render_template("bus_list.html", html_bus_list=bus_list, html_status=0)
    
    collection = db.user
    result = collection.find_one({"email":session["email"]})
    nickname = result["nickname"]
    email = result["email"]

    collection = db.favorite

    BusName = str(request.args.get("BusName"))
    BusData = khbus.get_bus_json()
    bus_list = khbus.get_bus_name(BusData,BusName)



    # 判斷公車有沒有被加進我的最愛
    for index in range(len(bus_list)):
        Id = bus_list[index]["Id"]
        cursor = collection.find({"Id":Id})
        if cursor == None:
            bus_list[index]["Favorite"] = 0
        else:
            for doc in cursor:
                if doc["email"] == email:
                    bus_list[index]["Favorite"] = 1

    # print("Member\n",bus_list)

    return render_template("bus_list.html", html_bus_list=bus_list, html_status=1, html_nickname=nickname)

# 列出公車資訊
@app.route("/bus_timetable/<Id>")
def bustimetable(Id):

    global bus_list

    while True:
        # 公車出發站
        DepartureZh=""
        # 公車目的地站
        DestinationZh=""

        for list in bus_list:
            if Id == list["Id"]:
                DepartureZh = "往" + list["DepartureZh"]
                DestinationZh = "往" + list["DestinationZh"]
                break

        busURL = "https://ibus.tbkc.gov.tw/cms/api/route/" + Id + "/estimate"
        bus_timetable = khbus.get_bus_info(busURL)

        # 判斷有沒有登入(html_status=0是未登入)
        if "email" not in session:
            return render_template("bus_timetable.html",html_bus_timetable=bus_timetable, html_DepartureZh=DepartureZh, html_DestinationZh=DestinationZh, html_status=0)
        
        collection = db.user
        result = collection.find_one({"email":session["email"]})
        nickname = result["nickname"]

        return render_template("bus_timetable.html",html_bus_timetable=bus_timetable, html_DepartureZh=DepartureZh, html_DestinationZh=DestinationZh, html_status=1, html_nickname=nickname)


# 公車資料
bus_list = []
# 判斷有無登入(0:沒有 1:有)
status=0

if __name__ == "__main__":
    app.run(port=3000)
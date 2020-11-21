from vo import cctvVo, tempVo, gasVo, controlVo
from flask import Flask, render_template, request, jsonify, redirect, url_for
from mariadb import dbConnection
from emailService import sendEmail
import os
import datetime
import json
import asyncio
import websockets   # pip install websockets
import cv2, base64  # python
import numpy as np



app = Flask(__name__)	# Flask object Assign to app
#192.168.219.108
db = dbConnection.dbConnection(host='192.168.219.108', id='latte', pw='lattepanda', db_name='test')

slist = "isaac7263@naver.com, juhea0619@naver.com, itit2014@naver.com, rabbit3919@naver.com"

#
"""
async def accept(websocket, path) :
    while True : 
        data = await websocket.recv()
        print(data)

server = websockets.serve(accept, "0.0.0.0", 8080)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
"""
#

# Vo LIST
cctvVo_list = [] # 임시 cctv 리스트
tempVo_list = []  # 온습도 리스트
gasVo_list = [] #  가스 리스트
controlVo_list = [] # control 리스트
#-----------------------------------------------------------------
# db 연결 
def dbConnect():
    return dbConnection.dbConnection(host='192.168.219.108', id='latte', pw='lattepanda', db_name='test')

# ip주소 얻기
def getIp() :
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

#--------------------------------------------------------------------
## controller
# main page
@app.route("/")
def index() :
    # db연결
	return render_template('index.html')
# 회원가입 Sign-Up
@app.route("/signup")
def signup():
    # db연결
    return render_template('signup.html')
# 회원가입 insert
@app.route("/signupInsert", methods=['POST'])
def signupInsert():
    # db연결
    db = dbConnect()

    _id = request.values["_id"]
    # _name = request.form.get('_name')
    _name = request.values["_name"]
    _password = request.values["_password"]

    print(_id, _name, _password)
    # 회원가입
    db.insertMember( _id, _name, _password )
    return render_template('index.html')


# signin [log-in]
@app.route("/signin", methods=['POST'])
def siginin() :
    # db연결
    db = dbConnect()

    if request.method == 'POST' :
         # post 로 보내면 request.form.get으로 받고,
         # get으로 보내는 경우 requst.args.get으로 받음
        _id = request.form.get('_id')  
        _password = request.form.get('_password')
        _ip = getIp()

        print("로그인 시도하는 ID & PW", _id, _password)
        result = db.selectLoginMember(_id, _password)
        print(result)
        return render_template('menu.html', _ip=_ip)

        if ( result[0]['COUNT(*)'] == 1 ) :
            return render_template('menu.html', _ip=_ip)
        else :
            return render_template('index.html')

# menu Home 
@app.route("/menuHome",  methods=['POST', 'GET'])
def menuHome() :
    _ip = getIp()
    return render_template('menu.html', _ip=_ip)


#--------------------------------------------------------------------
# list page
#--------------------------------------------------------------------
# cctv_list page
@app.route("/cctv_list",  methods=['POST', 'GET'])
def cctv_list() :
    # db연결
    db = dbConnect()

    # database에서 값 꺼내기
    dataFrame = db.selectCctv()
    # converting to dict
    data_dict = dataFrame.to_dict()

    cctvVo_list.clear()
    
    print( len(data_dict['c_time']) )
    for i in range( len(data_dict['c_time'] )) :
        obj = cctvVo.cctvVo(data_dict['c_time'][i], data_dict['c_image'][i])
        cctvVo_list.append(obj)

    #for i in range( len( data_dict['c_time'] ) ) :
        #obj = cctvVo.cctvVo( data_dict['c_time'][i] , data_dict['c_image'][ i ])
        #cctvVo_list.append(obj)

    return render_template('cctv_list.html', rows=cctvVo_list)

@app.route("/temp_list",  methods=['POST', 'GET'])
def temp_list() :
    # db연결
    db = dbConnect()

    # database에서 값 꺼내기
    dataFrame = db.selectTemp()
    # converting to dict
    data_dict = dataFrame.to_dict()

    tempVo_list.clear()
    
    for i in range( len( data_dict['t_time'] ) ) :
        obj = tempVo.tempVo(  data_dict['t_time'][ i ],  data_dict['t_temp'][ i ],  data_dict['t_humi'][ i ]  )
        tempVo_list.append(obj)
    
    return render_template('temp_list.html', rows=tempVo_list)

@app.route("/gas_list",  methods=['POST', 'GET'])
def gas_list() :
    # db연결
    db = dbConnect()
    
    # database에서 값 꺼내기
    dataFrame = db.selectGas()
    # converting to dict
    data_dict1 = dataFrame.to_dict()

    gasVo_list.clear()

    for i in range( len( data_dict1['g_time'] ) ) :
        obj = gasVo.gasVo(  data_dict1['g_time'][ i ],  data_dict1['g_gas'][ i ]  )
        gasVo_list.append(obj)
        
    return render_template('gas_list.html', rows=gasVo_list)

# iotControl 통신하기
@app.route("/iotControl", methods=['POST','GET'])
def iotControl() :
    # db연결
    db = dbConnect()

    # database에서 값 꺼내기
    dataFrame = db.selectControl()
    # converting to dict
    control_dict = dataFrame.to_dict()

    controlVo_list.clear()

    for i in range( len(control_dict['code'] ) ) :
        obj = controlVo.controlVo(control_dict['code'][i], control_dict['control'][i], control_dict['onoff'][i], control_dict['value'][i], control_dict['value2'][i], control_dict['startTime'][i], control_dict['endTime'][i])
        controlVo_list.append(obj)

    return render_template('iotControl.html', rows=controlVo_list)

# ajax 비동기 통신으로 전원 ON/OFF 하기
@app.route("/ajax", methods=['POST'])
def ajax() :
    # db연결
    db = dbConnect()

    # 데이터 수신
    data = request.get_json()
    # 데이터 출력
    print(data)
    # value 파싱
    _id = data['id']
    _onoff = data['onoff']

    # 전원 변경
    if (_onoff == 'Y' ) :
        _onoff = "N"
    else :
        _onoff = "Y"
    
    # 실제 변경 업데이트
    print(_id, _onoff)
    db.updateControlOnOff(_id, _onoff)
    
    # database에서 값 꺼내기 : 해당하는 것 하나만
    dataFrame = db.selectControlOne(_id)

    # converting to dict
    control_dict = dataFrame.to_dict()

    # 데이터 출력 및 확인
    print(control_dict)
    return jsonify(result = "success", result2= control_dict)

@app.route("/dust_page",  methods=['POST', 'GET'])
def dust_page() :
    _ip = getIp()
    return render_template('menu.html', _ip=_ip)

#--------------------------------------------------------------------
# From CCTV client / insert
@app.route("/insertCctv", methods=['POST', 'GET'])
def insertCctv() :
    # db연결
    db = dbConnect()

    #now = datetime.datetime.now()
    #nowDatetime =  now.strftime('%Y-%m-%d %H:%M:%S'.encode('unicode-escape').decode())
    c_time = request.values['time'] # 측정 시간
    c_image = request.files['image']  # 이미지 

    # image 파일 저장
    imageFileName = c_time + '.jpg'
    c_image.save(os.path.join( 'static/cctv_img/', imageFileName)) # 파일 저장
    
    # 디비에 저장하기 이전 버전
    #instance = cctvVo.cctvVo(c_time, imageFileName)   # 객체에 저장
    #cctvVo_list.append(instance)
    subject = "[카메라]사람이 감지되었습니다."
    content = "[카메라]사람이 감지되었습니다."
    sendEmail.sendEmail( subject, content )
    # db에 저장
    db.insertCctv(c_time, imageFileName)
    return ""

# From Temperature/Humidity 온습도 클라이언트로부터의 값 얻어서 넣기
@app.route("/insertTemp", methods=['POST', 'GET'])
def insertTemp() :
    # db연결
    db = dbConnect()

    now = datetime.datetime.now()
    nowDatetime =  now.strftime('%Y-%m-%d %H:%M:%S'.encode('unicode-escape').decode())
    
    c_time =nowDatetime         # imsi 현재시간
    c_temp = request.values['temp'] # 온도
    c_hum = request.values['hum'] # 습도
    c_sig1 = request.values['sig1'] #main sensor
    c_sig2 = request.values['sig2'] #sub sensor

    subject = ""
    content = ""
    # 이상감지
    if c_sig1 == "0" and c_sig2 == "1":
        subject = "[온습도]메인센서 이상, 서브센서로 감지합니다."
        content = "[온습도]메인센서 이상, 서브센서로 감지합니다. \n현재 온도 : [%s], 습도 : [%s] 입니다." % (c_temp, c_hum) 
        sendEmail.sendEmail( subject, content )
    elif c_sig1 == "1"  and c_sig2 == "0" :
        subject = "[온습도]서브센서 이상, 메인센서로 감지합니다."
        content = "[온습도]서브센서 이상, 메인센서로 감지합니다.. \n현재 온도 : [%s], 습도 : [%s] 입니다." % (c_temp, c_hum) 
        sendEmail.sendEmail( subject, content )
    elif c_sig1 == "0" and c_sig2 == "0" :
        subject = "온습도]메인센서, 서브센서 이상 센서를 점검하세요."
        content = "[온습도]메인센서, 서브센서 이상, 센서를 점검하세요. "
        sendEmail.sendEmail( subject, content)

    db.insertTemp(c_time, c_temp, c_hum)
    return ""

@app.route("/insertGas", methods=['POST','GET'])
def insertGas() :
    # db연결
    db = dbConnect()

    now = datetime.datetime.now()
    nowDatetime =  now.strftime('%Y-%m-%d %H:%M:%S'.encode('unicode-escape').decode())
    
    c_time =nowDatetime         # imsi 현재시간
    c_gas = request.values["gas"]
    c_sig1 = request.values['flag1'] #main sensor
    c_sig2 = request.values['flag2'] #sub sensor

    subject=""
    content=""
    # 이상감지
    if c_sig1 == "0" and c_sig2 == "1":    
        subject="[Gas]메인센서 이상, 서브센서로 감지합니다."
        content="[Gas]메인센서 이상, 서브센서로 감지합니다. 현재 가스 : [%s] "% c_gas
        sendEmail.sendEmail(subject, content)
    elif c_sig1 == "1"  and c_sig2 == "0" :
        subject="[Gas]서브센서 이상, 메인센서로 감지합니다."
        content="[Gas]서브센서 이상, 메인센서로 감지합니다. 현재 가스 : [%s] "% c_gas
        sendEmail.sendEmail(subject, content)
    elif c_sig1 == "0" and c_sig2 == "0" :
        subject="[Gas]메인센서 이상, 서브센서 이상 | 센서를 점검하세요!"
        content="[Gas]메인센서 이상, 서브센서 이상 | 센서를 점검하세요!"
        sendEmail.sendEmail(subject, content)
    elif c_sig1 =="2" :
        subject="[Gas]가스 누출을 메인센서로 감지했습니다."
        content="[Gas]가스 누출을 메인센서로 감지했습니다.\n현재 가스 : [%s] "% c_gas
        sendEmail.sendEmail(subject, content)
    elif c_sig2 =="2" :
        subject="[Gas]가스 누출을 서브센서로 감지했습니다."
        content="[Gas]가스 누출을 서브센서로 감지했습니다\n현재 가스 : [%s] "% c_gas
        sendEmail.sendEmail(subject, content)

    db.insertGas(c_time, c_gas)
    return ""

#-------------------------------------------------------------------
@app.route("/webhook", methods=['POST'])
def webhook() :
    req = request.get_json(force=True)
    #print(req)
    parameters = req['queryResult']['parameters']
    #print(parameters)
    Device_is = -1
    Power_is = -1
    Sensor_Name_is = -1

    if "Device" in parameters :
        print(parameters['Device'])
        Device = parameters['Device']
        Device_is = 1
    if "Power" in parameters :
        print(parameters['Power'])
        Power = parameters['Power']
        Power_is = 1
    if "Sensor_Name" in parameters :
        print(parameters['Sensor_Name'])
        Sensor_Name = parameters['Sensor_Name']
        Sensor_Name_is =1
    
    if Device_is == 1 and Power_is == 1 :   # 제품을 켜다, 끄다
        if Device == "에어컨" and Power == "켜다" :
            print(Device, Power)
        elif Device == "에어컨" and Power == "끄다" :
            print(Device, Power)
            
    return redirect(url_for('iotControl'))

#--------------------------------------------------------------------
host_addr = "0.0.0.0"
port_num = "8080"
if __name__ == "__main__":
    app.run(host=host_addr, port=port_num, debug=True)
    


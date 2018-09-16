# -*- encoding: utf8 -*-
import requests
import time
import sys
import re as regx
from bs4 import BeautifulSoup as bs

######################################################################
#########################    SETTINGS    #############################
######################################################################

check_time_term = 10        #3초에 한번 확인
id = "your id"           #아이디 입력
pw = "your pw"            #패스워드 입력
reserve_date = '20180922'   #예약 날짜 입력"
time_min = '0910'           #예약 희망 시간 최저
time_max = '1110'           #예약 희망 시간 최대
depart_station = '동탄'
arrive_station = '동대구'


########################    STAION LIST    ###########################
'공주', '광주송정', '김천구미', '나주', '대전', '동대구', '동탄', '목포', '부산', '수서', '신경주', '오송', '울산', '익산', '정읍', '지제', '천안아산'
######################################################################



######################################################################
######################    REQUEST META INFO     ######################
######################################################################

login_referer = "https://etk.srail.co.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000"
login_request_url = "https://etk.srail.co.kr/cmc/01/selectLoginInfo.do?pageId=TK0701000000"
check_seat_url = "https://etk.srail.co.kr/hpg/hra/01/selectScheduleList.do?pageId=TK0101010000"
temporal_session_id = '9TlJyAnoWpw33CTnx1f0yprb10fmr1fTA1vIIrf3UGZaX1e1MXNvjZjAIdSOBXTT'
my_cookie = {
    'JSESSIONID_ETK': temporal_session_id,
    'PCID': '15261430919745926997128',
    'RC_COLOR': '24',
    'RC_RESOLUTION': '1680*1050'
}

station_meta_info = {
    "공주": '0514',
    "광주송정": '0036',
    '김천구미': '0507',
    '나주': '0037',
    '대전': '0010',
    '동대구': '0015',
    '동탄': '0552',
    '목포': '0041',
    '부산': '0020',
    '수서': '0551',
    '신경주': '0508',
    '오송': '0297',
    '울산': '0509',
    '익산': '0030',
    '정읍': '0033',
    '지제': '0553',
    '천안아산': '0502'
}

common_header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "etk.srail.co.kr",
    "Referer": check_seat_url,
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
}

reserve_param = {
    'arvRsStnCd1': '0015', #도착역 코드
    'arvStnConsOrdr1': '000014', #tr에 있음
    'arvStnRunOrdr1': '000004', #tr에 있음
    'crossYn': 'N', # ????
    'dirSeatAttCd1': '000', #tr에 있음
    'dptDt1': '20180525', #날짜
    'dptRsStnCd1': '0551', #출발역 코드
    'dptStnConsOrdr1': '000001', #tr에 있음
    'dptStnRunOrdr1': '000001', #tr에 있음
    'dptTm1': '200000', #tr에 있음
    'etcSeatAttCd1': '000', #??
    'jobId': '1101', #고정인
    'jrnyCnt': '1', #고정인듯
    'jrnySqno1': '001', #tr에 있음
    'jrnyTpCd': '11', #??? 고정인듯
    'locSeatAttCd1': '000', #좌석위치 (조회시 내가 날림)
    'mutMrkVrfCd': None, #???
    'psgGridcnt': '1', #사람수??
    'psgInfoPerPrnb1': '1', #어른
    'psgInfoPerPrnb2': None, #장애인(1~3급)
    'psgInfoPerPrnb3': None, #장애인(4~6급)
    'psgInfoPerPrnb4': None, #노인
    'psgInfoPerPrnb5': None, #얼라
    'psgTpCd1': '1', #어른
    'psgTpCd2': None, #장애인 1~3급
    'psgTpCd3': None, #장애인(4~6급)
    'psgTpCd4': None, #노인
    'psgTpCd5': None, #얼라
    'psrmClCd1': '1', #???
    'reqTime': '1526195770894', #현재 시간
    'rqSeatAttCd1': '015', #좌석 속성 (일반015 / 휠체어 021 / 전동휠체어 028)
    'rsvTpCd': '01', #???
    'runDt1': '20180525', #날
    'scarGridcnt1': None, #???
    'scarNo1': None, #???
    'scarYn1': 'N', #???
    'seatNo1_1': None, #tr안에 있음
    'seatNo1_2': None, #tr안에 있음
    'seatNo1_3': None, #tr안에 있음
    'seatNo1_4': None, #tr안에 있음
    'seatNo1_5': None, #tr안에 있음
    'seatNo1_6': None, #tr안에 있음
    'seatNo1_7': None, #tr안에 있음
    'seatNo1_8': None, #tr안에 있음
    'seatNo1_9': None, #tr안에 있음
    'smkSeatAttCd1': '000', #???
    'stlbTrnClsfCd1': '17', #tr에 있
    'stndFlg': 'N', #??? 입석?
    'totPrnb': '1', #총 사람 수
    'trnGpCd1': '300', #기차 종류 (300: srt)
    'trnNo1': '00369', #기차번호
    'trnOrdrNo1': '6' #???
}

######################################################################
##########################    LOGICS    ##############################
######################################################################

def login(id, pw):
    header = dict(common_header)
    header["Referer"] = login_referer
    header['Content-Type'] = 'application/x-www-form-urlencoded'

    login_success_keyword = 'location.replace(\'/main.do\')'

    login_param = {
        'rsvTpCd': None,
        'goUrl': None,
        'from': None,
        'srchDvCd': '1',
        'srchDvNm': id,
        'hmpgPwdCphd': pw
    }
    response = requests.post(login_request_url, headers = header, params = login_param)

    if response.cookies and response.cookies['JSESSIONID_ETK']:
        print ("get cookie from login response:"+response.cookies['JSESSIONID_ETK'])
        my_cookie["JSESSIONID_ETK"] = response.cookies['JSESSIONID_ETK']

    if response.status_code != 200:
        return False
    elif ('오류' in response.text) or ('실패' in response.text) or ('존재' in response.text):
        return False
    elif login_success_keyword in response.text:
        return True

def reserve(can_reserve_list):
    header = dict(common_header)
    header['Cookie'] = "SR_MB_CD_NO="+str(id) +"; JSESSIONID_ETK="+my_cookie['JSESSIONID_ETK']
    header['Referer'] = check_seat_url

    for tr in can_reserve_list:
        param = set_reserve_param(tr)

        response = requests.post("https://etk.srail.co.kr/hpg/hra/01/checkUserInfo.do?pageId=TK0101010000", headers = header, params = param)
        if not (response.status_code == 200 and "location.replace('/hpg/hra/02/requestReservationInfo.do?pageId=TK0101030000')" in response.text) :
            continue

        response = requests.get("https://etk.srail.co.kr/hpg/hra/02/requestReservationInfo.do?pageId=TK0101030000", headers = header)
        if not (response.status_code == 200 and "location.replace('confirmReservationInfo.do?pageId=TK0101030000')" in response.text):
            continue

        response = requests.get("https://etk.srail.co.kr/hpg/hra/02/confirmReservationInfo.do?pageId=TK0101030000", headers = header)
        if not (response.status_code == 200 and "10분 내에 결제하지 않으면 예약이 취소됩니다" in response.text):
            continue
        print("예약 성공*********************")
        reserve_id = bs(response.text,'html.parser').find('input', attrs={"name":"pnrNo"})
        print(reserve_id)

        return reserve_id
        #예약 성공하면 반환값 리턴하면서 종료
    return False

def set_reserve_param(tr):
    param = dict(reserve_param)

    train_info_list = bs(str(tr), 'html.parser').select("td.trnNo > input")
    train_info_dict = { bs(str(info), 'html.parser').find()['name'].split('[')[0]: bs(str(info),'html.parser').find()['value'] for info in train_info_list }

    param['dptDt1'] = train_info_dict['dptDt']
    param['runDt1'] = train_info_dict['runDt']
    param['arvStnConsOrdr1'] = train_info_dict['arvStnConsOrdr']
    param['arvStnRunOrdr1'] = train_info_dict['arvStnRunOrdr']
    param['arvRsStnCd1'] = train_info_dict['arvRsStnCd']
    param['dirSeatAttCd1'] = '000'
    param['dptRsStnCd1'] = train_info_dict['dptRsStnCd']
    param['dptStnConsOrdr1'] = train_info_dict['dptStnConsOrdr']
    param['dptTm1'] = train_info_dict['dptTm']
    param['jrnySqno1'] = train_info_dict['jrnySqno']
    param['locSeatAttCd1'] = "000"
    param['reqTime'] = int(time.time()*1000) #현재시간
    param['rqSeatAttCd1'] = train_info_dict['seatAttCd']
    param['stlbTrnClsfCd1'] = train_info_dict['stlbTrnClsfCd']
    param['trnGpCd1'] = train_info_dict['trnGpCd']
    param['trnNo1'] = train_info_dict['trnNo']
    param['trnOrdrNo1'] = train_info_dict['trnOrdrNo'] #화면에서 몇번째 라인에 있던 열차인지

    return param

#빈 좌석이 있는지 확인
def checkSeat(start, dest, date, time_min = '000000', time_max = '220000'):
    header = dict(common_header)
    header["Referer"] = "https://etk.srail.co.kr/main.do"
    header['Content-Type'] = 'application/x-www-form-urlencoded'

    param = {
        'chtnDvCd': '1',
        'isRequest': 'Y',
        'psgInfoPerPrnb1': '1',
        'psgInfoPerPrnb2': '0',
        'psgInfoPerPrnb3': '0',
        'psgInfoPerPrnb4': '0',
        'psgInfoPerPrnb5': '0',
        'psgNum': '1',
        'seatAttCd': '015',
        'stlbTrnClsfCd': '05',
        'trnGpCd': '300' #300으로 하면 srt만 나옴, 109는 상관없이 다.
    }
    param['arvRsStnCdNm'] = dest
    param['arvRsStnCd'] = station_meta_info[dest]
    param['dptRsStnCdNm'] = start
    param['dptRsStnCd'] = station_meta_info[start]
    param['dptDt'] = date
    param['dptTm'] = time_min+'0000'

    print("좌석 정보를 조회합니다..")
    response = requests.post(check_seat_url, headers = header, params = param)

    #열차 정보만 가져온다.
    tr_list = bs(response.text, 'html.parser').select("tbody > tr")
    can_reserve_list = []
    for tr in tr_list:
        depart_time = bs(str(tr), "html.parser").find('input', attrs={"name": regx.compile("dptTm*")})['value'] #regular expression
        if int(time_min.ljust(6,'0')) > int(depart_time) or int(depart_time) > int(time_max.ljust(6,'0')):
            print("depart_time:"+depart_time+"은 예약대상이 아닙니다.")
            continue
        td_list = bs(str(tr), "html.parser").select('td')
        if "매진" not in str(td_list[6]):
            print("예약가능: {}, {}".format(td_list[3], td_list[4]))
            can_reserve_list.append(tr)
    return can_reserve_list

def pay(r_id): #r_id : 예약 번호
    #https://etk.srail.co.kr/hpg/hra/03/selectSettleInfo.do?pageId=TK0101040000
    #pnrNo	320180516896562
    print("pay")

def validate_setting_info():
    stations = station_meta_info.keys()
    if (depart_station not in stations) or (arrive_station not in stations):
        print("역 정보가 올바르지 않습니다. 다시 입력하세요")
        sys.exit(1)
    if int(time_min) > int(time_max):
        print("예약 희망 시간대가 비정상적입니다. 다시 입력하세요")
        sys.exit(1)


######################################################################
#########################    MAIN LOGIC    ###########################
######################################################################

if login(id, pw) == False:
    print("----login fail----")
    sys.exit(1)

print ("----login success----")
validate_setting_info()

isRight = input("출발역 = %s, 도착역 = %s, 예약하고자 하는 날짜 = %s, 희망시간대는 %s ~ %s 맞나요?(y/n):"%(depart_station, arrive_station, reserve_date, time_min, time_max))
if (isRight.lower() != 'y') and (isRight.upper() != 'Y'):
    sys.exit(1)

print("예약하고자 하는 날짜 = %s, 희망시간대는 %s ~ %s 로 열차를 검색하기 시작합니다" %(reserve_date, time_min, time_max))

while True:
    can_reserve_list = checkSeat(depart_station, arrive_station, reserve_date, time_min, time_max)
    if len(can_reserve_list) > 0:
        #예약 성공하면 종료
        reserve_result = reserve(can_reserve_list)
        if reserve_result:
            break
    time.sleep(check_time_term)

print ('end!!')
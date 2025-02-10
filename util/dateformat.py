import datetime
from pytz import timezone

def dateformat(timesec: int):

    d = datetime.datetime.fromtimestamp(timesec)
    

    tstr = d.strftime("%Y/%m/%d %H:%M:%S")
    return tstr

def timenow():
    shanghai = timezone("Asia/Shanghai")
    loc_d = shanghai.localize(datetime.datetime.now())
    return int(round(loc_d.timestamp()))

# if __name__=="__main__":
#     t = timenow()
#     print(dateformat(t))
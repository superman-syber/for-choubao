from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import json

today = datetime.now()
week_list = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
week = week_list[today.weekday()]

start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]



weather_apikey = "f98b35e5362346d2bc7576ae09a368df";


if city is None or weather_apikey is None:
    print('没有城市行政区域编码或者apikey')
    city_id = None
else:
    city_idurl = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={weather_apikey}"
    city_data = json.loads(requests.get(city_idurl).content.decode('utf-8'))['location'][0]
    city_id = city_data.get("id")
    city_name = city_data.get('name')

#print(city_id,city_name)
#print("-------------------------------")


def get_weather():
    if city_id is None:
        return None
    weatherurl = f"https://devapi.qweather.com/v7/weather/3d?location={city_id}&key={weather_apikey}&lang=zh"
    weather = json.loads(requests.get(weatherurl).content.decode('utf-8'))["daily"][0]
    return weather

#print(get_weather())
#print("-------------------------------")

def get_realtimeweather():
  if city_id is None:
    return None
  realtimeweatherurl = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={weather_apikey}&lang=zh"
  realtimeweather = json.loads(requests.get(realtimeweatherurl).content.decode('utf-8'))["now"]["temp"]
  return realtimeweather

#print(get_realtimeweather())
#print("-------------------------------")



# 获取空气质量
def get_airqu():
  air_quurl = f'https://devapi.qweather.com/v7/air/5d?location={city_id}&key={weather_apikey}&lang-zh'
  if city_id is None:
    return None
  airqu = json.loads(requests.get(air_quurl).content.decode('utf-8'))["daily"][0]
  return airqu

#print(get_airqu())
#print("-------------------------------")



#def get_weather():
#  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
#  res = requests.get(url).json()
#  weather = res['data']['list'][0]
#  return weather['weather'], math.floor(weather['temp']), math.floor(weather['high']), math.floor(weather['low'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days



def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

weather = get_weather()
airqu = get_airqu()
realtimeweather = get_realtimeweather()
wm = WeChatMessage(client)
# wea, temperature, max_temperature, min_temperature = get_weather()
data = {
  "date":{
    "value":today.strftime('%Y-%m-%d')
  },
  "week":{
    "value":week
  },
  "city":{
    "value":city
  },
  "weather":{
#    "value":wea
    "value": f"白天：{weather['textDay']}  ;  夜晚：{weather['textNight']}",
    "color": get_random_color()
  },
  # 湿度
  "humidity": {
    "value": weather['humidity']+"%",
    "color": get_random_color()
  },
  # 风力
  "wind": {
    "value": f"白天：{weather['windScaleDay']}级  ;  夜晚：{weather['windScaleNight']}级",
    "color": get_random_color()
  },

  "air_data": {
    "value": airqu['aqi'],
    "color": get_random_color()
  },
  # 空气质量
  "air_quality": {
    "value": airqu['category'],
    "color": get_random_color()
  },
  # 实时温度
  "temperature": {
    "value": realtimeweather,
    "color": get_random_color()
  },
  # 最高温
  "highest": {
    "value": weather['tempMax'],
    "color": get_random_color()
  },
  # 最低温度
  "lowest": {
    "value": weather['tempMin'],
    "color": get_random_color()
  },

#  "temperature":{
#    "value":temperature
#  },
#  "max_temperature":{
#    "value":max_temperature
#  },
#  "min_temperature":{
#    "value":min_temperature
#  },
  "love_days":{
    "value":get_count(),
    "color": get_random_color()
  },
  "birthday_left":{
    "value":get_birthday(),
    "color": get_random_color()
  },
  "words":{
    "value":get_words(), 
    "color":get_random_color()
  }
}
#print(data)
#print("--------------------")


res = wm.send_template(user_id, template_id, data)
print(res)

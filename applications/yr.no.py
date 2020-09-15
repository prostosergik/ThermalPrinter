from yr.libyr import Yr
from lib.portipc40 import ThermalPrinter
import json 
from pprint import pprint
from datetime import datetime
import math
from time import sleep



p = ThermalPrinter()
p.rf()
# p.linefeed()


location = "Montenegro/Other/Sveti_Spas~3339206"
location_xyz=(18.856194, 42.304875, 280)


weather = Yr(location_name=location)
# weather = Yr(location_name=location, forecast_link='forecast_hour_by_hour')
forecast = weather.dictionary.get('weatherdata', {}).get('forecast', {}).get('tabular',{}).get('time',[])


if forecast:
	soon = forecast[0] 

	p.justify('c')
	p.bold()
	p.size(1, 1)
	p.print(datetime.now().strftime("%-d %B %Y"))
	p.print(datetime.now().strftime("%H:%M"))
	p.linefeed()
	p.size(2,2)
	p.print(soon.get('temperature', {}).get('@value')+chr(31)+"/ "+soon.get('precipitation', {}).get('@value')+"mm")
	p.bold(False)
	p.size(1,2)
	p.print(soon.get('windSpeed', {}).get('@name') + " " + ('%.1f' % (float(soon.get('windSpeed', {}).get('@mps')) * 3.6)).rstrip('0').rstrip('.') +"km/h, "+ soon.get('windDirection', {}).get('@code') )

	p.linefeed()

	p.rf()
	for x in range(1, 5):
		fc = forecast[x]
		t_from = datetime.strptime(fc.get('@from'), '%Y-%m-%dT%H:%M:%S').strftime("%H")
		t_to = datetime.strptime(fc.get('@to'), '%Y-%m-%dT%H:%M:%S').strftime("%H")

		
		fc_str = "%s-%s:  %s, %skm/h %s,%smm" % (
					t_from,
					t_to,
					fc.get('temperature', {}).get('@value')+chr(31),
					('%.1f' % (float(fc.get('windSpeed',     {}).get('@mps')) * 3.6)).rstrip('0').rstrip('.').rjust(4),
					fc.get('windDirection', {}).get('@code').rjust(3),
					('%.1f' % float(fc.get('precipitation', {}).get('@value'))).rstrip('0').rstrip('.').rjust(3),
				)
		# print(fc_str)
		p.print(fc_str)

	p.linefeed(3)



# now = weather.now(as_json=True)

# obj_now = json.loads(now) 

# # pprint(obj_now)


# print("Forecast: " + obj_now.get('symbol', {}).get('@name'))
# print("Perciptations: "+obj_now.get('precipitation', {}).get('@value'))
# print("Wind: "+obj_now.get('windSpeed', {}).get('@name') +" "+ obj_now.get('windDirection', {}).get('@name') )
# print(obj_now.get('temperature', {}).get('@value'))


# # for forecast in weather.forecast():
# for forecast in weather.forecast(as_json=True):
#     print(forecast)


# p.size(3,2)
# # p.d_height()
# p.justify('c')
# p.print("5678/912")


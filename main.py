from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)
device.contrast(0)

from requests import get, ConnectionError
from xmltodict import parse
from datetime import timedelta, datetime
from os import environ

url = "http://demo.hafas.de/openapi/vbb-proxy/departureBoard?id=900002200&accessId=" + environ['VBB_ACCESS_ID']

def showDepartures(d):
  hbf = []
  turm = []
  wedding = []

  for bus in d['DepartureBoard']['Departure']:
    date_time_obj = datetime.strptime(bus.get('@rtDate', bus.get('@date')) + ' ' + bus.get('@rtTime', bus.get('@time')),  '%Y-%m-%d %H:%M:%S')
    minutes = int((date_time_obj - datetime.now()).total_seconds() / 60)
    if (minutes > 1):
      if (bus['@direction'] == 'S+U Hauptbahnhof'):
        hbf.append(minutes)
      if (bus['@direction'] == 'S+U Jungfernheide'):
        wedding.append(minutes)
      if (bus['@direction'] == 'S+U Pankow'):
        turm.append(minutes)
  msg = 'hbf: ' + ", ".join(map(str, hbf[:2])) + '  ' + 'wedding: ' + ", ".join(map(str, wedding[:2])) + '  ' + 'turm: ' + ", ".join(map(str, turm[:2]))
  show_message(device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.03)

try:
  lastUpdate = datetime.fromtimestamp(0000000000)
  while True:
    if lastUpdate < datetime.now() - timedelta(seconds=120):
      try:
        r = get(url)
      except ConnectionError:
        print("No internet connection available.")
        show_message(device, 'No internet connection available.', fill="white", font=proportional(LCD_FONT), scroll_delay=0.03)
      d = parse(r.content)
      lastUpdate = datetime.now()
    showDepartures(d)
except Exception as e:
  print(e)
  s = str(e)
  show_message(device, s, fill="white", font=proportional(LCD_FONT), scroll_delay=0.03)
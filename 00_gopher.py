import network
import socket
import time

from machine import Pin

led = Pin("LED", Pin.OUT)

ssid = '<put your ssid here>'
password = '<put your password here>'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 10 
while max_wait > 0: 
    if wlan.status() < 0 or wlan.status() >= 3: 
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3: 
    raise RuntimeError('network connection failed')
    print(wlan.status)
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )


html = """i                     		null.host	1
i		null.host	1
i        MMMMML   MMM                WMMMW		null.host	1
i        MMMMMML MMMMM   AMMMMMMA     WMMW     AMMMMMMA		null.host	1
i        MMMMM  W  MMMM MMA   WMMA    WMM     AMW   MMMM		null.host	1
i        MMMMMM   AWWWW MMMMMMMMMM   AMM      WMMMMMMMMW		null.host	1
i        MMMMMMM        WMMMM  WWWW WMMMMMMMW WMM   AMMW		null.host	1
i        WMMMMW          WV              VMMV      WMMV		null.host	1
i		null.host	1
i		null.host	1
i                       +mala's gopherhole		null.host	1
i		null.host	1
i             ==== Last updated: October, 15th 2022 ====		null.host	1
i		null.host	1
i ==== About ====		null.host	1
0Joshua	/users/mala/joshua	sdf.org	70
0+mala	/users/mala/me	sdf.org	70
i		null.host	1
i ==== Phlog ====		null.host	1
02022-10-15 - Repair	/users/mala/phlog/2022-10-15 - Repair	sdf.org	70
02022-10-08 - September	/users/mala/phlog/2022-10-08 - September	sdf.org	70
02022-09-10 - Twine	/users/mala/phlog/2022-09-10 - Twine	sdf.org	70
1Archive	/users/mala/phlog	sdf.org	70
i____________________________________________________________________________		null.host	1
i                            Gophered by Gophernicus/101 on NetBSD/amd64 9.1		null.host	1
.
"""

f = open('gophermap', 'w')
f.write(html)
f.close()

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 70)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
led.value(1)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            print(line)
            if not line or line == b'\r\n':
                break
        response = html
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        led.value(0)

    except OSError as e:
        cl.close()
        print('connection closed')


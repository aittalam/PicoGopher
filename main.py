import network
import socket
import time
import errno
import os
import uasyncio as asyncio

from picogopher import PicoGopher
from picohttp import PicoHTTP

from machine import Pin

onboard = Pin("LED", Pin.OUT)

# ------------------ CONFIG --------------------

# your WiFi's essid
wifi_essid = 'JOIN ¯\_(ツ)_/¯ ME'
wifi_password = None

# default ports for servers
http_port = 80
gopher_port = 70

# enable the experimental HTTP server
enable_http_server = False


# ----------------------------------------------

def start_AP(essid, pw):
    '''
        Runs as WiFi AP and returns its own IP.
        Requires WPA2 AES auth if both essid and pw
        are provided, no auth if pw is None.
    '''
    
    ap = network.WLAN(network.AP_IF)
    if pw is None:
        ap.config(essid=essid, security=0)
    else:
        ap.config(essid=essid, password=pw)

    ap.active(True)
    return ap.ifconfig()[0]


# --------------- HERE BE MAIN -----------------

async def main():
    print('[i] Connecting to Network...')
    fqdn = start_AP(wifi_essid, wifi_password)
    print(f'    Connection successful: listening on {fqdn}')

    print('[i] Starting up servers...')
    gopher_server = PicoGopher(fqdn, gopher_port)
    asyncio.create_task(asyncio.start_server(gopher_server.listener, "0.0.0.0", gopher_port))
    print('    Gopher')
    
    if enable_http_server:
        http_server = PicoHTTP(fqdn, http_port)
        asyncio.create_task(asyncio.start_server(http_server.listener, "0.0.0.0", http_port))
        print('    HTTP')

    print('[i] Ready.')

    while True:
        onboard.on()
        print("heartbeat")
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(120)
        
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()


import socket
import errno
import os
import uasyncio as asyncio
import ssl

# from picodisplay import PicoDisplay
from picowifi import PicoWiFi
from picopower import PicoPower
from picogopher import PicoGopher
from picogemini import PicoGemini
from picohttp import PicoHTTP
from picodns import run_dns_server
from config import Config

from machine import Pin

onboard = Pin("LED", Pin.OUT)


# --------------- HERE BE MAIN -----------------

async def main():
    cfg = Config()
    
    print('[i] Connecting to Network...')
    wifi = PicoWiFi(essid = cfg.WiFi.ESSID,
                    password = cfg.WiFi.password,
                    access_point = cfg.WiFi.enable_AP)

    server_ip = wifi.start()
    print(f'    Connection successful: listening on {server_ip}')

    print('[i] Starting up servers...')
    gopher_server = PicoGopher(server_ip, cfg.Gopher.port)
    asyncio.create_task(asyncio.start_server(gopher_server.listener, "0.0.0.0", cfg.Gopher.port))
    print('    Gopher')
    
    if cfg.HTTP.enabled:
        http_server = PicoHTTP(server_ip, cfg.HTTP.port)
        asyncio.create_task(asyncio.start_server(http_server.listener, "0.0.0.0", cfg.HTTP.port))
        print('    HTTP')

    if cfg.Gemini.enabled:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cfg.SSL.cert_file, cfg.SSL.key_file)
        gemini_server = PicoGemini(server_ip, cfg.Gemini)
        asyncio.create_task(asyncio.start_server(gemini_server.listener, "0.0.0.0", cfg.Gemini.port, ssl=context))
        print('    Gemini')

    if cfg.CaptivePortal.enabled:
        asyncio.create_task(run_dns_server(server_ip))
        print('    DNS')

    if cfg.Battery.enable_power_readings:
        pp = PicoPower(cfg.Battery.adc_vin,
                       cfg.Battery.conversion_factor,
                       cfg.Battery.full_battery,
                       cfg.Battery.empty_battery,
                       cfg.Battery.power_log_file)
        
    if cfg.Display.enabled:
        # set up the screen
        pd = PicoDisplay(
            essid = cfg.WiFi.ESSID,
            ip = server_ip,
            gopher_port = cfg.Gopher.port,
            http_port = cfg.HTTP.port,
            enable_http_server = cfg.HTTP.enable,
            enable_captive_portal = cfg.CaptivePortal.enable
            )
        pd.refresh_screen()


    print('[i] Ready.')


    while True:
        # blink led
        onboard.on()
        await asyncio.sleep(0.25)
        onboard.off()
        
        # do a power reading if enabled
        if cfg.Battery.enable_power_readings:
            # log power reading
            tm, voltage, percentage = pp.log_power_reading()

            # display power reading if display is enabled
            if cfg.Display.enabled:
                pd.update_voltage(tm, voltage, percentage)

            # put PicoGopher to sleep if power is below threshold
            if cfg.Battery.enable_sleep and voltage < cfg.Battery.powersave_threshold:
                message = f"=== Battery level below {cfg.Battery.powersave_threshold}V threshold:"
                message += f" sleeping for {cfg.Battery.sleep_time} seconds...\n"
                with open(cfg.Battery.power_log_file, "a") as f:
                    f.write(message)
                print(message, end="")

                # turn the wifi off
                wifi.stop()
                # deepsleep for battery_sleep_time seconds
                machine.deepsleep(1000*cfg.Battery.sleep_time)

        # sleep for a while
        await asyncio.sleep(60)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()


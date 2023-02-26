import socket
import time
import errno
import os
import uasyncio as asyncio

# from picodisplay import PicoDisplay
from picowifi import PicoWiFi
from picopower import PicoPower
from picogopher import PicoGopher
from picohttp import PicoHTTP
from picodns import run_dns_server

from machine import Pin, ADC

onboard = Pin("LED", Pin.OUT)

# ------------------ CONFIG --------------------

# your WiFi's essid
wifi_essid = 'JOIN ¯\_(ツ)_/¯ ME'
wifi_password = None

# default ports for servers
http_port = 80
gopher_port = 70

# enable HTTP server - experimental
enable_http_server = True

# enable captive portal - SUPER experimental :-)
enable_captive_portal = False
SERVER_IP = '192.168.4.1'


# -- battery --
# set the following to True if you want to log battery
# power and enable automatic deep sleep when battery level
# is below a given threshold
enable_power_readings = False

# adc_vin is the pin from which we read the system input voltage
# (change to 29 for Pico Lipo shim!)
adc_vin = ADC(28)

# As we read a 16 bits uint from adc_vin, we are going to get
# values up to 65535 for a 3.3V input (max input voltage).
# We further multiply by 2 to compensate for the voltage divider
# circuit (2 identical 100KOhm resistors in my custom circuit).
# NOTE that conversion_factor = 3 * 3.3 / 65535 for Pico Lipo shim,
# see https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/pico_lipo_shim/battery_pico.py        
conversion_factor = 2 * 3.3 / 65535

# Reference voltages for a full/empty battery, in volts
# NOTE that they could vary by battery size/manufacturer,
# so you will likely have to adjust them
full_battery = 4.0
empty_battery = 2.8

# To define the threshold below I have looked at the voltage
# value that corresponds to ~15' of battery life. If we pass
# this threshold, we should put the device to sleep and
# periodically check whether the battery has been recharged
# enough before we restart it
battery_powersave_threshold = 3.3
battery_sleep_time = 1200

# specifies where to log power readings (no logging if None)
power_log_file = "gopher/picopower.log"

# -- display --
enable_display = False


# --------------- HERE BE MAIN -----------------

async def main():
    print('[i] Connecting to Network...')
    wifi = PicoWiFi()
    fqdn = wifi.start()
    print(f'    Connection successful: listening on {fqdn}')

    print('[i] Starting up servers...')
    gopher_server = PicoGopher(fqdn, gopher_port)
    asyncio.create_task(asyncio.start_server(gopher_server.listener, "0.0.0.0", gopher_port))
    print('    Gopher')
    
    if enable_http_server:
        http_server = PicoHTTP(fqdn, http_port)
        asyncio.create_task(asyncio.start_server(http_server.listener, "0.0.0.0", http_port))
        print('    HTTP')

    if enable_captive_portal:
        asyncio.create_task(run_dns_server(SERVER_IP))
        print('    DNS')

    if enable_power_readings:
        pp = PicoPower(adc_vin, conversion_factor, full_battery, empty_battery, power_log_file)
        
    if enable_display:
        # set up the screen
        pd = PicoDisplay(
            essid = wifi_essid,
            ip = fqdn,
            gopher_port = gopher_port,
            http_port = http_port,
            enable_http_server = enable_http_server,
            enable_captive_portal = enable_captive_portal
            )
        pd.refresh_screen()


    print('[i] Ready.')

    # used to detect a system restart (e.g. for logging)
    just_started = True

    while True:
        # blink led
        onboard.on()
        await asyncio.sleep(0.25)
        onboard.off()
        
        # do a power reading if enabled
        if enable_power_readings:
            tm = time.localtime()
            voltage = pp.voltage()
            percentage = pp.percentage(voltage)

            message = '%04d-%02d-%02d %02d:%02d:%02d Lipo voltage: %.2f (%03d%%)\n' % (
                            tm[0], tm[1], tm[2],
                            tm[3], tm[4], tm[5],
                            voltage, percentage)

            if just_started:
                if machine.reset_cause == 3:
                    cause = "deepsleep"
                else:
                    cause = "reboot"
                restart_message = f"=== System restarted (waking up from {cause}) ===\n"
                print(restart_message, end="")

            print(message, end="")
        
            # log if enabled
            if power_log_file is not None:
                with open(power_log_file, "a") as f:
                    if just_started:
                        f.write(restart_message)
                    f.write(message)

            just_started = False

            # display power reading if display is enabled
            if enable_display:
                pd.update_voltage(tm, voltage, percentage)

            # put PicoGopher to sleep if power is below threshold
            if voltage < battery_powersave_threshold:
                message = f"=== Battery level below {battery_powersave_threshold}V threshold:"
                message += f" sleeping for {battery_sleep_time} seconds...\n"
                with open(power_log_file, "a") as f:
                    f.write(message)
                print(message, end="")

                # turn the wifi off
                wifi.stop()
                # deepsleep for battery_sleep_time seconds
                machine.deepsleep(1000*battery_sleep_time)

        # sleep for a while
        await asyncio.sleep(60)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()


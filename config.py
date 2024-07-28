from machine import ADC

class Config:
    
    class WiFi:
        ESSID = 'JOIN ¯\_(ツ)_/¯ ME'
        password = None
        # enable Access Point
        enable_AP = True

    class Gopher:
        enabled = True
        port = 70

    class HTTP:
        # enable HTTP server - experimental
        enabled = True
        port = 80

    class CaptivePortal:
        # enable captive portal - SUPER experimental :-)
        enabled = False
    
    
    class Battery:
        # set the following to True if you want to log battery
        # power and enable automatic deep sleep when battery level
        # is below a given threshold
        enable_power_readings = True
        # specifies where to log power readings (no logging if None)
        power_log_file = "gopher/picopower.log"

        # adc_vin is the pin from which we read the system input voltage
        # (change to 29 for Pico Lipo shim!)
        pico_lipo = False

        if pico_lipo:
            adc_vin = ADC(29)
        else:
            adc_vin = ADC(28)

        # As we read a 16 bits uint from adc_vin, we are going to get
        # values up to 65535 for a 3.3V input (max input voltage).
        # We further multiply by 2 to compensate for the voltage divider
        # circuit (2 identical 100KOhm resistors in my custom circuit).
        # NOTE that conversion_factor = 3 * 3.3 / 65535 for Pico Lipo shim,
        # see https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/pico_lipo_shim/battery_pico.py        
        if pico_lipo:
            conversion_factor = 3 * 3.3 / 65535
        else:
            conversion_factor = 2 * 3.3 / 65535

        # Reference voltages for a full/empty battery, in volts
        # NOTE that they could vary by battery size/manufacturer,
        # so you will likely have to adjust them
        full_battery = 4.0
        empty_battery = 2.8

        ### SLEEP (ー。ー) zzz
        # put the pico to sleep when power goes below a given threshold
        enable_sleep = False

        # To define the threshold below I have looked at the voltage
        # value that corresponds to ~15' of battery life. If we pass
        # this threshold, we should put the device to sleep and
        # periodically check whether the battery has been recharged
        # enough before we restart it
        powersave_threshold = 3.3
        sleep_time = 1200

    
    class Display:
        enabled = False


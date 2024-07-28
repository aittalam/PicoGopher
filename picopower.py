from machine import ADC
import time
import machine


class PicoPower:
        
    def __init__(self,
                 adc_vin,
                 conversion_factor,
                 full_battery_voltage,
                 empty_battery_voltage,
                 log_file = None
                 ):
        
        self._adc_vin = adc_vin
        self._conversion_factor = conversion_factor
        self._full_battery = full_battery_voltage
        self._empty_battery = empty_battery_voltage
        self._log_file = log_file
        self._just_started = True
                
    
    def voltage(self):
        ''' reads the voltage in adc_vin and converts it
            to get the actual battery voltage '''
        return self._adc_vin.read_u16() * self._conversion_factor


    def percentage(self, voltage):
        ''' converts battery voltage to percentage, according
            to the reference full/empty battery voltages '''
        percentage = 100 * ((voltage - self._empty_battery) / (self._full_battery - self._empty_battery))

        return 100.00 if percentage > 100 else percentage


    def log_power_reading(self):
        # performs a power reading, prints, logs, and returns data
        tm = time.localtime()
        voltage = self.voltage()
        percentage = self.percentage(voltage)


        if self._just_started:
            if machine.reset_cause == 3:
                cause = "deepsleep"
            else:
                cause = "reboot"
            restart_message = f"=== System restarted (waking up from {cause}) ===\n"
            print(restart_message, end="")


        message = '%04d-%02d-%02d %02d:%02d:%02d Lipo voltage: %.2f (%03d%%)\n' % (
                    tm[0], tm[1], tm[2],
                    tm[3], tm[4], tm[5],
                    voltage, percentage)

        print(message, end="")

        # log if enabled
        if self._log_file is not None:
            with open(self._log_file, "a") as f:
                if self._just_started:
                    f.write(restart_message)
                f.write(message)

        self._just_started = False

        return(tm, voltage, percentage)
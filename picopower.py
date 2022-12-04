from machine import ADC

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
                
    
    def voltage(self):
        ''' reads the voltage in adc_vin and converts it
            to get the actual battery voltage '''
        return self._adc_vin.read_u16() * self._conversion_factor


    def percentage(self, voltage):
        ''' converts battery voltage to percentage, according
            to the reference full/empty battery voltages '''
        percentage = 100 * ((voltage - self._empty_battery) / (self._full_battery - self._empty_battery))

        return 100.00 if percentage > 100 else percentage

    
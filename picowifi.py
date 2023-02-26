import network
import time

class PicoWiFi:
        
    def __init__(self,
                 essid = 'JOIN ¯\_(ツ)_/¯ ME',
                 password = None,
                 access_point = True
                 ):
        
        self._essid = essid
        self._password = password
        self._access_point= access_point


    def start(self):
        
        if self._access_point:
            # Runs as WiFi AP and returns its own IP
            # (no auth if pw is None, WPA2 AES auth otherwise)
            ap = network.WLAN(network.AP_IF)
            if self._password is None:
                ap.config(essid=self._essid, security=0)
            else:
                ap.config(essid=self._essid, password=self._password)

            ap.active(True)
            
            ip = ap.ifconfig()[0]
            self._wifi = ap
        
        else:
            # Connects to existing WiFi
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            print("Connecting: ", end="")
            wlan.connect(self._essid, self._password)

            # Wait for connect or fail
            max_wait = 10 
            while max_wait > 0: 
                if wlan.status() < 0 or wlan.status() >= 3: 
                    break
                max_wait -= 1
                print(".", end="")
                time.sleep(1)

            # Handle connection error
            if wlan.status() != 3: 
                raise RuntimeError('Network connection failed')
                print(wlan.status)
            else:
                print('Connected.')
                ip = wlan.ifconfig()[0]
                self._wifi = wlan

        return ip
    

    def stop(self):
        # see https://github.com/micropython/micropython/issues/9136#issuecomment-1430252794
        self._wifi.deinit()
from picographics import PicoGraphics, DISPLAY_INKY_PACK

class PicoDisplay:
    
    def __init__(self,
                 font = 'bitmap6',
                 essid = 'JOIN ¯\_(ツ)_/¯ ME',
                 ip = '192.168.4.1',
                 gopher_port = 70,
                 http_port = 80,
                 enable_http_server = False,
                 enable_captive_portal = False
                 ):
        # set up the display
        self._display = PicoGraphics(DISPLAY_INKY_PACK)
        self._display.set_update_speed(3)
        self._WIDTH, self._HEIGHT = self._display.get_bounds()
        self.set_font(font)

        # store attributes
        self._essid = essid
        self._ip = ip
        self._gopher_port = gopher_port
        self._http_port = http_port
        self._enable_http_server = enable_http_server
        self._enable_captive_portal = enable_captive_portal
        self._voltage_string = ""
        

    def set_font(self, font):
        self._font = font
        self._display.set_font(self._font)
        
    def clear_screen(self):
        self._display.set_pen(15)
        self._display.clear()
        self._display.set_pen(0)
        self._display.update()

    def add_text(self, text, x, y, scale=2):
        self._display.text(text, x, y, scale=scale)

    def show_text(self, text, x=10, y=10, scale=2):
        ''' mainly used for testing '''
        self.clear_screen()
        self.add_text(text, x, y, scale=scale)
        self._display.update()
        
    def refresh_screen(self):
        self.clear_screen()
        self.add_text(f"   === PicoGopher v1.1 ===", 10, 10)
        self.add_text(f"ESSID: {self._essid}", 10, 30)
        self.add_text(f"IP: {self._ip}", 10, 50)
        services = f"[G:{self._gopher_port}] "
        services += f"[H:{self._http_port if self._enable_http_server else 'OFF'}]"
        services += f" [D:{53 if self._enable_captive_portal else 'OFF'}]"
        self.add_text(services, 10, 70)
        self.add_text(f"{self._voltage_string}", 10, 90)
        self._display.update()

    def update_voltage(self, tm, voltage, percentage):
        msg = '%04d%02d%02d %02d:%02d %.2fV (%.2f%%)' % (tm[0], tm[1], tm[2], tm[3], tm[4], voltage, percentage)
        self._voltage_string = msg
        self.refresh_screen()


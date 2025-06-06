import smbus2
import time

class LCDDisplay:
    def __init__(self, address=LCD_ADDRESS, width=LCD_WIDTH, rows=LCD_ROWS):
        self.address = address
        self.bus = smbus2.SMBus(1)
        self.width = width
        self.rows = rows
        
        # Initialize display
        self.write_cmd(0x33)  # Initialize
        self.write_cmd(0x32)  # Set to 4-bit mode
        self.write_cmd(0x06)  # Cursor move direction
        self.write_cmd(0x0C)  # Turn cursor off
        self.write_cmd(0x28)  # 2 line display
        self.write_cmd(0x01)  # Clear display
        time.sleep(0.2)
        
    def write_cmd(self, cmd):
        high_nibble = cmd & 0xF0
        low_nibble = (cmd << 4) & 0xF0
        for nibble in [high_nibble, low_nibble]:
            self.bus.write_byte_data(self.address, nibble | 0x04, nibble | 0x00)
            time.sleep(0.0001)
            
    def write_data(self, data):
        high_nibble = data & 0xF0
        low_nibble = (data << 4) & 0xF0
        for nibble in [high_nibble, low_nibble]:
            self.bus.write_byte_data(self.address, nibble | 0x05, nibble | 0x01)
            time.sleep(0.0001)
            
    def display_string(self, string, line=1):
        if line == 1:
            self.write_cmd(0x80)
        elif line == 2:
            self.write_cmd(0xC0)
            
        for char in string.ljust(self.width)[:self.width]:
            self.write_data(ord(char))
            
    def clear(self):
        self.write_cmd(0x01)
        time.sleep(0.2)
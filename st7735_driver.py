from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from luma.core.render import canvas
import RPi.GPIO as GPIO
import time
import os
import sys

# GPIO Pin definitions for easier modification
BL_PIN = 4       # Backlight pin
DC_PIN = 24      # Data/Command pin
RST_PIN = 25     # Reset pin

# SPI interface definition
SPI_PORT = 0     # SPI port
SPI_DEVICE = 0   # SPI device (CE0)

KEY_PIN = 17     # Button pin

class Screen:
    def __init__(self, rotation=1, bgr=True, h_offset=0, v_offset=0, contrast=0x70):
        self.height = 128
        self.width = 160
        self.rotation = rotation
        self.bgr_mode = bgr
        self.h_offset = h_offset
        self.v_offset = v_offset
        self.contrast = contrast
        self.dc_pin = DC_PIN
        self.rst_pin = RST_PIN
        
        try:
            print("Initializing SPI interface...")
            # Hardware reset for ST7735 chip
            self.reset_display()
            
            # Initialize SPI
            self.serial = spi(port=SPI_PORT, device=SPI_DEVICE, gpio_DC=self.dc_pin, gpio_RST=self.rst_pin)
            print("SPI interface initialized successfully")
            print(f"Parameter settings: rotation={self.rotation}, BGR={self.bgr_mode}, h_offset={self.h_offset}, v_offset={self.v_offset}, contrast=0x{self.contrast:02X}")
            
            # Initialize ST7735 device
            self.device = st7735(self.serial, width=self.width, height=self.height, 
                                 rotate=self.rotation, h_offset=self.h_offset, 
                                 v_offset=self.v_offset, bgr=self.bgr_mode)
            # Set contrast
            self.device.contrast(self.contrast)
            print("ST7735 display initialized successfully")
            self.buffer = Image.new(self.device.mode, self.device.size)
            print("Image buffer created successfully")
        except Exception as e:
            print(f"Error initializing display: {e}")
            print("Please check if SPI interface is enabled, you can enable it via 'sudo raspi-config'")
            print("Make sure you can see SPI devices using the 'ls -l /dev/spidev*' command")
            print("Check connections and try running this program with 'sudo'")
            sys.exit(1)
            
        # Use default fonts available on Raspberry Pi
        self.fontType = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Common Raspberry Pi font
        self.fontTypeEN = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Common Raspberry Pi font
        
        # Check if font files exist
        if not os.path.exists(self.fontType):
            print(f"Warning: Font file {self.fontType} not found, trying fallback fonts")
            # Try other possibly existing fonts
            fallback_fonts = [
                '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'
            ]
            
            for font in fallback_fonts:
                if os.path.exists(font):
                    self.fontType = font
                    self.fontTypeEN = font
                    print(f"Using fallback font: {font}")
                    break
            else:
                # If all common fonts don't exist, use PIL's default font
                print("Warning: All fallback fonts do not exist, using default font")
                self.fontSize = 16  # Default font is usually smaller
                self.font = ImageFont.load_default()
                self.draw = ImageDraw.Draw(self.buffer)
                return
                
        self.fontSize = 24
        try:
            self.font = ImageFont.truetype(self.fontType, self.fontSize)
            print(f"Successfully loaded font: {self.fontType}")
        except Exception as e:
            print(f"Error loading font: {e}, using default font")
            self.font = ImageFont.load_default()
            
        self.draw = ImageDraw.Draw(self.buffer)
    
    def reset_display(self):
        """Hardware reset for ST7735 chip"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            
            # Reset sequence
            GPIO.output(self.rst_pin, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.rst_pin, GPIO.LOW)
            time.sleep(0.1)  # Reset pulse
            GPIO.output(self.rst_pin, GPIO.HIGH)
            time.sleep(0.1)  # Wait for chip to stabilize
            
            print("ST7735 chip hardware reset completed")
        except Exception as e:
            print(f"Error resetting ST7735 chip: {e}")

    def initGPIO(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(BL_PIN, GPIO.OUT)
            print("GPIO initialized successfully")
        except Exception as e:
            print(f"GPIO initialization error: {e}")
            print("Root privileges may be required, try using 'sudo' to run this program")

    def closeGPIO(self):
        try:
            GPIO.cleanup()
            print("GPIO cleanup completed")
        except Exception as e:
            print(f"GPIO cleanup error: {e}")

    def openScreen(self):
        try:
            GPIO.output(BL_PIN, GPIO.HIGH)
            print("Screen backlight turned on")
        except Exception as e:
            print(f"Error turning on screen backlight: {e}")

    def closeScreen(self):
        try:
            GPIO.output(BL_PIN, GPIO.LOW)
            print("Screen backlight turned off")
        except Exception as e:
            print(f"Error turning off screen backlight: {e}")
            
    def setContrast(self, contrast):
        try:
            self.contrast = contrast
            self.device.contrast(contrast)
            print(f"Contrast set to: 0x{contrast:02X}")
        except Exception as e:
            print(f"Error setting contrast: {e}")

    def drawRect(self, x, y, w, h, color='black', outline=None):
        try:
            self.draw.rectangle((x, y, x+w, y+h), outline=outline, fill=color)
            self.device.display(self.buffer)
        except Exception as e:
            print(f"Error drawing rectangle: {e}")

    def drawCircle(self, x, y, radius, color='white', outline=None):
        try:
            self.draw.ellipse((x-radius, y-radius, x+radius, y+radius), outline=outline, fill=color)
            self.device.display(self.buffer)
        except Exception as e:
            print(f"Error drawing circle: {e}")

    def drawLine(self, x0, y0, x1, y1, color='white', width=1):
        try:
            self.draw.line((x0, y0, x1, y1), fill=color, width=width)
            self.device.display(self.buffer)
        except Exception as e:
            print(f"Error drawing line: {e}")

    def drawPoint(self, x, y, color='white'):
        try:
            self.draw.point((x, y), fill=color)
            self.device.display(self.buffer)
        except Exception as e:
            print(f"Error drawing point: {e}")

    def drawDemo(self):
        try:
            self.draw.rectangle((10,10,10+20,10+20), outline="white", fill="green")
            self.draw.text((30, 40), "Hello World", fill="red")
            self.draw.text((10, 70), "http://xfxuezhang.cn", "white")
            self.device.display(self.buffer)
            print("Demo graphics drawn")
        except Exception as e:
            print(f"Error drawing demo graphics: {e}")
    
    def drawColorTest(self):
        try:
            # Draw RGB color test bars
            self.clearScreen()
            # Red bar
            self.draw.rectangle((0, 0, self.width, 40), fill="red")
            # Green bar
            self.draw.rectangle((0, 40, self.width, 80), fill="green")
            # Blue bar
            self.draw.rectangle((0, 80, self.width, 120), fill="blue")
            # White labels
            self.draw.text((5, 15), "RED", fill="white")
            self.draw.text((5, 55), "GREEN", fill="white")
            self.draw.text((5, 95), "BLUE", fill="white")
            self.device.display(self.buffer)
            print("Color test graphics drawn")
        except Exception as e:
            print(f"Error drawing color test: {e}")
    
    def drawChessboard(self):
        try:
            self.clearScreen()
            block_size = 16  # Chessboard square size
            for x in range(0, self.width, block_size):
                for y in range(0, self.height, block_size):
                    # Alternately draw black and white squares
                    color = "white" if ((x // block_size) + (y // block_size)) % 2 == 0 else "black"
                    self.draw.rectangle((x, y, x + block_size, y + block_size), fill=color)
            self.device.display(self.buffer)
            print("Chessboard test pattern drawn")
        except Exception as e:
            print(f"Error drawing chessboard test: {e}")

    def drawImage(self, image_path, x=0, y=0):
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                # Resize image if it's too large
                if img.width > self.width or img.height > self.height:
                    img = img.resize((min(img.width, self.width), min(img.height, self.height)))
                # Paste the image onto our buffer
                self.buffer.paste(img, (x, y))
                self.device.display(self.buffer)
                print(f"Image {image_path} displayed")
            else:
                print(f"Image file {image_path} not found")
        except Exception as e:
            print(f"Error displaying image: {e}")

    def drawText(self, x, y, msg, color='white', fontSize=None, fontType=None):
        try:
            if fontType and os.path.exists(fontType):
                newType = fontType
            else:
                newType = self.fontTypeEN
                
            newSize = fontSize if fontSize else self.fontSize
            
            # Check if using default font
            if hasattr(self, 'font') and self.font == ImageFont.load_default():
                font = self.font
            else:
                font = ImageFont.truetype(newType, newSize)
                
            # Calculate text width to prevent overflow
            text_width = min(len(msg)*newSize/2, self.width-x)
            self.drawRect(x, y, text_width, newSize, 'black')
            self.draw.text((x, y), msg, font=font, fill=color)
            self.device.display(self.buffer)
        except Exception as e:
            print(f"Error in drawText: {e}")

    def clearScreen(self, color='black'):
        try:
            self.draw.rectangle(self.device.bounding_box, outline=None, fill=color)
            self.device.display(self.buffer)
            print("Screen cleared")
        except Exception as e:
            print(f"Error clearing screen: {e}")

    def showInfo(self):
        try:
            self.clearScreen()
            self.drawText(18, 20, 'Xiaofeng Senior')
            self.drawText(5, 45, 'The Big Bang Theory')
            self.drawText(20, 80, "xfxuezhang.cn", "red", fontSize=12)
            print("Info displayed")
        except Exception as e:
            print(f"Error displaying info: {e}")
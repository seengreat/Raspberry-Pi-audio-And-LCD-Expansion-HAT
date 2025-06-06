import os
import sys
import time
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from luma.core.render import canvas

# Import our driver module
from st7735_driver import Screen, BL_PIN, DC_PIN, RST_PIN, SPI_PORT, SPI_DEVICE, KEY_PIN

# Test different display configurations
def test_screen_configurations():
    # Configuration parameters: rotation, bgr, h_offset, v_offset, contrast
    configurations = [
        # Default configuration modified to BGR=True
        (1, True, 0, 0, 0x70),
        # Other common configurations
        (0, True, 0, 0, 0x70),  # Rotation 0 degrees
        (2, True, 0, 0, 0x70),  # Rotation 180 degrees
        (3, True, 0, 0, 0x70),  # Rotation 270 degrees
        (1, False, 0, 0, 0x70),  # RGB mode
        (1, True, 0, 0, 0xA0),   # High contrast
        (1, True, 1, 1, 0x70),   # 1 pixel offset
        (1, True, 2, 3, 0x70),   # Larger offset
    ]
    
    for i, (rotation, bgr, h_offset, v_offset, contrast) in enumerate(configurations):
        print(f"\nTesting configuration #{i+1}: rotation={rotation}, BGR={bgr}, h_offset={h_offset}, v_offset={v_offset}, contrast=0x{contrast:02X}")
        
        screen = None
        try:
            # Initialize and test
            screen = Screen(rotation=rotation, bgr=bgr, h_offset=h_offset, v_offset=v_offset, contrast=contrast)
            screen.initGPIO()
            screen.openScreen()
            
            # Draw test patterns
            screen.drawColorTest()
            print("Please observe RGB color bars on the screen...")
            time.sleep(3)
            
            screen.drawChessboard()
            print("Please observe black and white chessboard pattern...")
            time.sleep(3)
            
            screen.drawDemo()
            print("Please observe test text on the screen...")
            time.sleep(3)
            
            input(f"Configuration #{i+1} test complete. If the screen displayed correctly, press Enter to continue to the next configuration, or press Ctrl+C to exit...")
        
        except KeyboardInterrupt:
            print("Test interrupted by user")
            if screen:
                screen.closeGPIO()
            return
                
        except Exception as e:
            print(f"Error during configuration #{i+1} test: {e}")
        
        finally:
            if screen:
                screen.closeGPIO()
    
    print("All configurations tested")


# Try different SPI devices (CE0/CE1)
def test_spi_devices():
    print("\nTesting different SPI device configurations")
    
    for device in [0, 1]:  # Try device=0 (CE0) and device=1 (CE1)
        print(f"\nTesting SPI device={device} (corresponding to {'CE0' if device==0 else 'CE1'})...")
        
        try:
            # Initialize SPI with different device parameter
            print("Initializing SPI interface...")
            GPIO.setmode(GPIO.BCM)
            # Hardware reset
            GPIO.setup(RST_PIN, GPIO.OUT)
            GPIO.output(RST_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(RST_PIN, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(RST_PIN, GPIO.HIGH)
            time.sleep(0.1)
            
            serial = spi(port=SPI_PORT, device=device, gpio_DC=DC_PIN, gpio_RST=RST_PIN)
            device_obj = st7735(serial, width=160, height=128, rotate=1, h_offset=0, v_offset=0, bgr=True)
            device_obj.contrast(0x70)
            
            # Create a simple image for testing
            with canvas(device_obj) as draw:
                draw.rectangle((0, 0, 160, 40), fill="red")
                draw.rectangle((0, 40, 160, 80), fill="green")
                draw.rectangle((0, 80, 160, 128), fill="blue")
                draw.text((10, 10), f"CE{device}", fill="white")
            
            print(f"SPI device={device} test image drawn")
            time.sleep(3)
            
            input(f"SPI device={device} test complete. If the screen displayed, press Enter to continue...")
            
        except Exception as e:
            print(f"Error testing SPI device={device}: {e}")
        
        finally:
            GPIO.cleanup()

# Test button and color switching
def test_key_color_change():
    print("\nButton color change test")
    print("Press the button to change screen color")
    print("Press Ctrl+C to exit the test")
    
    # Initialize color list
    colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"]
    color_index = 0
    
    screen = None
    try:
        # Initialize screen
        screen = Screen()
        screen.initGPIO()
        screen.openScreen()
        
        # Initialize button
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(KEY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set as pull-up input
        
        # Display the first color
        screen.clearScreen(color=colors[color_index])
        print(f"Current color: {colors[color_index]}")
        
        last_button_state = GPIO.input(KEY_PIN)
        
        # Main loop
        while True:
            # Read button state
            button_state = GPIO.input(KEY_PIN)
            
            # Detect button press (level change from high to low)
            if button_state == 0 and last_button_state == 1:
                # Button pressed, change color
                color_index = (color_index + 1) % len(colors)
                screen.clearScreen(color=colors[color_index])
                print(f"Button pressed, switching color to: {colors[color_index]}")
                time.sleep(0.2)  # Simple debounce
            
            last_button_state = button_state
            time.sleep(0.05)  # Short delay to reduce CPU usage
            
    except KeyboardInterrupt:
        print("\nButton test interrupted by user")
    except Exception as e:
        print(f"Button test error: {e}")
    finally:
        if screen:
            screen.closeGPIO()
        GPIO.cleanup()  # Ensure GPIO is cleaned up
        print("Button test complete")

# Test drawing functions
def test_drawing_functions():
    print("\nDrawing functions test")
    print("This will demonstrate various drawing capabilities")
    
    screen = None
    try:
        # Initialize screen
        screen = Screen()
        screen.initGPIO()
        screen.openScreen()
        
        # Clear screen to start
        screen.clearScreen()
        time.sleep(1)
        
        # Draw points
        print("Drawing points...")
        for x in range(0, 160, 10):
            screen.drawPoint(x, 10, color="red")
            time.sleep(0.05)
        time.sleep(2)
        
        # Draw lines
        print("Drawing lines...")
        screen.clearScreen()
        for i in range(0, 128, 10):
            screen.drawLine(0, i, 159, 127-i, color="green", width=1)
            time.sleep(0.1)
        time.sleep(2)
        
        # Draw rectangles
        print("Drawing rectangles...")
        screen.clearScreen()
        for i in range(10, 60, 10):
            screen.drawRect(80-i, 64-i, i*2, i*2, color="blue", outline="white")
            time.sleep(0.2)
        time.sleep(2)
        
        # Draw circles
        print("Drawing circles...")
        screen.clearScreen()
        colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
        for i, color in enumerate(colors):
            screen.drawCircle(80, 64, 50-i*8, color=color)
            time.sleep(0.3)
        time.sleep(2)
        
        # Draw text
        print("Drawing text...")
        screen.clearScreen()
        screen.drawText(10, 10, "Hello, World!", color="white", fontSize=16)
        screen.drawText(10, 30, "LCD Display", color="yellow", fontSize=16)
        screen.drawText(10, 50, "Test Pattern", color="cyan", fontSize=16)
        screen.drawText(10, 70, "Raspberry Pi", color="green", fontSize=16)
        screen.drawText(10, 90, "ST7735 LCD", color="red", fontSize=16)
        time.sleep(4)
        
        print("Drawing functions test complete")
        
    except KeyboardInterrupt:
        print("\nDrawing test interrupted by user")
    except Exception as e:
        print(f"Drawing test error: {e}")
    finally:
        if screen:
            screen.closeGPIO()
        print("Drawing test complete")

if __name__ == '__main__':
    print("="*50)
    print("ST7735 LCD Screen Test Program")
    print("="*50)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("Warning: This program may require root privileges to access GPIO and SPI")
        print("It's recommended to run with 'sudo python lcd_app.py'")
        
    # Check if SPI is enabled
    if not os.path.exists('/dev/spidev0.0') and not os.path.exists('/dev/spidev0.1'):
        print("Error: SPI device files not detected")
        print("Please enable SPI by running 'sudo raspi-config' then select 'Interface Options' -> 'SPI' -> 'Yes'")
        print("Restart your Raspberry Pi after enabling")
        print("If already enabled but still seeing this error, check your hardware connections")
        sys.exit(1)
    
    print("\nSelect test mode:")
    print("1: Standard Test - Run basic display test")
    print("2: Configuration Test - Test multiple display configurations to find the best settings")
    print("3: Hardware Check - Check connections and backlight")
    print("4: Button Color Change Test")
    print("5: Drawing Functions Test")
    
    try:
        choice = input("Enter option (1-5): ")
        
        if choice == '2':
            # Test multiple screen configurations
            test_screen_configurations()
        elif choice == '3':
            # Hardware check mode
            print("Hardware check mode - Testing backlight only")
            screen = None
            try:
                # Create Screen instance
                screen = Screen()
                screen.initGPIO()  
                
                # Backlight test
                print("Testing backlight - You should see the screen backlight change")
                for _ in range(5):  # Blink backlight 5 times
                    print("Backlight ON")
                    screen.openScreen()  # Use the driver's method instead of directly operating GPIO
                    time.sleep(1)
                    print("Backlight OFF")
                    screen.closeScreen()  # Use the driver's method instead of directly operating GPIO
                    time.sleep(1)
                
                # Turn backlight on at the end
                print("Test complete, keeping backlight on")
                screen.openScreen()
                time.sleep(1)
            except Exception as e:
                print(f"Backlight test error: {e}")
            finally:
                # Clean up GPIO
                if screen:
                    screen.closeGPIO()
                print("Hardware test complete")
        
        elif choice == '4':
            # Test button color change
            test_key_color_change()
        elif choice == '5':
            # Test drawing functions
            test_drawing_functions()
        else:
            # Default or option 1 - Standard test
            screen = None  # Initialize screen variable to ensure it can be used in finally block
            try:
                print("Initializing screen...")
                screen = Screen()  # Using default parameters, now defaulting to BGR=True
                print("Initializing GPIO...")
                screen.initGPIO()
                print("Opening screen...")
                screen.openScreen()
                print("Displaying color test...")
                screen.drawColorTest()
                time.sleep(2)
                print("Displaying chessboard test...")
                screen.drawChessboard()
                time.sleep(2)
                print("Displaying demo...")
                screen.drawDemo()
                time.sleep(2)
                print("Clearing screen...")
                screen.clearScreen()
                print(f"Screen size: {screen.width}x{screen.height}")
                print("Displaying info...")
                screen.showInfo()
                screen.drawText(5, 125, 'Total Captures=', color='green', fontSize=18)
                screen.drawText(85, 125, str(1), color='red', fontSize=18)
                time.sleep(2)
                screen.drawText(85, 125, str(2), color='red', fontSize=18)
                print("Program execution complete")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                print("Cleaning up GPIO...")
                if screen:  # Check if screen has been initialized
                    screen.closeGPIO()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        GPIO.cleanup()  # Ensure GPIO is cleaned up
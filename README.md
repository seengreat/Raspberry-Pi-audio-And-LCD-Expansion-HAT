# Raspberry Pi Audio and LCD Expansion Board

## 1. Introduction
This expansion board provides extended audio and LCD functionality for the Raspberry Pi.

## 2. Installation Tutorial

### 2.1 Raspberry Pi OS Flashing
This test uses the **Raspberry Pi 4B**. Before installation, you need to install an operating system on the Raspberry Pi. The system version used in the current test is:
```plaintext
Linux raspberrypi 6.12.20+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.20-1+rpt1~bpo12+1 (2025-03-19) aarch64 GNU/Linux 
```
**Note**: This kernel version may be special. Please ensure compatibility. After the system boots up, you can use the `uname -a` command to confirm if the system version matches.

### 2.2 Audio Driver

#### 2.2.1 Disable Default Raspberry Pi Audio
To use the audio functionality of the expansion board, you need to disable the default audio of the Raspberry Pi. Execute the following command to open the configuration file:
```bash
sudo nano /boot/firmware/config.txt
```
In the opened file, find the line `dtparam=audio=on`, add a `#` at the beginning to change it to `#dtparam=audio=on`. After the modification, press `Ctrl + C`, then enter `Y` to save and exit.

#### 2.2.2 Install WM8960 Driver
Navigate to the directory containing the `wm8960_install.sh` file, grant execution permissions to the installation script, and execute it:
```bash
chmod 777 wm8960_install.sh
sudo ./wm8960_install.sh
```

#### 2.2.3 Reboot and Check Driver Loading Status
After the installation is complete, reboot the Raspberry Pi. After installing the wm8960 module and booting up, check if the driver is loaded successfully:
```bash
sudo reboot
# Wait for the boot to complete
```

#### 2.2.4 Sound Card Detection
Use the following commands to detect sound card information:
```bash
# View the sound card list
cat /proc/asound/cards
# View sound card device file information
ls /dev/snd/ -lh
```
Among them, `Controlc0` plays a control role; `PcmC0D0P` represents the playback channel of Card0 Device0; `PcmC2D0C` represents the recording channel of Card2 Device0. A sound card can have multiple devices, and each device can have playback and recording channels.

You can also use the following commands to view playback and recording sound card information respectively:
```bash
# View playback sound card information
aplay -l
# View recording sound card information
arecord -l
```

### 2.3 LCD Driver

#### 2.3.1 Enable Raspberry Pi SPI
Run the following command to enter the Raspberry Pi configuration interface:
```bash
sudo raspi-config
```
In the configuration interface, select **Interfacing Options → SPI → Yes** to enable the SPI kernel driver. After enabling, reboot the Raspberry Pi:
```bash
sudo reboot
```

#### 2.3.2 Install Dependencies
Execute the following commands to install the dependencies required for the LCD driver:
```bash
sudo apt install python3-luma.lcd 
sudo apt-get install python3 python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 -y 
sudo apt-get install libtiff-dev -y 
```

#### 2.3.3 Grant Permissions
Grant the user `pi` access permissions to SPI, GPIO, and I2C:
```bash
sudo usermod -a -G spi,gpio,i2c pi
```

## 3. Usage Instructions

### 3.1 Audio Usage

#### 3.1.1 Recording
Use the following command to record audio. The recorded audio file will be named `test.wav`:
```bash
sudo arecord -D hw:0,0 -f S32_LE -r 16000 -c 2 test.wav
```

#### 3.1.2 Playback
Use the following command to play the audio file `test.wav`. The same command is used for headphone playback:
```bash
sudo aplay -Dhw:0 test.wav
```

### 3.2 LCD Usage
Execute the test script directly:
```bash
python3 lcd_app.py
```
After executing the script, follow the prompts to enter any number between 1 and 5 in the command line, then press Enter. Different numbers represent different parameter settings.

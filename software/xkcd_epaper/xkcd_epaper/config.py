import spidev
import RPi.GPIO as GPIO
import time
import subprocess

from itertools import zip_longest

# Pin definition
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24
SERVO_PIN = 18

# SPI device, bus = 0, device = 0
SPI = spidev.SpiDev(0, 0)
try:
    result = subprocess.check_output(
        ["cat", "/sys/module/spidev/parameters/bufsiz"]
    )
    SPI_BUFFER_SIZE = int(result.strip())
except Exception:
    # small, but should do the trick
    SPI_BUFFER_SIZE = 512

# Display resolution
EPD_WIDTH = 400
EPD_HEIGHT = 300
EPD_BUFFER_SIZE = EPD_WIDTH * EPD_HEIGHT // 8
EPD_WHITE_IMAGE = [0xFF for i in range(0, EPD_BUFFER_SIZE)]
EPD_BLACK_IMAGE = [0x00 for i in range(0, EPD_BUFFER_SIZE)]

# EPD4IN2B commands
PANEL_SETTING = 0x00
POWER_SETTING = 0x01
POWER_OFF = 0x02
POWER_OFF_SEQUENCE_SETTING = 0x03
POWER_ON = 0x04
POWER_ON_MEASURE = 0x05
BOOSTER_SOFT_START = 0x06
DEEP_SLEEP = 0x07
DATA_START_TRANSMISSION_1 = 0x10
DATA_STOP = 0x11
DISPLAY_REFRESH = 0x12
DATA_START_TRANSMISSION_2 = 0x13
VCOM_LUT = 0x20
W2W_LUT = 0x21
B2W_LUT = 0x22
W2B_LUT = 0x23
B2B_LUT = 0x24
PLL_CONTROL = 0x30
TEMPERATURE_SENSOR_CALIBRATION = 0x40
TEMPERATURE_SENSOR_SELECTION = 0x41
TEMPERATURE_SENSOR_WRITE = 0x42
TEMPERATURE_SENSOR_READ = 0x43
VCOM_AND_DATA_INTERVAL_SETTING = 0x50
LOW_POWER_DETECTION = 0x51
TCON_SETTING = 0x60
RESOLUTION_SETTING = 0x61
GSST_SETTING = 0x65
GET_STATUS = 0x71
AUTO_MEASURE_VCOM = 0x80
VCOM_VALUE = 0x81
VCM_DC_SETTING = 0x82
PARTIAL_WINDOW = 0x90
PARTIAL_IN = 0x91
PARTIAL_OUT = 0x92
PROGRAM_MODE = 0xA0
ACTIVE_PROGRAM = 0xA1
READ_OTP_DATA = 0xA2
POWER_SAVING = 0xE3


def delay_ms(delaytime):
    """ small wrapper around time.sleep() """
    time.sleep(delaytime / 1000.0)


def grouper(iterable, n, fillvalue=None):
    """ split an iterable in groups of n items

    shamelessly copied from https://docs.python.org/3/library/itertools.html
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def send_command(command):
    """ send a command to the display """
    GPIO.output(DC_PIN, GPIO.LOW)
    SPI.writebytes([command])


def send_data_byte(data):
    """ sends one byte of data to the display """
    GPIO.output(DC_PIN, GPIO.HIGH)
    SPI.writebytes([data])


def send_data_list(data):
    """ send lot of data to the display

    the installed version of spidev doesn't have the writebytes2 function;
    this is a pure python implementation. The buffer size is only half of
    the size reported
    """
    GPIO.output(DC_PIN, GPIO.HIGH)
    for buffer in grouper(data, SPI_BUFFER_SIZE):
        SPI.writebytes([b for b in buffer if b is not None])

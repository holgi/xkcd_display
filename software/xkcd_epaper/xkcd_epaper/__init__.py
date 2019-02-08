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

# SPI device, bus = 0, device = 0
SPI = spidev.SpiDev(0, 0)
try:
    result = subprocess.check_output(["cat", "/sys/module/spidev/parameters/bufsiz"])
    SPI_BUFFER_SIZE = int(result.strip())
except subprocess.CalledProcessError:
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


class EPD:
    """ Interface for the Waveshare ePaper 4.2" display """

    def send_command(self, command):
        """ send a command to the display """
        GPIO.output(DC_PIN, GPIO.LOW)
        SPI.writebytes([command])

    def send_data_byte(self, data):
        """ sends one byte of data to the display """
        GPIO.output(DC_PIN, GPIO.HIGH)
        SPI.writebytes([data])

    def send_data_list(self, data):
        """ send lot of data to the display

        the installed version of spidev doesn't have the writebytes2 function;
        this is a pure python implementation. The buffer size is only half of
        the size reported
        """
        GPIO.output(DC_PIN, GPIO.HIGH)
        for buffer in grouper(data, SPI_BUFFER_SIZE):
            SPI.writebytes([b for b in buffer if b is not None])

    def init(self):
        """ initialize the display """

        # setup gpio and spi
        print("setup gpio and spi")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)
        SPI.max_speed_hz = 2000000
        SPI.mode = 0b00

        self.reset()

        print("setup commands")
        self.send_command(BOOSTER_SOFT_START)
        self.send_data_byte(0x17)
        self.send_data_byte(0x17)
        self.send_data_byte(0x17)  # 07 0f 17 1f 27 2F 37 2f
        self.send_command(POWER_ON)
        self.wait_until_idle()
        self.send_command(PANEL_SETTING)
        self.send_data_byte(0x0F)  # LUT from OTP

        print("clear: send 1")
        self._send_white_image(DATA_START_TRANSMISSION_1)


    def reset(self):
        """ hardware reset

        setting the reset pin from high to low resets the module
        """
        print("reset")
        for value in (GPIO.HIGH, GPIO.LOW, GPIO.HIGH):
            GPIO.output(RST_PIN, value)
            delay_ms(200)

    def clear(self):
        """ clear the display with a white image """
        print("clear: send 2")
        self._send_white_image(DATA_START_TRANSMISSION_2)
        print("clear: refresh")
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def display(self, pixels):
        """ display an image

        the pixel values should amount to a length of 400 x 300 items
        """
        print("display: send 2")
        self.send_command(DATA_START_TRANSMISSION_2)
        buffer = self._buffer_from_pixels(pixels)
        self.send_data_list(buffer)
        print("display: refresh")
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def sleep(self):
        """ send the display into sleep """
        self.send_command(POWER_OFF)
        self.wait_until_idle()
        self.send_command(DEEP_SLEEP)
        self.send_data_byte(0xA5)

    def wait_until_idle(self):
        """ wait for the display """
        while GPIO.input(BUSY_PIN) == 0:  # 0: idle, 1: busy
            delay_ms(100)

    def _buffer_from_pixels(self, pixels):
        """ generator: yield buffer values from pixel list """
        for pixel_group in grouper(pixels, 8):
            byte = 0xFF
            for group_pos, pixel_value in enumerate(pixel_group):
                if pixel_value == 0:
                    byte &= ~(0x80 >> group_pos)
            yield byte

    def _send_white_image(self, transmission):
        """ sends all white pixels using a transmission channel """
        print("sending white")
        self.send_command(transmission)
        self.send_data_list(EPD_WHITE_IMAGE)


import RPi.GPIO as GPIO

from .config import (
    RST_PIN,
    DC_PIN,
    CS_PIN,
    BUSY_PIN,
    SERVO_PIN,
    SPI,
    BOOSTER_SOFT_START,
    POWER_ON,
    PANEL_SETTING,
    DATA_START_TRANSMISSION_1,
    DATA_START_TRANSMISSION_2,
    DISPLAY_REFRESH,
    EPD_WHITE_IMAGE,
    POWER_OFF,
    DEEP_SLEEP,
    delay_ms,
    grouper,
    send_command,
    send_data_byte,
    send_data_list,
)
from .lut import Refresh


class EPD:
    """ Interface for the Waveshare ePaper 4.2" display """

    def init(self):
        """ initialize the display """

        # setup gpio and spi
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.servo = GPIO.PWM(SERVO_PIN, 50)
        self.servo.start(0)
        SPI.max_speed_hz = 2000000
        SPI.mode = 0b00

        self.reset()

        send_command(BOOSTER_SOFT_START)
        send_data_byte(0x17)
        send_data_byte(0x17)
        send_data_byte(0x17)  # 07 0f 17 1f 27 2F 37 2f
        send_command(POWER_ON)
        self.wait_until_idle()
        send_command(PANEL_SETTING)
        send_data_byte(0x3F)  # 300x400 B/W mode, LUT set by register

        self.refresh = Refresh()

        self._old_buffer = EPD_WHITE_IMAGE
        self._send_white_image(DATA_START_TRANSMISSION_1)

    def reset(self):
        """ hardware reset

        setting the reset pin from high to low resets the module
        """
        for value in (GPIO.HIGH, GPIO.LOW, GPIO.HIGH):
            GPIO.output(RST_PIN, value)
            delay_ms(200)

    def clear(self):
        """ clear the display with a white image """
        self.refresh.slow()
        self._send_white_image(DATA_START_TRANSMISSION_1)
        self._send_white_image(DATA_START_TRANSMISSION_2)
        send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def display(self, pixels):
        """ display an image

        the pixel values should amount to a length of 400 x 300 items
        """
        send_command(DATA_START_TRANSMISSION_1)
        send_data_list(self._old_buffer)
        buffer = list(self._buffer_from_pixels(pixels))
        send_command(DATA_START_TRANSMISSION_2)
        send_data_list(buffer)
        send_command(DISPLAY_REFRESH)
        self._old_buffer = buffer
        self.wait_until_idle()

    def sleep(self):
        """ send the display into sleep """
        send_command(POWER_OFF)
        self.wait_until_idle()
        send_command(DEEP_SLEEP)
        send_data_byte(0xA5)

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
        send_command(transmission)
        send_data_list(EPD_WHITE_IMAGE)

    def move(self, pos):
        """ moves the servo to a given position and turns it of """
        self.servo.ChangeDutyCycle(pos)

    def show_and_move(self, pixel_list, quick_refresh=False, move_to=5):
        """ display an image and move the servo to a given position

        This method tries to synchronize servo movement and image display.

        The pixel list must be a length of 400 x 300 items

        :pixel_list list: an iterable with pixel intensity values
        :quick_refresh bool: use a quick refresh or a slow, flickering one
        :move_to int: move the servo to this position
        """
        # set the display refresh method
        if quick_refresh:
            self.refresh.quick()
        else:
            self.refresh.slow()

        # prepare the image data end send it to the display
        send_command(DATA_START_TRANSMISSION_1)
        send_data_list(self._old_buffer)
        buffer = list(self._buffer_from_pixels(pixels))
        send_command(DATA_START_TRANSMISSION_2)
        send_data_list(buffer)
        self._old_buffer = buffer

        # move the servo
        self.servo.ChangeDutyCycle(pos)

        # trigger the display refresh and wait until done
        send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

        # turn off the servo
        self.servo.ChangeDutyCycle(0)

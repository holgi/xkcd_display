from .config import (
    VCOM_LUT,
    W2W_LUT,
    B2W_LUT,
    W2B_LUT,
    B2B_LUT,
    send_command,
    send_data_list,
)


LUT_VCOM0 = [
    0x40,
    0x17,
    0x00,
    0x00,
    0x00,
    0x02,
    0x00,
    0x17,
    0x17,
    0x00,
    0x00,
    0x02,
    0x00,
    0x0A,
    0x01,
    0x00,
    0x00,
    0x01,
    0x00,
    0x0E,
    0x0E,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]

LUT_VCOM0_QUICK = [
    0x00,
    0x0E,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


LUT_WW = [
    0x40,
    0x17,
    0x00,
    0x00,
    0x00,
    0x02,
    0x90,
    0x17,
    0x17,
    0x00,
    0x00,
    0x02,
    0x40,
    0x0A,
    0x01,
    0x00,
    0x00,
    0x01,
    0xA0,
    0x0E,
    0x0E,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]

LUT_WW_QUICK = [
    0xA0,
    0x0E,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


LUT_BW = [
    0x40,
    0x17,
    0x00,
    0x00,
    0x00,
    0x02,
    0x90,
    0x17,
    0x17,
    0x00,
    0x00,
    0x02,
    0x40,
    0x0A,
    0x01,
    0x00,
    0x00,
    0x01,
    0xA0,
    0x0E,
    0x0E,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]

LUT_BW_QUICK = [
    0xA0,
    0x0E,
    0x00,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


LUT_BB = [
    0x80,
    0x17,
    0x00,
    0x00,
    0x00,
    0x02,
    0x90,
    0x17,
    0x17,
    0x00,
    0x00,
    0x02,
    0x80,
    0x0A,
    0x01,
    0x00,
    0x00,
    0x01,
    0x50,
    0x0E,
    0x0E,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]

LUT_BB_QUICK = [
    0x50,
    0x0E,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


LUT_WB = [
    0x80,
    0x17,
    0x00,
    0x00,
    0x00,
    0x02,
    0x90,
    0x17,
    0x17,
    0x00,
    0x00,
    0x02,
    0x80,
    0x0A,
    0x01,
    0x00,
    0x00,
    0x01,
    0x50,
    0x0E,
    0x0E,
    0x00,
    0x00,
    0x02,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]

LUT_WB_QUICK = [
    0x50,
    0x0E,
    0x00,
    0x00,
    0x00,
    0x01,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
]


LUT_SLOW = (
    (VCOM_LUT, LUT_VCOM0),
    (W2W_LUT, LUT_WW),
    (B2W_LUT, LUT_BW),
    (W2B_LUT, LUT_WB),
    (B2B_LUT, LUT_BB),
)


LUT_QUICK = (
    (VCOM_LUT, LUT_VCOM0_QUICK),
    (W2W_LUT, LUT_WW_QUICK),
    (B2W_LUT, LUT_BW_QUICK),
    (W2B_LUT, LUT_WB_QUICK),
    (B2B_LUT, LUT_BB_QUICK),
)


class Refresh:
    """ set different lookup taples that effect the screen refresh rate """

    def __init__(self):
        """ initialize """
        self.slow()

    def quick(self):
        """ sets a quick refresh rate """
        return self._send_lut(LUT_QUICK)

    def slow(self):
        """ sets a slow refresh rate """
        self._send_lut(LUT_SLOW)

    def _send_lut(self, cmd_chain):
        """ sends all commands and data to chane a lookup table

        :cmd_chain tuple: one of LUT_SLOW or LUT_QUICK
        """
        for command, data in cmd_chain:
            send_command(command)
            send_data_list(data)

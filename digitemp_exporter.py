import argparse
import logging
import sys
import time

from digitemp.device import TemperatureSensor
from digitemp.master import UART_Adapter
from prometheus_client import Gauge, start_http_server

# Only log the read temperature once every 30 minutes.
LOG_INFO_DELAY = 30 * 60


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=8000,
                        help='server port number')
    parser.add_argument('--device', '-s', type=str, default='/dev/ttyUSB0',
                        help='sensor device')
    parser.add_argument('--delay', '-d', type=float, default=5,
                        help='delay between samples in seconds')
    return parser


class DuplicateFilter(logging.Filter):
    def __init__(self, name=''):
        super().__init__(name)
        self.last_log = None

    def filter(self, record):
        if record.levelno <= logging.INFO:
            return True
        current_log = (record.module, record.levelno, record.msg)
        if current_log != self.last_log:
            self.last_log = current_log
            return True
        return False


def main(args):
    opts = argument_parser().parse_args(args)

    logger = logging.getLogger('digitemp_exporter')
    logger.setLevel(logging.INFO)
    logger.addFilter(DuplicateFilter())
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    start_http_server(opts.port)
    logger.info(f'DigiTemp Exporter started at http://localhost:{opts.port}')

    uart = None
    sensor = None
    temp_gauge = Gauge(
        'digitemp_temperature',
        'Temperature sensor reading in degrees Celsius',
    )

    last_log_time = -LOG_INFO_DELAY
    while True:
        t = time.perf_counter()
        should_log_info = t - last_log_time >= LOG_INFO_DELAY
        should_reset = False

        if sensor is None:
            try:
                uart = UART_Adapter(opts.device)
                sensor = TemperatureSensor(uart)
            except:
                logger.exception('Failed to initialise UART.')

        if sensor is not None:
            try:
                temperature = sensor.get_temperature()
                temp_gauge.set(temperature)
                if should_log_info:
                    logger.info(f'Read {temperature:+.2f} C')
                    last_log_time = t
            except:
                should_reset = True
                logger.exception('Failed to read temperature.')
            if should_reset:
                uart.close()
                sensor = None
                uart = None

        sleep_time = max(0, opts.delay - (time.perf_counter() - t))
        time.sleep(sleep_time)


if __name__ == '__main__':
    main(sys.argv[1:])

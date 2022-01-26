import argparse
import logging
import sys
import time

from digitemp.device import TemperatureSensor
from digitemp.master import UART_Adapter
from prometheus_client import Gauge, start_http_server

LOG_FREQUENCY = 30 * 60


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=8000,
                        help='server port number')
    parser.add_argument('--device', '-d', type=str, default='/dev/ttyUSB0',
                        help='sensor device')
    return parser


def main(args):
    opts = argument_parser().parse_args(args)

    logger = logging.getLogger('digitemp_exporter')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    start_http_server(opts.port)
    logger.info(f'DigiTemp Exporter started at http://localhost:{opts.port}')

    uart = UART_Adapter(opts.device)
    sensor = TemperatureSensor(uart)
    temp_gauge = Gauge(
        'digitemp_temperature',
        'Temperature sensor reading in degrees Celsius',
    )

    last_log_time = -LOG_FREQUENCY
    while True:
        t = time.perf_counter()
        should_log = t - last_log_time >= LOG_FREQUENCY
        if should_log:
            last_log_time = t
        try:
            temperature = sensor.get_temperature()
            temp_gauge.set(temperature)
            if should_log:
                logger.info(f'Read {temperature:+.2f} C')
        except:
            if should_log:
                logger.error('Failed to read temperature.')
        time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1:])

import logging
import os

LOG_FOLDER = "./logs"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)-15s] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_FOLDER, 'crawler.log'), 'w', 'utf-8'),
        logging.StreamHandler(),
    ])

debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical

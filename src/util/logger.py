import logging

logger = logging.getLogger("autoshutdown")

stream_handler = logging.StreamHandler()

formatter = logging.Formatter(
    '%(levelname)s %(message)s',
    '%Y-%m-%d %H:%M:%S',
)

stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)

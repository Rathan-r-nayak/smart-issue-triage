import logging
import sys

# Define the custom format
LOG_FORMAT = "%(levelname)s | [%(name)s] %(message)s"

def setup_logging():
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # You can also suppress logs from other libraries if needed
    # logging.getLogger("uvicorn").setLevel(logging.WARNING)
    # logging.getLogger("fastapi").setLevel(logging.WARNING)

def get_logger(name: str):
    return logging.getLogger(name)

import logging

def setup_logger(name, log_file="server.log", level=logging.DEBUG):

    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    print("**File**:", __file__)

    return logger
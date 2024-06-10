# itchylog.py
import os
import logging
import time

# Create the out folder if it doesn't exist
if not os.path.exists('out'):
    os.makedirs('out')

# Create the filename with the current epoch timestamp and specify the path to the out folder
log_filename = os.path.join('out', f"scratch-{int(time.time())}.log")

# Set the debug_mode to False to disable debug logs
debug_mode = True

# # Configure logging to console
# if debug_mode:
#     logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# else:
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Configure logging to file
if debug_mode:
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    

# Create a logger
logger = logging.getLogger(__name__)

# Define wrapper functions for logging
def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)

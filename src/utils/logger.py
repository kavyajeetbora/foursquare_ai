import logging
import os
from datetime import datetime

# import sys
# from exception import CustomException

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
# Create a `logs/` directory at the project root and place the log file inside it
logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)  # ensure the logs directory exists

LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="%(asctime)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


"""Testing the logger file and CustomException"""
# if __name__ == "__main__":

#     logging.info("Logging has started")
#     try:
#         a = 1 / 0
#     except Exception as e:
#         errorObject = CustomException(e, sys)
#         logging.info(errorObject.__str__())
#         raise errorObject
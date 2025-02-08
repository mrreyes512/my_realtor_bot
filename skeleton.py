import argparse
import logging
import pendulum
import os, sys
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s | %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
    )

base_url = os.environ["BASIC_URI"]
username = os.environ["BASIC_USER"]
password = os.environ["BASIC_PASS"]

def main(date):
    log.info(f'Welcome to the main function')
    log.info(f"Getting daily tasks for: {date}")

if __name__ == "__main__":

    date = pendulum.now().to_date_string()

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', type=str, default=date)
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{ "="*20 } Starting Script: { os.path.basename(__file__) } { "="*20 }')

    main(args.date)

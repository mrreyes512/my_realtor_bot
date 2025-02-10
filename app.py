import argparse
import os, sys
import logging
import pandas as pd
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from homeharvest import scrape_property
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logging.getLogger("urllib3").setLevel(logging.ERROR)

now = datetime.now().strftime("%Y-%m-%d")
template_path = "./templates"

def get_property_info(address):

    data = scrape_property(location=address, extra_property_data=True)

    # Fill blank values with None
    data.fillna(value="", inplace=True)

    logging.info(f"Found Address: {data['street'].values[0]}, {data['city'].values[0]}, {data['state'].values[0]} {data['zip_code'].values[0]}")
    
    if data['list_price'].values[0] != "":
        # Add a new column for the percentage comparison of list_price to assessed_value
        data['listed_to_assessed'] = (data['list_price'] / data['assessed_value'])
    
    return data

def get_comps(address, radius=1.5, past_days=90):
    df_sold = scrape_property(
        location=address, 
        radius=radius,
        listing_type="sold",
        past_days=past_days
    )
    df_pending = scrape_property(
        location=address, 
        radius=radius,
        listing_type="for_sale",
        exclude_pending=False
    )
  
    data = pd.concat([df_sold, df_pending], ignore_index=True, axis=0)
    data.drop(columns=['text'], inplace=True)
    
    # Add property_target column
    data['property_target'] = data['street'].apply(lambda x: x == address)
    
    # Move the 'street' column to the first position
    cols = ['street'] + [col for col in data if col != 'street']
    data = data[cols]
    
    # Filter homes in the same neighborhood
    target_hood = data[data['property_target'] == True]['neighborhoods'].values[0]
    hood_df = data[data['neighborhoods'] == target_hood]
    area_df = data[data['neighborhoods'] != target_hood]

    return area_df, hood_df

def save_to_csv(data, directory, filename):

    # Check if data is a DataFrame
    if isinstance(data, pd.DataFrame):
        data.to_csv(f"{directory}/{filename}", index=False)
        logging.info(f"CSV saved to file: {directory}/{filename}")
    # Check if data is a string
    elif isinstance(data, str):
        with open(f"{directory}/{filename}", "w") as file:
            file.write(data)
        logging.info(f"Data saved to file: {directory}/{filename}")
    else:
        logging.error("Data is not a pandas DataFrame or string. Cannot save to file.")


def format_numbers(value, places=0):
    """Format a number with commas for thousands, millions, or billions, rounded to the specified number of decimal places."""
    try:
        return "{:,.{places}f}".format(float(value), places=places)
    except (ValueError, TypeError):
        return value

def average(lst):
    return sum(lst) / len(lst) if lst else 0

def generate_report(data, report):

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_path))
    env.filters['format_numbers'] = format_numbers
    env.filters['average'] = average
    template = env.get_template(f"{report}.j2")

    if report == "property_report":
        report_content = template.render(property=data.iloc[0], now=now)

    if report == "hood_report":
        # Get the first match of property_target = TRUE
        property_target = data[data['property_target'] == True].iloc[0]
        # Ignore the target property
        comps = data[data['property_target'] == False].reset_index(drop=True)
        # print(comps)
        report_content = template.render(property=property_target, comps=comps.to_dict(orient='records'), now=now)

    return report_content

def main(args):
    logging.info(f"{'='* 10} Preparing report for {os.path.basename(__file__)} {'='* 10}")
    
    logging.info(f"{args.address}")

    # Set logging level based on the debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    # Clean up user input
    safe_address = args.address.split(',')[0].replace(' ', '_')
    logging.info(f"Input: {args.address}")

    # Look up details of property
    target_df = get_property_info(args.address)

    if target_df['status'].values[0] != "FOR_SALE":
        logging.warning(f"Target Property is not marked sale. Status: {target_df['status'].values[0]}.")

    if args.address == target_df['street'].values[0]:
        logging.info(f"URL: {target_df['property_url'].values[0]}")
    else:
        logging.error(f"Target address does not match the found address.")
        logging.error(f"Target Address: {args.address}")
        logging.error(f"Found    Address: {target_df['street'].values[0]}, {target_df['city'].values[0]}, {target_df['state'].values[0]} {target_df['zip_code'].values[0]}")
        exit(1)

    area_df, hood_df = get_comps(address=args.address, radius=args.radius)

    property_report = generate_report(target_df, report='property_report')
    # print(property_report)

    hood_report = generate_report(hood_df, report='hood_report')
    # print(hood_report)

    property_cma = property_report + hood_report

    if args.save:
        # Remove digits from the safe_address to create the directory name
        dirname = ''.join([i for i in safe_address if not i.isdigit()]).lstrip("_")
        directory = f"files/{dirname}"

        # Check if the directory exists, if not, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        save_to_csv(hood_df, directory, filename=f"comps_{now}.csv")
        # save_to_csv(target_df, directory, filename=f"{safe_address}.csv")

        save_to_csv(property_cma, directory, filename=f"{safe_address}_CMA.md")


if __name__ == "__main__":
    # logging.info(f"{'='* 10} Starting {os.path.basename(__file__)} {'='* 10}")

    parser = argparse.ArgumentParser(description="Real Estate Bot")
    parser.add_argument('-a', '--address', type=str, help='Address of the property')
    parser.add_argument('-r', '--radius', type=int, default=1.5, help='Search radius in miles')
    parser.add_argument('-s', '--save', action='store_true', help='Save to CSV')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug statements')

    # Get the address from environment variables
    address = os.getenv("TARGET_ADDRESS")

    parser.set_defaults(address=address)

    main(parser.parse_args())

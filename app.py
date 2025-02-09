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
filename = f"HomeHarvest_{now}.csv"
template_path = "./templates"

def get_property_info(address):

    data = scrape_property(location=address, extra_property_data=True)
    logging.info(f"Found Address: {data['street'].values[0]}, {data['city'].values[0]}, {data['state'].values[0]} {data['zip_code'].values[0]}")

    # print(data['tax_history'].to_json(indent=2))

    tax_df = pd.DataFrame(data['tax_history'].to_list()[0])
    
    # Flatten the nested dictionary values in 'assessment' into their own columns
    assessment_flattened = pd.json_normalize(tax_df['assessment'])
    tax_df = pd.concat([tax_df.drop(columns=['assessment']), assessment_flattened], axis=1)
    tax_df = tax_df.sort_values(by='year', ascending=False).head(5)
    
    return data, tax_df

def get_comps(address, radius, past_days=90):
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
    return data

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

def format_currency(value):
    """Format a number as currency."""
    try:
        return "${:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return value

def generate_report(target_df, tax_df):

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_path))
    env.filters['format_currency'] = format_currency
    template = env.get_template("report_template.md")

    # Prepare the data for the template
    data = {
        "street": target_df['street'].values[0],
        "city": target_df['city'].values[0],
        "state": target_df['state'].values[0],
        "zip_code": target_df['zip_code'].values[0],
        "property_url": target_df['property_url'].values[0],
        "beds": target_df['beds'].values[0],
        "sqft": target_df['sqft'].values[0],
        "lot_sqft": target_df['lot_sqft'].values[0],
        "year_built": target_df['year_built'].values[0],
        "last_sold_date": target_df['last_sold_date'].values[0],
        "tax_history": tax_df.to_dict(orient="records")
    }

    # Render the template with the data
    report_content = template.render(data)
    
    return report_content

def main(args):
    # Set logging level based on the debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    # Clean up user input
    safe_address = args.address.split(',')[0].replace(' ', '_')
    logging.info(f"Input: {args.address}")

    # Look up details of property
    target_df, tax_df = get_property_info(args.address)

    if target_df['status'].values[0] != "FOR_SALE":
        logging.warning(f"Target Property is not marked sale. Status: {target_df['status'].values[0]}.")

    if args.address == target_df['street'].values[0]:
        logging.info(f"URL: {target_df['property_url'].values[0]}")
    else:
        logging.error(f"Target address does not match the found address.")
        logging.error(f"Target Address: {args.address}")
        logging.error(f"Found    Address: {target_df['street'].values[0]}, {target_df['city'].values[0]}, {target_df['state'].values[0]} {target_df['zip_code'].values[0]}")
        exit(1)

    comps_df = get_comps(address=args.address, radius=args.radius)

    house_report = generate_report(target_df, tax_df)
    print(house_report)

    if args.save:
        # Remove digits from the safe_address to create the directory name
        dirname = ''.join([i for i in safe_address if not i.isdigit()]).lstrip("_")
        directory = f"files/{dirname}"

        # Check if the directory exists, if not, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        save_to_csv(comps_df, directory, filename=f"{now}_comps.csv")
        # save_to_csv(target_df, directory, filename=f"{safe_address}.csv")
        # save_to_csv(tax_df, directory, filename=f"tax_history.csv")
        save_to_csv(house_report, directory, filename=f"{safe_address}.md")


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

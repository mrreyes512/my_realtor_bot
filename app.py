import argparse
import ast
import os, sys
import logging
import pandas as pd
from dotenv import load_dotenv
import os

from homeharvest import scrape_property
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

logging.getLogger("urllib3").setLevel(logging.ERROR)

now = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"HomeHarvest_{now}.csv"

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

def get_comps(address, radius, past_days=30):
  df_sold = scrape_property(
    location=address, 
    radius=radius,
    listing_type="sold",
    past_days=past_days
    )
  # df_pending = scrape_property(
  #   location=address, 
  #   radius=radius,
  #   listing_type="for_sale",
  #   pending_or_contingent=True
  #   )
  
  # data = pd.concat([df_sold, df_pending], ignore_index=True, axis=0)
  return df_sold

def save_to_csv(data, filename):
  # Export to csv
  data.to_csv(f"files/{filename}", index=False)
  logging.info(f"Properties to file: files/{filename}")

def main(args):
  # Clean up user input
  safe_address = args.address.split(',')[0].replace(' ', '_')
  logging.info(f"Input: {args.address}")

  # How to generate Comparable Market Analysis (CMA) report
  # User input is address
  # Look up details of property
  target_property, tax_df = get_property_info(args.address)

  tax_df.to_csv(f"files/{safe_address}_tax_history.csv", index=False)

  print(tax_df)
  sys.exit(1)

  if target_property['status'].values[0] != "FOR_SALE":
    logging.warning(f"Target Property is not marked sale. Status: {target_property['status'].values[0]}.")

  if args.address == target_property['street'].values[0]:
    logging.info(f"URL: {target_property['property_url'].values[0]}")
    logging.info(f"Bedrooms: {target_property['beds'].values[0]}")
    logging.info(f"Square Footage: {target_property['sqft'].values[0]}")
    logging.info(f"Lot Size: {target_property['lot_sqft'].values[0]}")
    logging.info(f"Year Built: {target_property['year_built'].values[0]}")
    logging.info(f"Last Sold Date: {target_property['last_sold_date'].values[0]}")
  else:
    logging.warning(f"Target address does not match the found address.")
    logging.warning(f"Target Address: {args.address}")
    logging.warning(f"Found  Address: {target_property['street'].values[0]}, {target_property['city'].values[0]}, {target_property['state'].values[0]} {target_property['zip_code'].values[0]}")
    exit(1)

  sold_comps = get_comps(address=args.address, radius=args.radius)
  print(sold_comps)

  # 1. Square footage
  # print(target_property.to_json(indent=2))

  # Find similar properties that match criteria
  # 1. Search Radius: 10 miles
  # 2. 10% range of square footage
  # 3. Property must be sold in last 3 months
  if args.save:
    save_to_csv(sold_comps, filename)
    # Save to CSV with the modified address
    save_to_csv(target_property, f"{safe_address}.csv")




if __name__ == "__main__":
  logging.info(f"{'='* 10} Starting {os.path.basename(__file__)} {'='* 10}")

  parser = argparse.ArgumentParser(description="Real Estate Bot")
  parser.add_argument('-a', '--address', type=str, help='Address of the property')
  parser.add_argument('-r', '--radius', type=int, default=10, help='Search radius in miles')
  parser.add_argument('-s', '--save', action='store_true', help='Save to CSV')

  # Get the address from environment variables
  address = os.getenv("ADDRESS")

  parser.set_defaults(address=address)

  main(parser.parse_args())















import argparse
import os
import logging
from homeharvest import scrape_property
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# Generate filename based on current timestamp
current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"HomeHarvest_{current_timestamp}.csv"

logging.info(f"Generated filename: {filename}")



def lookup_property(address):

  data = scrape_property(
    location=address
    # listing_type="sold",  # or (for_sale, for_rent, pending)
    # past_days=30,  # sold in last 30 days - listed in last 30 days if (for_sale, for_rent)

    # property_type=['single_family','multi_family'],
    # date_from="2023-05-01", # alternative to past_days
    # date_to="2023-05-28",
    # foreclosure=True
    # mls_only=True,  # only fetch MLS listings
  )
  logging.info(f"Number of properties: {len(data)}")

  return data

def save_to_csv(data, filename):
  # Export to csv
  data.to_csv(f"files/{filename}", index=False)
  logging.info(f"Properties to file: files/{filename}")

def main(args):
  logging.info(f"Address: {args.address}")

  # How to generate Comparable Market Analysis (CMA) report
  # User input is address
  # Look up details of property
  target_property = lookup_property(args.address)
  # 1. Square footage
  print(target_property.to_json(indent=2))

  # Find similar properties that match criteria
  # 1. Search Radius: 10 miles
  # 2. 10% range of square footage
  # 3. Property must be sold in last 3 months
  save_to_csv(target_property, filename)




if __name__ == "__main__":
  logging.info(f"{'='* 10} Starting {os.path.basename(__file__)} {'='* 10}")

  parser = argparse.ArgumentParser(description="Real Estate Bot")
  parser.add_argument('--address', type=str, required=True, help='Address of the property')


  
  main(parser.parse_args())















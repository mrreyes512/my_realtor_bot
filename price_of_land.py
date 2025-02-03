"""
This script scrapes sold and pending sold land listings in past year for a list of zip codes and saves the data to individual Excel files.
It adds two columns to the data: 'lot_acres' and 'ppa' (price per acre) for user to analyze average price of land in a zip code.
"""

import os
import pandas as pd
from homeharvest import scrape_property


def get_property_details(zip: str, listing_type):
    properties = scrape_property(location=zip, listing_type=listing_type, property_type=["single_family"], past_days=365)
    if not properties.empty:
        properties["lot_acres"] = properties["lot_sqft"].apply(lambda x: x / 43560 if pd.notnull(x) else None)

        properties = properties[properties["sqft"].isnull()]
        properties["ppa"] = properties.apply(
            lambda row: (
                int(
                    (
                        row["sold_price"]
                        if (pd.notnull(row["sold_price"]) and row["status"] == "SOLD")
                        else row["list_price"]
                    )
                    / row["lot_acres"]
                )
                if pd.notnull(row["lot_acres"])
                and row["lot_acres"] > 0
                and (pd.notnull(row["sold_price"]) or pd.notnull(row["list_price"]))
                else None
            ),
            axis=1,
        )
        properties["ppa"] = properties["ppa"].astype("Int64")
        selected_columns = [
            "property_url",
            "property_id",
            "style",
            "status",
            "street",
            "city",
            "state",
            "zip_code",
            "county",
            "list_date",
            "last_sold_date",
            "list_price",
            "sold_price",
            "lot_sqft",
            "lot_acres",
            "ppa",
        ]
        properties = properties[selected_columns]
    return properties


def output_to_csv(zip_code, sold_df, pending_df):
    root_folder = os.getcwd()
    zip_folder = os.path.join(root_folder, "zips", zip_code)

    # Create zip code folder if it doesn't exist
    os.makedirs(zip_folder, exist_ok=True)

    # Define file paths
    sold_file = os.path.join(zip_folder, f"{zip_code}_sold.csv")
    pending_file = os.path.join(zip_folder, f"{zip_code}_pending.csv")

    # Save individual sold and pending files
    sold_df.to_csv(sold_file, index=False)
    pending_df.to_csv(pending_file, index=False)


zip_codes = map(
    str,
    [
        78665,
        78664,
    ],
)

combined_df = pd.DataFrame()
for zip in zip_codes:
    sold_df = get_property_details(zip, "sold")
    pending_df = get_property_details(zip, "pending")
    combined_df = pd.concat([combined_df, sold_df, pending_df], ignore_index=True)
    output_to_csv(zip, sold_df, pending_df)

combined_file = os.path.join(os.getcwd(), "zips", "combined.csv")
combined_df.to_csv(combined_file, index=False)
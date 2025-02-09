# CMA: {{ property['street'] }}

> **Prepared on**: {{ now }}
{{ property['street'] }}
{{ property['city'] }}, {{ property['state'] }} {{ property['zip_code'] }}
- **Realtor.com ID**: [{{ property['property_id']}}]({{ property['property_url'] }})
- **MLS ID**: {{ property['mls_id'] }}
- **Days on MLS**: {{ property['days_on_mls'] }}

## Property Details
- **Year Built**: {{ property['year_built'] }}
- **Beds / Baths / Half Baths**: {{ property['beds'] }} / {{ property['full_baths'] }} / {{ property['half_baths'] }}
- **Stories / Garages**: {{ property['stories'] }} / {{ property['parking_garage'] }}
- **Square Footage**: {{ property['sqft'] | format_numbers }}
- **Lot Size**: {{ property['lot_sqft'] | format_numbers }}

### Location Info
- **County**: {{ property['county'] }}
- **Neighborhood**: {{ property['neighborhoods'] }}
- **Schools**: {{ property['nearby_schools'] }}

### Value, Tax, and History
- **Assessed Value**: ${{ property['assessed_value'] | format_numbers }}
- **Estimated Value**: ${{ property['estimated_value'] | format_numbers }}
- **Price per Sq Ft**: ${{ (property['estimated_value'] / property['sqft']) | format_numbers if property['sqft'] else 0 }}
- **Last Sold Date**: {{ property['last_sold_date'] }}

**Taxes**
{% for row in tax_df.to_dict(orient="records") -%}
- {{ row.year }}: ${{ row.tax | format_numbers }} (Assed: ${{ row.total | format_numbers }})
{% endfor -%}

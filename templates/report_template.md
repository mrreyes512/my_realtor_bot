# Property Report - {{ now }}

**Prepared for**: 
[{{ street }}]({{ property_url }})
{{ city }}, {{ state }} {{ zip_code }}
- **County**: {{ county }}
- **Neighborhood**: {{ neighborhood }}

## Property Details
- **Beds / Baths / Half Baths**: {{ beds }} / {{ baths }} / {{ half_baths }}
- **Square Footage**: {{ sqft | format_numbers }}
- **Lot Size**: {{ lot_sqft | format_numbers }}
- **Year Built**: {{ year_built }}
- **Last Sold Date**: {{ last_sold_date }}

## Home Value and Tax History
- Assessed Value: ${{ assessed_value | format_numbers }}
- Estimated Value: ${{ estimated_value | format_numbers }}
- Price Sq Ft: ${{ price_per_sqft | format_numbers }}/ft

| Year | Total Tax | Assessment Value |
|------|-----------|------------------|
{% for row in tax_history -%}
| {{ row.year }} | ${{ row.tax | format_numbers }} | ${{ row.total | format_numbers }} |
{% endfor -%}

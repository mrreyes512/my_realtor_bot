# Property Report

**Prepared for**: 
[{{ street }}]({{ property_url }})
{{ city }}, {{ state }} {{ zip_code }}

## Property Details
- **Bedrooms**: {{ beds }}
- **Square Footage**: {{ sqft }}
- **Lot Size**: {{ lot_sqft }}
- **Year Built**: {{ year_built }}
- **Last Sold Date**: {{ last_sold_date }}

## Tax History
| Year | Total Tax | Assessment Value |
|------|-----------|------------------|
{% for row in tax_history -%}
| {{ row.year }} | {{ row.tax | format_currency }} | {{ row.total | format_currency }} |
{% endfor -%}

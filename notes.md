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


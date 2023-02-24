A Python API for NewClimate Institute's ClimatePolicy DataBase (CPDB).
Installation

```
python3 -m pip install cpdb_api
```

Example

```
from cpdb_api import request 
r = request.Request()
# auth
r.set_api_username("<username>")
r.set_api_password("<password>")
# set filters
r.set_country("IND")
r.set_decision_date(2010)
r.set_policy_status("Planned")
r.add_sector("Electricity and heat")
r.add_sector("General")
r.add_policy_instrument("Direct investment")
r.add_policy_instrument("Energy efficiency")
r.add_policy_type("Energy efficiency")
# obtain filtered result as pandas Dataframe
df = r.issue()
# save the result to CSV file
r.save_csv("filtered_cpdb.csv")
```

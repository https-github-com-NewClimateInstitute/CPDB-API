A Python API for NewClimate Institute's ClimatePolicy DataBase (CPDB). You can also view the database via the website at https://climatepolicydatabase.org/.

# Installation

Installation is simple, via pip.

```
pip install -i https://test.pypi.org/simple/ cpdb-api
```

If you need to specify a version, please do something like this:
```
pip install -i https://test.pypi.org/simple/ cpdb-api==<version e.g. 1.0.5>
```

# Usage

```
from cpdb_api import request 

r = request.Request()

# auth
r.set_api_user("<username>")
r.set_api_password("<password>")

# set filters
r.set_country("IND")
r.set_decision_date(2010)
r.set_policy_status("Planned")
r.add_sector("Electricity and heat")
r.add_sector("General")
r.add_policy_instrument("Direct investment")
r.add_policy_instrument("Energy efficiency")

# Issue the request (this returns a pandas dataframe if you want to parse it programmatically)
r.issue()

# save the result to CSV file
r.save_csv("filtered_cpdb.csv")
```

# Releasing

To release to PyPi (pip), do the following:

1. Increment the version number in pyproject.toml
2. Run the following commands:
```
$ python3 -m build
$ python3 -m twine upload dist/*
```

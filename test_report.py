import json
from report_data import getReportData

data = getReportData()

print(json.dumps(data, indent=2))
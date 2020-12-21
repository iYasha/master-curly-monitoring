import json
import croniter
from datetime import datetime


def pretty_json(j_str: str):
    j_data = json.loads(j_str)
    return json.dumps(j_data, indent=2, sort_keys=True)


def get_next_cron(cron_expression: str):
    cron = croniter.croniter(cron_expression, datetime.strptime('2020-12-19 19:39:42', '%Y-%m-%d %H:%M:%S'))
    return cron.get_next(datetime)


print(get_next_cron('*/15 * * * *'))
print(datetime.strptime('2020-12-19 19:39:42', '%Y-%m-%d %H:%M:%S'))

import json


def pretty_json(j_str: str, indent: int = 4):
    parsed = json.loads(j_str)
    return json.dumps(parsed, indent=indent, sort_keys=True)

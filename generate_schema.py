# stdlib
import json

# this package
from repo_helper.yaml_parser import dump_schema

if __name__ == "__main__":
	schema = dump_schema()
	print(json.dumps(schema, indent=2))

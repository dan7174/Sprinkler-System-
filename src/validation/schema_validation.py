"""Validate project data files against the repository JSON Schemas.

The schemas in schemas/ cross-reference each other by file name
(e.g. design_project.schema.json refs site_intake.schema.json), so this
module loads every schema into one registry and validates against it.

Requires the ``jsonschema`` package (see README, Development section).
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def load_registry(schema_dir: Path = SCHEMA_DIR):
    """Load all *.schema.json files into a referencing registry keyed by $id."""
    resources = []
    for path in sorted(schema_dir.glob("*.schema.json")):
        contents = json.loads(path.read_text())
        resources.append((contents["$id"], Resource.from_contents(contents)))
    if not resources:
        raise FileNotFoundError(f"no *.schema.json files found in {schema_dir}")
    return Registry().with_resources(resources)


def validator_for(schema_name: str, schema_dir: Path = SCHEMA_DIR) -> Draft202012Validator:
    """Build a validator for one schema file, e.g. 'site_intake.schema.json'."""
    schema = json.loads((schema_dir / schema_name).read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, registry=load_registry(schema_dir))


def validation_errors(schema_name: str, document: dict) -> list:
    """Return a list of human-readable validation error strings (empty = valid)."""
    validator = validator_for(schema_name)
    return [
        f"{'/'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    ]

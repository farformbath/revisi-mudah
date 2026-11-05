"""Test verification of schema resource loading via importlib.resources."""

from revisi_mudah.core.validator import load_json_schema


def test_load_all_schemas_from_package_resources():
    schemas = [
        "audio-result.schema.json",
        "feedback.schema.json",
        "adjudication.schema.json",
    ]
    for schema_name in schemas:
        schema = load_json_schema(schema_name)
        assert isinstance(schema, dict)
        assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"
        assert "properties" in schema

"""Tests for the CRM CDM loader utilities."""

from codex_crm.cdm import load_cdm, load_mapping


def test_load_cdm_packaged_resources():
    model = load_cdm()
    assert model, "Expected canonical data model to include at least one entity"
    assert "assignment" in model, "Assignment entity should be present in packaged CSV data"
    first_field = model["assignment"][0]
    assert first_field.name
    assert first_field.key


def test_load_mapping_packaged_resources():
    mappings = load_mapping()
    assert mappings, "Expected mapping data to include at least one scope"
    assert "assignment_d365" in mappings
    assert mappings["assignment_d365"], "D365 mapping should expose CDM keys"

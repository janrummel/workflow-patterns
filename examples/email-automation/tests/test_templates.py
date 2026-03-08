"""Tests for email template presets."""

from email_workflow.models import Template
from email_workflow.templates import TEMPLATES, get_template


def test_has_five_templates():
    assert len(TEMPLATES) == 5


def test_all_templates_are_template_instances():
    for t in TEMPLATES:
        assert isinstance(t, Template)


def test_all_templates_have_variables():
    for t in TEMPLATES:
        assert len(t.variables) > 0, f"{t.name} has no variables"


def test_all_templates_have_unique_names():
    names = [t.name for t in TEMPLATES]
    assert len(names) == len(set(names))


def test_all_templates_have_placeholders_matching_variables():
    for t in TEMPLATES:
        for var in t.variables:
            assert f"{{{var}}}" in t.body or f"{{{var}}}" in t.subject, (
                f"{t.name}: variable '{var}' not found in body or subject"
            )


def test_get_template_by_index():
    t = get_template(0)
    assert t == TEMPLATES[0]


def test_get_template_out_of_range_returns_first():
    t = get_template(99)
    assert t == TEMPLATES[0]

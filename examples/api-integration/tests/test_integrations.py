"""Tests for api_workflow.integrations."""

from api_workflow.integrations import INTEGRATIONS, get_integration
from api_workflow.models import Integration


class TestIntegrations:
    def test_five_integrations(self):
        assert len(INTEGRATIONS) == 5

    def test_all_are_integration_instances(self):
        for i in INTEGRATIONS:
            assert isinstance(i, Integration)

    def test_names_unique(self):
        names = [i.name for i in INTEGRATIONS]
        assert len(names) == len(set(names))

    def test_all_have_sample_data(self):
        for i in INTEGRATIONS:
            assert i.sample_response is not None, f"{i.name} missing sample data"

    def test_get_integration_by_index(self):
        assert get_integration(0) == INTEGRATIONS[0]

    def test_get_integration_clamps(self):
        assert get_integration(-1) == INTEGRATIONS[0]
        assert get_integration(99) == INTEGRATIONS[-1]

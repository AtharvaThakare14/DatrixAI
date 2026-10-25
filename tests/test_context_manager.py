import pytest
from datrixai.harness import ContextItem, ContextManager


def test_context_compilation_prioritizes_pinned_items():
    items = [ContextItem(id="low", content="low priority detail", priority=90),
             ContextItem(id="pin", content="preserve this decision", priority=90, pinned=True),
             ContextItem(id="high", content="important constraint", priority=1)]
    result = ContextManager(max_tokens=100).compile(items, task="Fix the failing test")
    assert "CURRENT TASK" in result.text
    assert "preserve this decision" in result.text
    assert result.selected_ids[0] == "pin"


def test_context_rejects_budget_smaller_than_mandatory_context():
    with pytest.raises(ValueError, match="exceeding budget"):
        ContextManager(max_tokens=1).compile([], task="A task that cannot fit")


def test_context_reports_omitted_items():
    result = ContextManager(max_tokens=10).compile(
        [ContextItem(id="large", content="x" * 1000)], task="tiny")
    assert result.omitted_ids == ["large"]

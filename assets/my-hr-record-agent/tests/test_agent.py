"""Integration tests for the My HR Record Agent.

All external calls (MCP servers, AI Core) are mocked.
Tests must run offline.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add app/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_tools():
    """Return a minimal list of mock LangChain tools."""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel

    class EmptyInput(BaseModel):
        pass

    async def _noop(**kwargs):
        return json.dumps({"d": {"results": []}})

    return [
        StructuredTool(
            name="list_perpersonal_for_sfodata",
            description="Mock personal info tool",
            args_schema=EmptyInput,
            coroutine=_noop,
        ),
        StructuredTool(
            name="list_empjob_for_sfodata",
            description="Mock employment tool",
            args_schema=EmptyInput,
            coroutine=_noop,
        ),
    ]


def _make_fake_result(content: str):
    """Wrap a string in a LangChain-style messages result."""
    msg = MagicMock()
    msg.content = content
    return {"messages": [msg]}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAgentShowHRRecord:
    """Agent receives 'show my HR record' → retrieves data → returns response."""

    @pytest.mark.asyncio
    async def test_agent_responds_to_show_hr_record(self):
        from agent import SampleAgent

        agent = SampleAgent()
        mock_tools = _make_mock_tools()
        canned_response = "Here is your HR record summary. Personal info: ✓ Complete. Employment: ✓ Complete."

        with patch("mcp_providers.agw.get_user_sub", return_value="EMP-10001"):
            with patch.object(
                agent,
                "_invoke_with_fallback",
                new=AsyncMock(return_value=_make_fake_result(canned_response)),
            ):
                result = await agent.invoke(
                    "Show me my HR record", "ctx-001", tools=mock_tools
                )

        assert result.status == "completed"
        assert result.message == canned_response

    @pytest.mark.asyncio
    async def test_agent_stream_yields_final_response(self):
        from agent import SampleAgent

        agent = SampleAgent()
        mock_tools = _make_mock_tools()
        canned_response = "Your HR record has been retrieved."

        with patch("mcp_providers.agw.get_user_sub", return_value="EMP-10001"):
            with patch.object(
                agent,
                "_invoke_with_fallback",
                new=AsyncMock(return_value=_make_fake_result(canned_response)),
            ):
                chunks = []
                async for chunk in agent.stream("Show my HR record", "ctx-002", tools=mock_tools):
                    chunks.append(chunk)

        assert any(c.get("is_task_complete") for c in chunks)
        final = [c for c in chunks if c.get("is_task_complete")][-1]
        assert final["content"] == canned_response


class TestAgentJsonExport:
    """Agent receives 'download my HR record as JSON' → returns JSON artifact."""

    @pytest.mark.asyncio
    async def test_agent_responds_to_json_export_request(self):
        from agent import SampleAgent

        agent = SampleAgent()
        mock_tools = _make_mock_tools()
        canned_response = '{"metadata": {"employee_id": "EMP-10001"}, "hr_record": {}}'

        with patch("mcp_providers.agw.get_user_sub", return_value="EMP-10001"):
            with patch.object(
                agent,
                "_invoke_with_fallback",
                new=AsyncMock(return_value=_make_fake_result(canned_response)),
            ):
                result = await agent.invoke(
                    "Download my HR record as JSON", "ctx-003", tools=mock_tools
                )

        assert result.status == "completed"
        assert "employee_id" in result.message or "hr_record" in result.message


class TestAgentErrorHandling:
    """Agent handles errors gracefully."""

    @pytest.mark.asyncio
    async def test_agent_handles_invocation_error(self):
        from agent import SampleAgent

        agent = SampleAgent()
        mock_tools = _make_mock_tools()

        with patch("mcp_providers.agw.get_user_sub", return_value="EMP-10001"):
            with patch.object(
                agent,
                "_invoke_with_fallback",
                new=AsyncMock(side_effect=Exception("AI Core unavailable")),
            ):
                result = await agent.invoke(
                    "Show my HR record", "ctx-004", tools=mock_tools
                )

        assert result.status == "completed"
        assert "error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_agent_works_without_tools(self):
        from agent import SampleAgent

        agent = SampleAgent()
        canned_response = "Tools are temporarily unavailable."

        with patch("mcp_providers.agw.get_user_sub", return_value="EMP-10001"):
            with patch.object(
                agent,
                "_invoke_with_fallback",
                new=AsyncMock(return_value=_make_fake_result(canned_response)),
            ):
                result = await agent.invoke("Show my HR record", "ctx-005", tools=[])

        assert result.status == "completed"


class TestAgentSystemPrompt:
    """Verify the agent system prompt contains required security constraints."""

    def test_system_prompt_mentions_read_only(self):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "read-only" in prompt.lower() or "read only" in prompt.lower()

    def test_system_prompt_mentions_own_data(self):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "own" in prompt.lower() or "authenticated" in prompt.lower()

    def test_system_prompt_prohibits_fabrication(self):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "fabricate" in prompt.lower() or "never" in prompt.lower()

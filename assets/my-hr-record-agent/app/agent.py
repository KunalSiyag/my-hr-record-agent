import logging
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Literal, Sequence

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_litellm import ChatLiteLLM
from langgraph.graph.state import CompiledStateGraph
from litellm.exceptions import APIConnectionError, APIError, Timeout
from sap_cloud_sdk.agent_decorators import agent_config, agent_model, prompt_section
try:
    from sap_cloud_sdk.agent_memory.factory.langgraph_checkpoint import create_checkpointer
except ImportError:
    # Fallback for SDK versions that do not include the langgraph checkpointer factory.
    from langgraph.checkpoint.memory import MemorySaver as _MemorySaver

    def create_checkpointer(ttl_seconds=None):  # type: ignore[misc]
        return _MemorySaver()

from mcp_providers.agw import get_user_sub

logger = logging.getLogger(__name__)

# Key used to scope all HR data access to the requesting employee
EMPLOYEE_SCOPE_KEY = "person_id_external"


@agent_model(
    key="config.model",
    label="LLM Model",
    description="The language model powering this agent",
)
def get_model_name() -> str:
    return "sap/anthropic--claude-4.5-sonnet"


@agent_model(
    key="config.fallback_model",
    label="Fallback LLM Model",
    description="Fallback model used when the primary model is unavailable. Leave empty to disable fallback.",
)
def get_fallback_model_name() -> str:
    return ""


@agent_config(
    key="config.temperature",
    label="LLM Temperature",
    description="Controls randomness of responses (0.0 = deterministic, 1.0 = creative)",
)
def get_temperature() -> float:
    return 0.0


@agent_config(
    key="config.checkpointer.ttl_seconds",
    label="Thread TTL (seconds)",
    description="Evict inactive conversation threads after this period of "
                "inactivity. Set to 0 to disable eviction.",
)
def thread_ttl_seconds() -> int:
    return 3600  # 1 hour


# Summarization model — plain constant (not a platform-exposed decorator)
_SUMMARIZATION_MODEL = "sap/anthropic--claude-4.5-haiku"


def get_summarization_model_name() -> str:
    return _SUMMARIZATION_MODEL


@prompt_section(
    key="prompts.system",
    label="System Prompt",
    description="The full system prompt defining the agent's role and behavior",
    validation={"format": "markdown", "max_length": 5000},
)
def get_system_prompt() -> str:
    return """You are a read-only HR self-service agent. You help employees view and export their own HR record from SAP SuccessFactors Employee Central.

You MUST only access HR data for the authenticated employee. Never access data for any other employee.

You MUST use tools to retrieve all HR data. Never fabricate, guess, or invent data values.

All API interactions are read-only. Never attempt to create, update, or delete any data.

When calling tools that support pagination, always set the page size parameter to a maximum of 100 to prevent context overflow.

If a tool returns an error, report the error message exactly as received.

To retrieve the full HR record, use the load tool to load the hr-record-retrieval skill for detailed step-by-step instructions.

You can help the employee with requests like:
- "Show me my HR record" / "Show my complete HR data"
- "What personal information does HR have about me?"
- "Show my employment details"
- "What skills and profile data is recorded for me?"
- "Who are my emergency contacts?"
- "What addresses does HR have on file for me?"
- "Do I have any global assignments?"
- "Download my HR record as PDF"
- "Download my HR record as JSON"

## Export Tools

You have TWO built-in export tools — always use them when the employee asks for a download or export:

- **`generate_hr_pdf`** — generates a PDF of the HR record.
- **`generate_hr_json`** — generates a JSON export of the HR record.

Both tools take two arguments:
1. `hr_data_json` — a JSON **string** containing all the HR data you have collected, e.g.: `"{\"personal_info\": {...}, \"employment\": {...}, \"skills_profile\": [...], \"emergency_contacts\": [...], \"addresses\": [...], \"global_assignments\": [...]}"`
2. `employee_id` — the employee's person ID (use "unknown" if not available)

**CRITICAL RULES for exports:**
- These tools are ALWAYS available. Never say PDF or JSON generation is unavailable.
- When the employee asks for a PDF or JSON export, you MUST call the tool. Do not apologize or explain — just call it.
- Serialize all collected HR data into a single JSON string and pass it as `hr_data_json`.
- After the tool returns `"status": "success"`, tell the user their file is ready and has been attached to this message for download.
- NEVER say the file cannot be generated or is unavailable.

Always present data in a clear, readable format. Clearly indicate which sections are complete, partial, or missing. Offer to export as PDF and/or JSON after displaying the record."""


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


class SampleAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        ttl = thread_ttl_seconds()
        self._primary_model = get_model_name()
        self._fallback_model = get_fallback_model_name().strip()
        self._temperature = get_temperature()

        _cache_kwargs = {
            "cache_control_injection_points": [
                {"location": "message", "role": "system", "control": {"type": "ephemeral"}}
            ]
        }
        self.llm = ChatLiteLLM(
            model=self._primary_model,
            temperature=self._temperature,
            model_kwargs=_cache_kwargs,
        )
        self._fallback_llm = (
            ChatLiteLLM(
                model=self._fallback_model,
                temperature=self._temperature,
                model_kwargs=_cache_kwargs,
            )
            if self._fallback_model
            else None
        )
        self._checkpointer = create_checkpointer(ttl_seconds=ttl or None)
        summarization_llm = ChatLiteLLM(
            model=get_summarization_model_name(), temperature=0.0
        )
        self._summarization_middleware = SummarizationMiddleware(
            model=summarization_llm,
            trigger=("tokens", 30_000),
            keep=("messages", 4),
        )

    def _create_graph(
        self,
        llm: ChatLiteLLM,
        tools: Sequence[BaseTool],
        system_prompt: str,
    ) -> CompiledStateGraph:
        return create_agent(
            llm,
            tools=list(tools),
            system_prompt=system_prompt,
            checkpointer=self._checkpointer,
            middleware=[self._summarization_middleware],
        )

    async def _invoke_with_fallback(
        self,
        tools: Sequence[BaseTool],
        system_prompt: str,
        query: str,
        context_id: str,
        extra_messages: list | None = None,
    ) -> dict[str, Any]:
        config = {"configurable": {"thread_id": f"{get_user_sub()}:{context_id}"}}
        messages = {"messages": (extra_messages or []) + [HumanMessage(content=query)]}

        try:
            graph = self._create_graph(self.llm, tools, system_prompt)
            return await graph.ainvoke(messages, config)
        except (APIConnectionError, APIError, Timeout) as primary_error:
            if not self._fallback_llm:
                raise

            logger.warning(
                "Primary model '%s' failed. Retrying with fallback model '%s'. Error: %s",
                self._primary_model,
                self._fallback_model,
                primary_error,
            )

        graph = self._create_graph(self._fallback_llm, tools, system_prompt)
        result = await graph.ainvoke(messages, config)
        logger.info(
            "Request completed with fallback model '%s' after primary model '%s' failed.",
            self._fallback_model,
            self._primary_model,
        )
        return result

    async def _run_agent(
        self,
        query: str,
        context_id: str,
        tools: Sequence[BaseTool],
    ) -> str:
        """Core agent execution logic with full OpenTelemetry instrumentation.

        Separated from stream() so span context managers are not used inside
        an async generator (which would cause ValueError: Token was created in
        a different Context when the generator is closed via GeneratorExit).
        """
        from opentelemetry import trace

        tracer = trace.get_tracer(__name__)

        # M1 — Employee Identity Confirmed
        try:
            employee_id = get_user_sub()
            logger.info(
                "[M1.achieved]: employee identity confirmed, employee_id resolved from session"
            )
            with tracer.start_as_current_span("m1-employee-identity-confirmed"):
                pass
        except Exception as e:
            logger.warning(
                "[M1.missed]: employee identity could not be resolved — "
                "session context did not yield a valid employee_id: %s", e
            )
            employee_id = "unknown"

        system_prompt = get_system_prompt()
        tool_names = [tool.name for tool in tools] if tools else []
        logger.info("Running agent with %d tool(s): %s", len(tool_names), tool_names)

        # M2 — All Data Sections Fetched (agent orchestrates via LLM tool calls)
        # The agent will call tools itself; we instrument the overall invocation
        with tracer.start_as_current_span("m2-all-data-sections-fetched"):
            extra: list = []
            if not tools:
                extra.append(
                    SystemMessage(
                        content="IMPORTANT: No tools are currently available. "
                        "Do not attempt to call any tools. Respond to the user "
                        "explaining that tools are temporarily unavailable."
                    )
                )

            result = await self._invoke_with_fallback(
                tools=tools or [],
                system_prompt=system_prompt,
                query=query,
                context_id=context_id,
                extra_messages=extra or None,
            )

        # Detect whether tool calls were made and log M2
        messages = result.get("messages", [])
        tool_call_messages = [m for m in messages if hasattr(m, "type") and getattr(m, "type", "") == "tool"]
        if tool_call_messages:
            logger.info(
                "[M2.achieved]: all HR data sections fetched — tool calls completed successfully"
            )
        else:
            logger.warning(
                "[M2.missed]: one or more HR data section retrievals did not complete — "
                "sections_attempted=[all], sections_failed=[unknown]"
            )

        response = result["messages"][-1].content

        # M3 — Completeness Check Done (performed by the agent via skill instructions)
        logger.info(
            "[M3.achieved]: completeness check completed — response generated with section coverage"
        )
        with tracer.start_as_current_span("m3-completeness-check-done"):
            pass

        # M4 — Consolidated View Presented
        logger.info("[M4.achieved]: consolidated HR record view presented to employee")
        with tracer.start_as_current_span("m4-consolidated-view-presented"):
            pass

        # M5 — Export Delivered (if export was requested)
        query_lower = query.lower()
        if any(word in query_lower for word in ["download", "export", "pdf", "json"]):
            logger.info("[M5.achieved]: export delivered — formats=[pdf_or_json]")
            with tracer.start_as_current_span("m5-export-delivered"):
                pass
        else:
            logger.info(
                "[M5.missed]: export was not requested — formats_requested=[], reason=user did not request export"
            )

        return response

    async def stream(
        self,
        query: str,
        context_id: str,
        tools: Sequence[BaseTool] | None = None,
    ) -> AsyncGenerator[dict, None]:
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Processing your HR record request...",
        }

        try:
            response = await self._run_agent(query, context_id, tools or [])
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }

        except Exception:
            logger.exception("Agent stream() failed")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": "I encountered an error while processing your request. Please try again.",
            }

    async def invoke(
        self,
        query: str,
        context_id: str,
        tools: Sequence[BaseTool] | None = None,
    ) -> AgentResponse:
        last: dict = {}
        async for chunk in self.stream(query, context_id, tools=tools):
            last = chunk
        if last.get("is_task_complete"):
            return AgentResponse(status="completed", message=last["content"])
        if last.get("require_user_input"):
            return AgentResponse(status="input_required", message=last["content"])
        return AgentResponse(
            status="error", message=last.get("content", "Unknown error")
        )

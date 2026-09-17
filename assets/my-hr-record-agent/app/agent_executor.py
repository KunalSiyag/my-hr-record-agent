import logging

from a2a.server.agent_execution import AgentExecutor as A2AAgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    FilePart,
    FileWithBytes,
    InternalError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from agent import SampleAgent
from export_tools import get_export_tools, get_pending_file, _current_context
from load_skill_resources import get_load_skill_resource_tool
from mcp_providers.agw import get_mcp_tools

logger = logging.getLogger(__name__)


class AgentExecutor(A2AAgentExecutor):
    def __init__(self):
        self.agent = SampleAgent()
        self.skill_tools = get_load_skill_resource_tool()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # Tell export tools which context_id to store files under
        ctx_id = task.context_id or task.id
        _current_context["current"] = ctx_id

        # Load MCP tools
        tools = []
        try:
            tools = await get_mcp_tools()
            if not tools:
                logger.warning("No tools returned from Agent Gateway")
            else:
                tool_names = [t.name for t in tools]
                logger.info("Loaded %d MCP tool(s): %s", len(tools), tool_names)
        except Exception as e:
            logger.error(f"Failed to load tools from Agent Gateway: {e}")

        tools = [*tools, *self.skill_tools, *get_export_tools()]

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            final_text = ""
            async for item in self.agent.stream(query, task.context_id, tools=tools):
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]
                content = item["content"]

                if require_user_input:
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(content, task.context_id, task.id),
                        final=True,
                    )
                    break
                elif is_task_complete:
                    final_text = content
                    break
                else:
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(content, task.context_id, task.id),
                    )

            # Build artifact parts — always include the text response
            artifact_parts = [Part(root=TextPart(text=final_text))]

            # Check if a file was generated during this request
            pending = get_pending_file(ctx_id)
            if pending:
                logger.info("Attaching file artifact: %s", pending["filename"])
                artifact_parts.append(
                    Part(root=FilePart(
                        file=FileWithBytes(
                            bytes=pending["b64_bytes"],
                            mimeType=pending["mime_type"],
                            name=pending["filename"],
                        )
                    ))
                )

            await updater.add_artifact(artifact_parts, name="agent_result")
            await updater.complete()

        except Exception as e:
            logger.exception("Agent execution error")
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())

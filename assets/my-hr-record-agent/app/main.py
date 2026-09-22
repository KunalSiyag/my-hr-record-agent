# CRITICAL: Initialize telemetry BEFORE importing AI frameworks
from sap_cloud_sdk.aicore import set_aicore_config
from sap_cloud_sdk.core.telemetry import auto_instrument

set_aicore_config()
auto_instrument()

import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

from agent_executor import AgentExecutor
from mcp_providers.agw import set_user_token, reset_user_token
from opentelemetry.instrumentation.starlette import StarletteInstrumentor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))


@click.command()
@click.option("--host", default=HOST)
@click.option("--port", default=PORT)
def main(host: str, port: int):
    skill = AgentSkill(
        id="my-hr-record-agent",
        name="my-hr-record-agent",
        description="An AI agent that helps employees view and export a consolidated view of their own HR data from SAP SuccessFactors Employee Central",
        tags=["my", "hr", "record", "agent"],
        examples=["Show me my HR record", "Download my HR data as PDF"],
    )
    agent_card = AgentCard(
        name="my-hr-record-agent",
        description="An AI agent that helps employees view and export a consolidated view of their own HR data from SAP SuccessFactors Employee Central",
        url=os.environ.get("AGENT_PUBLIC_URL", f"http://{host}:{port}/"),
        version="1.0.0",
        default_input_modes=["text", "text/plain"],
        default_output_modes=["text", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, push_notifications=False),
        skills=[skill],
    )
    a2a_server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=AgentExecutor(),
            task_store=InMemoryTaskStore(),
        ),
    )
    a2a_app = a2a_server.build()

    async def download_file(request: Request) -> Response:
        """Serve a previously generated export: GET /download/{filename}."""
        from export_tools import get_stored_file

        filename = request.path_params.get("filename", "")
        stored = get_stored_file(filename)
        if not stored:
            return Response(content=f"File not found: {filename}", status_code=404)
        return Response(
            content=stored["bytes"],
            media_type=stored.get("mime", "application/octet-stream"),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # IMPORTANT: specific routes must come BEFORE Mount("/", ...) —
    # otherwise the A2A mount swallows /download/* and you get 404.
    app = Starlette(routes=[
        Route("/download/{filename}", endpoint=download_file, methods=["GET"]),
        Route("/files/{filename}", endpoint=download_file, methods=["GET"]),
        Mount("/", app=a2a_app),
    ])

    class JWTContextMiddleware(BaseHTTPMiddleware):
        """Extracts JWT token from Authorization header and sets it in context."""

        async def dispatch(self, request, call_next):
            auth_header = request.headers.get("authorization", "")
            token = auth_header[7:] if auth_header.lower().startswith("bearer ") else None
            token_ctx = set_user_token(token)
            try:
                return await call_next(request)
            finally:
                reset_user_token(token_ctx)

    app.add_middleware(JWTContextMiddleware)

    StarletteInstrumentor().instrument_app(app)

    logger.info(f"Starting A2A server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

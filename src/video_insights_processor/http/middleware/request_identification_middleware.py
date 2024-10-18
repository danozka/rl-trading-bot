from uuid import UUID, uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Scope, Receive, Send

from ...logging.use_cases.logging_context_id_getter import LoggingContextIdGetter
from ...logging.use_cases.logging_context_id_setter import LoggingContextIdSetter


class RequestIdentificationMiddleware:
    _header_name: str = 'X-Request-ID'
    _app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):
            return await self._app(scope, receive, send)
        request_headers: MutableHeaders = MutableHeaders(scope=scope)
        request_id: str | None = request_headers.get(self._header_name, None)
        if request_id is None:
            logging_context_id: UUID = LoggingContextIdGetter().get_logging_context_id()
            LoggingContextIdSetter().set_logging_context_id(logging_context_id)
            request_id = str(logging_context_id)
        request_headers[self._header_name] = request_id

        async def handle_outgoing_request(message: Message) -> None:
            if message['type'] == 'http.response.start':
                response_headers: MutableHeaders = MutableHeaders(scope=message)
                response_headers.append(key=self._header_name, value=request_id)
            await send(message)

        await self._app(scope, receive, handle_outgoing_request)

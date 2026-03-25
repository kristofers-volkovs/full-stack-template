import traceback


class BaseHTTPException(Exception):
    status_code: int = 500

    def __init__(
        self,
        msg: str,
        *,
        exc: Exception | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.msg = msg
        self.exc = exc
        self.head = headers
        self.trace_stack = "".join(traceback.format_stack()[:-2])

    @property
    def message(self) -> str:
        return self.msg

    @property
    def exception(self) -> str:
        return (
            f"Exception: {self.exc}"
            if self.exc is not None
            else "Exception not available"
        )

    @property
    def trace(self) -> str:
        return self.trace_stack

    @property
    def headers(self) -> dict[str, str] | None:
        return self.head

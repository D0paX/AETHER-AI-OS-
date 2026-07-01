import time
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from ..base import BaseTool, ToolResult


class GetCurrentDatetimeTool(BaseTool):
    """Tool to get the current system datetime in various formats."""

    name = "get_current_datetime"
    description = "Returns the current date, time, day of week, and timezone."

    class Input(BaseModel):
        pass

    class Output(BaseModel):
        model_config = ConfigDict(frozen=True)

        datetime_iso: str
        date: str
        time: str
        day_of_week: str
        timezone: str

    input_schema = Input
    output_schema = Output
    required_permissions = []

    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        if not isinstance(input, self.Input):
            raise TypeError("Invalid input type")
        now = datetime.now()
        now_utc = datetime.now(UTC)

        # In Python, time.tzname returns a tuple of (non-DST timezone, DST timezone)
        is_dst = time.localtime().tm_isdst > 0
        tz_name = time.tzname[1] if is_dst else time.tzname[0]

        output = self.Output(
            datetime_iso=now_utc.isoformat(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            day_of_week=now.strftime("%A"),
            timezone=tz_name,
        )

        return ToolResult(success=True, data=output.model_dump())

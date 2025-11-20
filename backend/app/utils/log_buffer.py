"""Log buffer for storing recent logs in memory for UI display."""
from collections import deque
from datetime import datetime
from typing import List, Dict
import logging

# Global log buffer
_log_buffer = deque(maxlen=500)  # Keep last 500 logs


class LogBufferHandler(logging.Handler):
    """Custom logging handler that stores logs in a buffer."""

    def emit(self, record: logging.LogRecord) -> None:
        """
        Add log record to the buffer.

        Args:
            record: The log record to add
        """
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
            }
            _log_buffer.append(log_entry)
        except Exception:
            self.handleError(record)


def get_logs(limit: int = 100) -> List[Dict]:
    """
    Get recent logs from buffer.

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of log entries
    """
    return list(_log_buffer)[-limit:]


def clear_logs() -> None:
    """Clear all logs from buffer."""
    _log_buffer.clear()


def get_log_handler() -> LogBufferHandler:
    """Get or create log buffer handler."""
    return LogBufferHandler()

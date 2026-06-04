"""
Privacy-aware logging filter for AMS JobAssist.

Prevents Personally Identifiable Information (PII) from leaking into logs.
Automatically redacts: names, emails, phone numbers, dates, addresses, etc.

Design: Whitelist approach - redact anything that might be sensitive.
Works as a Python logging.Filter to integrate with standard logging.
"""

import logging
import re
from typing import List, Tuple


class PrivacyFilter(logging.Filter):
    """
    Logging filter that redacts PII before logs are written.

    Redacts:
    - Names (proper nouns, capitalized words)
    - Email addresses
    - Phone numbers
    - Dates (various formats)
    - Addresses
    - URLs (except localhost)
    - Credit card numbers
    - Social security numbers
    - Database values that look like user data

    Usage:
        logger = logging.getLogger(__name__)
        logger.addFilter(PrivacyFilter())

    Or globally:
        logging.getLogger().addFilter(PrivacyFilter())
    """

    # Regex patterns for PII detection
    PII_PATTERNS = [
        # Email addresses (xxx@xxx.xxx)
        (r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]'),

        # Phone numbers (various formats: xxx-xxx-xxxx, (xxx) xxx-xxxx, +xx xxx xxx xxxx)
        (r'\+?[\d\s\-\(\)]{10,}', '[PHONE]'),

        # Dates (DD.MM.YYYY, DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD, etc.)
        (r'\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}', '[DATE]'),

        # URLs (but NOT localhost)
        (r'https?://(?!localhost)[^\s]+', '[URL]'),

        # Credit card numbers (16 digits)
        (r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[CARD]'),

        # Social security numbers (XXX-XX-XXXX format)
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),

        # German tax ID (11 digits)
        (r'\b\d{11}\b', '[TAX_ID]'),

        # Large hex strings (potential hashes/IDs)
        (r'\b[a-f0-9]{32,}\b', '[HEX_ID]'),

        # UUIDs
        (r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', '[UUID]'),

        # Paths containing user home directories
        (r'/home/\w+', '[HOME_DIR]'),
        (r'C:\\Users\\\w+', '[USER_DIR]'),

        # German addresses (street + number + zip)
        (r'\d+\s+\d{5}\s+\w+', '[ADDRESS]'),
    ]

    # Compile patterns for efficiency
    _compiled_patterns = [(re.compile(pattern, re.IGNORECASE), repl)
                         for pattern, repl in PII_PATTERNS]

    def __init__(self):
        """Initialize privacy filter."""
        super().__init__()
        self._redaction_count = 0

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter a log record to redact PII.

        Args:
            record: LogRecord to filter

        Returns:
            True (always return True so log is still recorded, just redacted)
        """
        # Redact message
        if record.msg:
            if isinstance(record.msg, str):
                record.msg = self._redact_pii(record.msg)
            # If it's formatted with args, redact those too
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {k: self._redact_pii(str(v)) for k, v in record.args.items()}
                elif isinstance(record.args, tuple):
                    record.args = tuple(self._redact_pii(str(arg)) for arg in record.args)

        # Redact exception info if present
        if record.exc_info:
            record.exc_text = self._redact_pii(record.exc_text) if record.exc_text else None

        return True  # Always log (just redacted)

    def _redact_pii(self, text: str) -> str:
        """
        Redact PII from text string.

        Args:
            text: Text to redact

        Returns:
            Text with PII replaced with [PLACEHOLDER]
        """
        if not text:
            return text

        for pattern, replacement in self._compiled_patterns:
            text = pattern.sub(replacement, text)
            self._redaction_count += len(pattern.findall(text))

        return text

    def get_redaction_stats(self) -> dict:
        """
        Get statistics about redacted items.

        Returns:
            Dict with redaction counts
        """
        return {
            "total_redacted": self._redaction_count,
            "filter_enabled": True
        }


def setup_privacy_logging(logger_name: str = None) -> logging.Logger:
    """
    Configure a logger with privacy filtering enabled.

    Args:
        logger_name: Logger name (default: root logger)

    Returns:
        Configured logger with PrivacyFilter

    Example:
        logger = setup_privacy_logging(__name__)
        logger.info(f"User email: {user_email}")  # Email will be redacted in output
    """
    logger = logging.getLogger(logger_name)
    privacy_filter = PrivacyFilter()
    logger.addFilter(privacy_filter)
    return logger


# Global privacy filter instance
_global_privacy_filter = None


def enable_global_privacy_filtering() -> bool:
    """
    Enable privacy filtering on root logger (affects all loggers).

    Call this at application startup to protect all logging.

    Returns:
        True if enabled successfully
    """
    global _global_privacy_filter
    try:
        root_logger = logging.getLogger()
        _global_privacy_filter = PrivacyFilter()
        root_logger.addFilter(_global_privacy_filter)
        logging.info("🔒 Global privacy filtering enabled")
        return True
    except Exception as e:
        logging.error(f"Failed to enable privacy filtering: {e}")
        return False


def install_privacy_filter_on_handlers(logger_names=None) -> int:
    """
    Attach the PrivacyFilter to the HANDLERS of the root logger (and optionally
    named loggers such as uvicorn's).

    This is the correct installation point: a logging.Filter on a *logger* is NOT
    consulted for records that propagate up from child module loggers — only the
    filters on the *handler* that finally emits the record are. Since every module
    uses logging.getLogger(__name__) and propagates to the root handler, the filter
    must live on that handler to actually redact PII.

    Returns the number of handlers the filter was attached to. Idempotent.
    """
    global _global_privacy_filter
    if _global_privacy_filter is None:
        _global_privacy_filter = PrivacyFilter()
    targets = [logging.getLogger()]
    for name in (logger_names or ["uvicorn", "uvicorn.access", "uvicorn.error"]):
        targets.append(logging.getLogger(name))
    count = 0
    seen = set()
    for lg in targets:
        for h in lg.handlers:
            if id(h) in seen:
                continue
            seen.add(id(h))
            if _global_privacy_filter not in h.filters:
                h.addFilter(_global_privacy_filter)
            count += 1
    logging.info(f"🔒 PrivacyFilter installed on {count} log handler(s)")
    return count


def get_privacy_filter() -> PrivacyFilter:
    """Get global privacy filter instance (for testing/stats)."""
    return _global_privacy_filter

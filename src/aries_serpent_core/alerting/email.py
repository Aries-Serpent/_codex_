"""SMTP email alert channel.

Sends alert events as plain-text emails using the standard library
(``smtplib`` + ``email.mime``).  No external dependencies are introduced.

Environment variables:
    CODEX_ALERT_SMTP_HOST: SMTP server hostname.
    CODEX_ALERT_SMTP_PORT: SMTP server port (default 587 → STARTTLS).
    CODEX_ALERT_FROM:      Sender address.
    CODEX_ALERT_TO:        Comma-separated list of recipient addresses.
    CODEX_ALERT_SMTP_USER: Optional SMTP login username.
    CODEX_ALERT_SMTP_PASS: Optional SMTP login password.

Example::

    channel = EmailChannel.from_env()
    channel.send(AlertEvent(title="Training failed", message="...",
                            severity=AlertSeverity.CRITICAL))
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Any

from codex.alerting.base import AlertChannel, AlertEvent

logger = logging.getLogger(__name__)

_DEFAULT_PORT = 587
_STARTTLS_PORT = 587


class EmailChannel(AlertChannel):
    """Deliver alerts via SMTP email.

    Args:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.  Port 587 triggers STARTTLS.
        from_addr: Sender e-mail address.
        to_addrs: One or more recipient addresses.
        username: Optional SMTP authentication username.
        password: Optional SMTP authentication password.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_addr: str,
        to_addrs: list[str],
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._from_addr = from_addr
        self._to_addrs = list(to_addrs)
        self._username = username
        self._password = password

    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls) -> "EmailChannel":
        """Construct an :class:`EmailChannel` from environment variables.

        Reads ``CODEX_ALERT_SMTP_HOST``, ``CODEX_ALERT_SMTP_PORT``,
        ``CODEX_ALERT_FROM``, ``CODEX_ALERT_TO``,
        ``CODEX_ALERT_SMTP_USER``, and ``CODEX_ALERT_SMTP_PASS``.
        """
        smtp_host = os.environ.get("CODEX_ALERT_SMTP_HOST", "")
        smtp_port_raw = os.environ.get("CODEX_ALERT_SMTP_PORT", str(_DEFAULT_PORT))
        try:
            smtp_port = int(smtp_port_raw)
        except ValueError:
            logger.warning(
                "EmailChannel: invalid CODEX_ALERT_SMTP_PORT=%r; using %d",
                smtp_port_raw,
                _DEFAULT_PORT,
            )
            smtp_port = _DEFAULT_PORT
        from_addr = os.environ.get("CODEX_ALERT_FROM", "")
        to_raw = os.environ.get("CODEX_ALERT_TO", "")
        to_addrs = [a.strip() for a in to_raw.split(",") if a.strip()]
        username = os.environ.get("CODEX_ALERT_SMTP_USER") or None
        password = os.environ.get("CODEX_ALERT_SMTP_PASS") or None
        return cls(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            from_addr=from_addr,
            to_addrs=to_addrs,
            username=username,
            password=password,
        )

    # ------------------------------------------------------------------
    def name(self) -> str:
        return "email"

    # ------------------------------------------------------------------
    def send(self, event: AlertEvent) -> bool:
        """Send *event* as an e-mail.

        Returns:
            ``True`` on success, ``False`` on failure (logs a warning).
        """
        if not self._smtp_host:
            logger.warning(
                "EmailChannel: no SMTP host configured "
                "(set CODEX_ALERT_SMTP_HOST or pass smtp_host=...)"
            )
            return False
        if not self._to_addrs:
            logger.warning(
                "EmailChannel: no recipient addresses configured "
                "(set CODEX_ALERT_TO or pass to_addrs=...)"
            )
            return False

        body = self._build_body(event)
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = f"[{event.severity.value.upper()}] {event.title}"
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)

        try:
            if self._smtp_port == _STARTTLS_PORT:
                smtp: Any = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            else:
                smtp = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)

            with smtp:
                if self._username and self._password:
                    smtp.login(self._username, self._password)
                smtp.sendmail(self._from_addr, self._to_addrs, msg.as_string())
            return True
        except smtplib.SMTPException as exc:
            logger.warning("EmailChannel: SMTP error — %s", exc)
            return False
        except OSError as exc:
            logger.warning("EmailChannel: network error — %s", exc)
            return False
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover — unexpected errors
            logger.warning("EmailChannel: unexpected error — %s", exc)
            return False

    # ------------------------------------------------------------------
    def _build_body(self, event: AlertEvent) -> str:
        lines = [
            f"Title:     {event.title}",
            f"Severity:  {event.severity.value}",
            f"Timestamp: {event.timestamp or '—'}",
        ]
        if event.run_id:
            lines.append(f"Run ID:    {event.run_id}")
        if event.epoch:
            lines.append(f"Epoch:     {event.epoch}")
        lines.append("")
        lines.append(event.message)
        if event.metadata:
            lines.append("")
            lines.append("Metadata:")
            for key, value in event.metadata.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)

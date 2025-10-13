from __future__ import annotations

import re

_EMAIL = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
_PHONE = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4})")
_GPL = re.compile(r"GNU GENERAL PUBLIC LICENSE|GPL v[23]", re.I)


def scrub(text: str, *, allow_gpl: bool = False) -> tuple[str, dict]:
    flags = {"pii_email": False, "pii_phone": False, "license_gpl": False}

    def mask_email(m: re.Match) -> str:
        flags["pii_email"] = True
        u, d = m.group(1), m.group(2)
        return u[:2] + "***@" + ("***" + d[-4:])

    def mask_phone(m: re.Match) -> str:
        flags["pii_phone"] = True
        return "[PHONE_REDACTED]"

    out = _EMAIL.sub(mask_email, text)
    out = _PHONE.sub(mask_phone, out)
    if _GPL.search(out):
        flags["license_gpl"] = True
        if not allow_gpl:
            out = "[LICENSE_BLOCKED_GPL]\n"
    return out, flags

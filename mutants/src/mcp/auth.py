"""Authentication and authorization primitives for MCP tests."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any, Optional
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_hash_credential__mutmut_orig(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode("utf-8")
    else:
        data = credential
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_1(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = None
    else:
        data = credential
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_2(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode(None)
    else:
        data = credential
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_3(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode("XXutf-8XX")
    else:
        data = credential
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_4(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode("UTF-8")
    else:
        data = credential
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_5(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode("utf-8")
    else:
        data = None
    return hashlib.sha256(data).hexdigest()


def x_hash_credential__mutmut_6(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    if isinstance(credential, str):
        data = credential.encode("utf-8")
    else:
        data = credential
    return hashlib.sha256(None).hexdigest()

x_hash_credential__mutmut_mutants : ClassVar[MutantDict] = {
'x_hash_credential__mutmut_1': x_hash_credential__mutmut_1, 
    'x_hash_credential__mutmut_2': x_hash_credential__mutmut_2, 
    'x_hash_credential__mutmut_3': x_hash_credential__mutmut_3, 
    'x_hash_credential__mutmut_4': x_hash_credential__mutmut_4, 
    'x_hash_credential__mutmut_5': x_hash_credential__mutmut_5, 
    'x_hash_credential__mutmut_6': x_hash_credential__mutmut_6
}

def hash_credential(*args, **kwargs):
    result = _mutmut_trampoline(x_hash_credential__mutmut_orig, x_hash_credential__mutmut_mutants, args, kwargs)
    return result 

hash_credential.__signature__ = _mutmut_signature(x_hash_credential__mutmut_orig)
x_hash_credential__mutmut_orig.__name__ = 'x_hash_credential'


@dataclass(frozen=True)
class Principal:
    """Represents an authenticated actor within the MCP system."""

    principal_id: str

    @classmethod
    def from_credential(cls, credential: str | bytes) -> "Principal":
        """Create a principal based on a hashed credential."""

        hashed = hash_credential(credential)
        return cls(principal_id=hashed)  # Use full hash for security


class MCPAuthenticator:
    """Simple authenticator that issues deterministic session tokens."""

    def xǁMCPAuthenticatorǁ__init____mutmut_orig(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = session_seed or secrets.token_bytes(32)

    def xǁMCPAuthenticatorǁ__init____mutmut_1(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = None

    def xǁMCPAuthenticatorǁ__init____mutmut_2(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = session_seed and secrets.token_bytes(32)

    def xǁMCPAuthenticatorǁ__init____mutmut_3(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = session_seed or secrets.token_bytes(None)

    def xǁMCPAuthenticatorǁ__init____mutmut_4(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = session_seed or secrets.token_bytes(33)
    
    xǁMCPAuthenticatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthenticatorǁ__init____mutmut_1': xǁMCPAuthenticatorǁ__init____mutmut_1, 
        'xǁMCPAuthenticatorǁ__init____mutmut_2': xǁMCPAuthenticatorǁ__init____mutmut_2, 
        'xǁMCPAuthenticatorǁ__init____mutmut_3': xǁMCPAuthenticatorǁ__init____mutmut_3, 
        'xǁMCPAuthenticatorǁ__init____mutmut_4': xǁMCPAuthenticatorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthenticatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthenticatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPAuthenticatorǁ__init____mutmut_orig)
    xǁMCPAuthenticatorǁ__init____mutmut_orig.__name__ = 'xǁMCPAuthenticatorǁ__init__'

    def xǁMCPAuthenticatorǁauthenticate__mutmut_orig(self, credential: Optional[str]) -> Optional[Principal]:
        """Authenticate a credential and return a principal if valid."""

        if not credential:
            return None
        return Principal.from_credential(credential)

    def xǁMCPAuthenticatorǁauthenticate__mutmut_1(self, credential: Optional[str]) -> Optional[Principal]:
        """Authenticate a credential and return a principal if valid."""

        if credential:
            return None
        return Principal.from_credential(credential)

    def xǁMCPAuthenticatorǁauthenticate__mutmut_2(self, credential: Optional[str]) -> Optional[Principal]:
        """Authenticate a credential and return a principal if valid."""

        if not credential:
            return None
        return Principal.from_credential(None)
    
    xǁMCPAuthenticatorǁauthenticate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthenticatorǁauthenticate__mutmut_1': xǁMCPAuthenticatorǁauthenticate__mutmut_1, 
        'xǁMCPAuthenticatorǁauthenticate__mutmut_2': xǁMCPAuthenticatorǁauthenticate__mutmut_2
    }
    
    def authenticate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthenticatorǁauthenticate__mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthenticatorǁauthenticate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    authenticate.__signature__ = _mutmut_signature(xǁMCPAuthenticatorǁauthenticate__mutmut_orig)
    xǁMCPAuthenticatorǁauthenticate__mutmut_orig.__name__ = 'xǁMCPAuthenticatorǁauthenticate'

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_orig(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_1(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = None
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_2(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed - principal.principal_id.encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_3(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode(None)
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_4(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode("XXutf-8XX")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_5(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode("UTF-8")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthenticatorǁgenerate_session_token__mutmut_6(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode("utf-8")
        return hashlib.sha256(None).hexdigest()
    
    xǁMCPAuthenticatorǁgenerate_session_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_1': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_1, 
        'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_2': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_2, 
        'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_3': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_3, 
        'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_4': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_4, 
        'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_5': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_5, 
        'xǁMCPAuthenticatorǁgenerate_session_token__mutmut_6': xǁMCPAuthenticatorǁgenerate_session_token__mutmut_6
    }
    
    def generate_session_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthenticatorǁgenerate_session_token__mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthenticatorǁgenerate_session_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_session_token.__signature__ = _mutmut_signature(xǁMCPAuthenticatorǁgenerate_session_token__mutmut_orig)
    xǁMCPAuthenticatorǁgenerate_session_token__mutmut_orig.__name__ = 'xǁMCPAuthenticatorǁgenerate_session_token'


class MCPAuthorizer:
    """Permissive authorizer with deterministic permission hashing."""

    def xǁMCPAuthorizerǁauthorize__mutmut_orig(
        self,
        principal: Optional[Principal],
        tool_name: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize the principal for the requested tool."""

        _ = payload  # placeholder for richer policies
        return principal is not None

    def xǁMCPAuthorizerǁauthorize__mutmut_1(
        self,
        principal: Optional[Principal],
        tool_name: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize the principal for the requested tool."""

        _ = None  # placeholder for richer policies
        return principal is not None

    def xǁMCPAuthorizerǁauthorize__mutmut_2(
        self,
        principal: Optional[Principal],
        tool_name: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize the principal for the requested tool."""

        _ = payload  # placeholder for richer policies
        return principal is None
    
    xǁMCPAuthorizerǁauthorize__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthorizerǁauthorize__mutmut_1': xǁMCPAuthorizerǁauthorize__mutmut_1, 
        'xǁMCPAuthorizerǁauthorize__mutmut_2': xǁMCPAuthorizerǁauthorize__mutmut_2
    }
    
    def authorize(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthorizerǁauthorize__mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthorizerǁauthorize__mutmut_mutants"), args, kwargs, self)
        return result 
    
    authorize.__signature__ = _mutmut_signature(xǁMCPAuthorizerǁauthorize__mutmut_orig)
    xǁMCPAuthorizerǁauthorize__mutmut_orig.__name__ = 'xǁMCPAuthorizerǁauthorize'

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_orig(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_1(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = True,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_2(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = None
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_3(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(None, tool_name, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_4(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, None, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_5(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, None)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_6(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(tool_name, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_7(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, payload)
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_8(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, )
        if not require_confirm:
            return allowed
        return allowed

    def xǁMCPAuthorizerǁconfirm_authorization__mutmut_9(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, payload)
        if require_confirm:
            return allowed
        return allowed
    
    xǁMCPAuthorizerǁconfirm_authorization__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthorizerǁconfirm_authorization__mutmut_1': xǁMCPAuthorizerǁconfirm_authorization__mutmut_1, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_2': xǁMCPAuthorizerǁconfirm_authorization__mutmut_2, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_3': xǁMCPAuthorizerǁconfirm_authorization__mutmut_3, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_4': xǁMCPAuthorizerǁconfirm_authorization__mutmut_4, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_5': xǁMCPAuthorizerǁconfirm_authorization__mutmut_5, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_6': xǁMCPAuthorizerǁconfirm_authorization__mutmut_6, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_7': xǁMCPAuthorizerǁconfirm_authorization__mutmut_7, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_8': xǁMCPAuthorizerǁconfirm_authorization__mutmut_8, 
        'xǁMCPAuthorizerǁconfirm_authorization__mutmut_9': xǁMCPAuthorizerǁconfirm_authorization__mutmut_9
    }
    
    def confirm_authorization(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthorizerǁconfirm_authorization__mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthorizerǁconfirm_authorization__mutmut_mutants"), args, kwargs, self)
        return result 
    
    confirm_authorization.__signature__ = _mutmut_signature(xǁMCPAuthorizerǁconfirm_authorization__mutmut_orig)
    xǁMCPAuthorizerǁconfirm_authorization__mutmut_orig.__name__ = 'xǁMCPAuthorizerǁconfirm_authorization'

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_orig(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_1(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = None
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_2(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode(None)
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_3(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode("XXutf-8XX")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_4(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode("UTF-8")
        return hashlib.sha256(payload).hexdigest()

    def xǁMCPAuthorizerǁcompute_permission_hash__mutmut_5(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode("utf-8")
        return hashlib.sha256(None).hexdigest()
    
    xǁMCPAuthorizerǁcompute_permission_hash__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPAuthorizerǁcompute_permission_hash__mutmut_1': xǁMCPAuthorizerǁcompute_permission_hash__mutmut_1, 
        'xǁMCPAuthorizerǁcompute_permission_hash__mutmut_2': xǁMCPAuthorizerǁcompute_permission_hash__mutmut_2, 
        'xǁMCPAuthorizerǁcompute_permission_hash__mutmut_3': xǁMCPAuthorizerǁcompute_permission_hash__mutmut_3, 
        'xǁMCPAuthorizerǁcompute_permission_hash__mutmut_4': xǁMCPAuthorizerǁcompute_permission_hash__mutmut_4, 
        'xǁMCPAuthorizerǁcompute_permission_hash__mutmut_5': xǁMCPAuthorizerǁcompute_permission_hash__mutmut_5
    }
    
    def compute_permission_hash(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPAuthorizerǁcompute_permission_hash__mutmut_orig"), object.__getattribute__(self, "xǁMCPAuthorizerǁcompute_permission_hash__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_permission_hash.__signature__ = _mutmut_signature(xǁMCPAuthorizerǁcompute_permission_hash__mutmut_orig)
    xǁMCPAuthorizerǁcompute_permission_hash__mutmut_orig.__name__ = 'xǁMCPAuthorizerǁcompute_permission_hash'


# Backwards compatible aliases for older docs/tests
BasicAuthenticator = MCPAuthenticator
AllowAllAuthorizer = MCPAuthorizer

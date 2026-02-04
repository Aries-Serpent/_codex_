"""
Authentication exceptions for Codex platform.

Provides specific exception types for authentication and authorization errors.
"""

from typing import Optional
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


class AuthError(Exception):
    """Base authentication error."""
    
    def xǁAuthErrorǁ__init____mutmut_orig(self, message: str, code: str = "auth_error"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.code = code
    
    def xǁAuthErrorǁ__init____mutmut_1(self, message: str, code: str = "XXauth_errorXX"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.code = code
    
    def xǁAuthErrorǁ__init____mutmut_2(self, message: str, code: str = "AUTH_ERROR"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.code = code
    
    def xǁAuthErrorǁ__init____mutmut_3(self, message: str, code: str = "auth_error"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(None)
        self.message = message
        self.code = code
    
    def xǁAuthErrorǁ__init____mutmut_4(self, message: str, code: str = "auth_error"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = None
        self.code = code
    
    def xǁAuthErrorǁ__init____mutmut_5(self, message: str, code: str = "auth_error"):
        """
        Initialize auth error.
        
        Args:
            message: Error message
            code: Error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.code = None
    
    xǁAuthErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthErrorǁ__init____mutmut_1': xǁAuthErrorǁ__init____mutmut_1, 
        'xǁAuthErrorǁ__init____mutmut_2': xǁAuthErrorǁ__init____mutmut_2, 
        'xǁAuthErrorǁ__init____mutmut_3': xǁAuthErrorǁ__init____mutmut_3, 
        'xǁAuthErrorǁ__init____mutmut_4': xǁAuthErrorǁ__init____mutmut_4, 
        'xǁAuthErrorǁ__init____mutmut_5': xǁAuthErrorǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAuthErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAuthErrorǁ__init____mutmut_orig)
    xǁAuthErrorǁ__init____mutmut_orig.__name__ = 'xǁAuthErrorǁ__init__'


class AuthenticationError(AuthError):
    """Authentication failed (401)."""
    
    def xǁAuthenticationErrorǁ__init____mutmut_orig(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_1(self, message: str = "XXAuthentication requiredXX", 
                 code: str = "authentication_required"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_2(self, message: str = "authentication required", 
                 code: str = "authentication_required"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_3(self, message: str = "AUTHENTICATION REQUIRED", 
                 code: str = "authentication_required"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_4(self, message: str = "Authentication required", 
                 code: str = "XXauthentication_requiredXX"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_5(self, message: str = "Authentication required", 
                 code: str = "AUTHENTICATION_REQUIRED"):
        super().__init__(message, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_6(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(None, code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_7(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(message, None)
    
    def xǁAuthenticationErrorǁ__init____mutmut_8(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(code)
    
    def xǁAuthenticationErrorǁ__init____mutmut_9(self, message: str = "Authentication required", 
                 code: str = "authentication_required"):
        super().__init__(message, )
    
    xǁAuthenticationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthenticationErrorǁ__init____mutmut_1': xǁAuthenticationErrorǁ__init____mutmut_1, 
        'xǁAuthenticationErrorǁ__init____mutmut_2': xǁAuthenticationErrorǁ__init____mutmut_2, 
        'xǁAuthenticationErrorǁ__init____mutmut_3': xǁAuthenticationErrorǁ__init____mutmut_3, 
        'xǁAuthenticationErrorǁ__init____mutmut_4': xǁAuthenticationErrorǁ__init____mutmut_4, 
        'xǁAuthenticationErrorǁ__init____mutmut_5': xǁAuthenticationErrorǁ__init____mutmut_5, 
        'xǁAuthenticationErrorǁ__init____mutmut_6': xǁAuthenticationErrorǁ__init____mutmut_6, 
        'xǁAuthenticationErrorǁ__init____mutmut_7': xǁAuthenticationErrorǁ__init____mutmut_7, 
        'xǁAuthenticationErrorǁ__init____mutmut_8': xǁAuthenticationErrorǁ__init____mutmut_8, 
        'xǁAuthenticationErrorǁ__init____mutmut_9': xǁAuthenticationErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthenticationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAuthenticationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAuthenticationErrorǁ__init____mutmut_orig)
    xǁAuthenticationErrorǁ__init____mutmut_orig.__name__ = 'xǁAuthenticationErrorǁ__init__'


class InvalidTokenError(AuthenticationError):
    """Token is invalid or malformed."""
    
    def xǁInvalidTokenErrorǁ__init____mutmut_orig(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_1(self, message: str = "XXInvalid tokenXX", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_2(self, message: str = "invalid token", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_3(self, message: str = "INVALID TOKEN", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_4(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(None, "invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_5(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, None)
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_6(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__("invalid_token")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_7(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, )
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_8(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, "XXinvalid_tokenXX")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_9(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, "INVALID_TOKEN")
        self.reason = reason
    
    def xǁInvalidTokenErrorǁ__init____mutmut_10(self, message: str = "Invalid token", reason: Optional[str] = None):
        super().__init__(message, "invalid_token")
        self.reason = None
    
    xǁInvalidTokenErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInvalidTokenErrorǁ__init____mutmut_1': xǁInvalidTokenErrorǁ__init____mutmut_1, 
        'xǁInvalidTokenErrorǁ__init____mutmut_2': xǁInvalidTokenErrorǁ__init____mutmut_2, 
        'xǁInvalidTokenErrorǁ__init____mutmut_3': xǁInvalidTokenErrorǁ__init____mutmut_3, 
        'xǁInvalidTokenErrorǁ__init____mutmut_4': xǁInvalidTokenErrorǁ__init____mutmut_4, 
        'xǁInvalidTokenErrorǁ__init____mutmut_5': xǁInvalidTokenErrorǁ__init____mutmut_5, 
        'xǁInvalidTokenErrorǁ__init____mutmut_6': xǁInvalidTokenErrorǁ__init____mutmut_6, 
        'xǁInvalidTokenErrorǁ__init____mutmut_7': xǁInvalidTokenErrorǁ__init____mutmut_7, 
        'xǁInvalidTokenErrorǁ__init____mutmut_8': xǁInvalidTokenErrorǁ__init____mutmut_8, 
        'xǁInvalidTokenErrorǁ__init____mutmut_9': xǁInvalidTokenErrorǁ__init____mutmut_9, 
        'xǁInvalidTokenErrorǁ__init____mutmut_10': xǁInvalidTokenErrorǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInvalidTokenErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInvalidTokenErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInvalidTokenErrorǁ__init____mutmut_orig)
    xǁInvalidTokenErrorǁ__init____mutmut_orig.__name__ = 'xǁInvalidTokenErrorǁ__init__'


class TokenExpiredError(AuthenticationError):
    """Token has expired."""
    
    def xǁTokenExpiredErrorǁ__init____mutmut_orig(self, message: str = "Token expired"):
        super().__init__(message, "token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_1(self, message: str = "XXToken expiredXX"):
        super().__init__(message, "token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_2(self, message: str = "token expired"):
        super().__init__(message, "token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_3(self, message: str = "TOKEN EXPIRED"):
        super().__init__(message, "token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_4(self, message: str = "Token expired"):
        super().__init__(None, "token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_5(self, message: str = "Token expired"):
        super().__init__(message, None)
    
    def xǁTokenExpiredErrorǁ__init____mutmut_6(self, message: str = "Token expired"):
        super().__init__("token_expired")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_7(self, message: str = "Token expired"):
        super().__init__(message, )
    
    def xǁTokenExpiredErrorǁ__init____mutmut_8(self, message: str = "Token expired"):
        super().__init__(message, "XXtoken_expiredXX")
    
    def xǁTokenExpiredErrorǁ__init____mutmut_9(self, message: str = "Token expired"):
        super().__init__(message, "TOKEN_EXPIRED")
    
    xǁTokenExpiredErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenExpiredErrorǁ__init____mutmut_1': xǁTokenExpiredErrorǁ__init____mutmut_1, 
        'xǁTokenExpiredErrorǁ__init____mutmut_2': xǁTokenExpiredErrorǁ__init____mutmut_2, 
        'xǁTokenExpiredErrorǁ__init____mutmut_3': xǁTokenExpiredErrorǁ__init____mutmut_3, 
        'xǁTokenExpiredErrorǁ__init____mutmut_4': xǁTokenExpiredErrorǁ__init____mutmut_4, 
        'xǁTokenExpiredErrorǁ__init____mutmut_5': xǁTokenExpiredErrorǁ__init____mutmut_5, 
        'xǁTokenExpiredErrorǁ__init____mutmut_6': xǁTokenExpiredErrorǁ__init____mutmut_6, 
        'xǁTokenExpiredErrorǁ__init____mutmut_7': xǁTokenExpiredErrorǁ__init____mutmut_7, 
        'xǁTokenExpiredErrorǁ__init____mutmut_8': xǁTokenExpiredErrorǁ__init____mutmut_8, 
        'xǁTokenExpiredErrorǁ__init____mutmut_9': xǁTokenExpiredErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenExpiredErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenExpiredErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenExpiredErrorǁ__init____mutmut_orig)
    xǁTokenExpiredErrorǁ__init____mutmut_orig.__name__ = 'xǁTokenExpiredErrorǁ__init__'


class TokenRevokedError(AuthenticationError):
    """Token has been revoked."""
    
    def xǁTokenRevokedErrorǁ__init____mutmut_orig(self, message: str = "Token revoked"):
        super().__init__(message, "token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_1(self, message: str = "XXToken revokedXX"):
        super().__init__(message, "token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_2(self, message: str = "token revoked"):
        super().__init__(message, "token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_3(self, message: str = "TOKEN REVOKED"):
        super().__init__(message, "token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_4(self, message: str = "Token revoked"):
        super().__init__(None, "token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_5(self, message: str = "Token revoked"):
        super().__init__(message, None)
    
    def xǁTokenRevokedErrorǁ__init____mutmut_6(self, message: str = "Token revoked"):
        super().__init__("token_revoked")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_7(self, message: str = "Token revoked"):
        super().__init__(message, )
    
    def xǁTokenRevokedErrorǁ__init____mutmut_8(self, message: str = "Token revoked"):
        super().__init__(message, "XXtoken_revokedXX")
    
    def xǁTokenRevokedErrorǁ__init____mutmut_9(self, message: str = "Token revoked"):
        super().__init__(message, "TOKEN_REVOKED")
    
    xǁTokenRevokedErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRevokedErrorǁ__init____mutmut_1': xǁTokenRevokedErrorǁ__init____mutmut_1, 
        'xǁTokenRevokedErrorǁ__init____mutmut_2': xǁTokenRevokedErrorǁ__init____mutmut_2, 
        'xǁTokenRevokedErrorǁ__init____mutmut_3': xǁTokenRevokedErrorǁ__init____mutmut_3, 
        'xǁTokenRevokedErrorǁ__init____mutmut_4': xǁTokenRevokedErrorǁ__init____mutmut_4, 
        'xǁTokenRevokedErrorǁ__init____mutmut_5': xǁTokenRevokedErrorǁ__init____mutmut_5, 
        'xǁTokenRevokedErrorǁ__init____mutmut_6': xǁTokenRevokedErrorǁ__init____mutmut_6, 
        'xǁTokenRevokedErrorǁ__init____mutmut_7': xǁTokenRevokedErrorǁ__init____mutmut_7, 
        'xǁTokenRevokedErrorǁ__init____mutmut_8': xǁTokenRevokedErrorǁ__init____mutmut_8, 
        'xǁTokenRevokedErrorǁ__init____mutmut_9': xǁTokenRevokedErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRevokedErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenRevokedErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenRevokedErrorǁ__init____mutmut_orig)
    xǁTokenRevokedErrorǁ__init____mutmut_orig.__name__ = 'xǁTokenRevokedErrorǁ__init__'


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials provided."""
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_orig(self, message: str = "Invalid credentials"):
        super().__init__(message, "invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_1(self, message: str = "XXInvalid credentialsXX"):
        super().__init__(message, "invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_2(self, message: str = "invalid credentials"):
        super().__init__(message, "invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_3(self, message: str = "INVALID CREDENTIALS"):
        super().__init__(message, "invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_4(self, message: str = "Invalid credentials"):
        super().__init__(None, "invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_5(self, message: str = "Invalid credentials"):
        super().__init__(message, None)
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_6(self, message: str = "Invalid credentials"):
        super().__init__("invalid_credentials")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_7(self, message: str = "Invalid credentials"):
        super().__init__(message, )
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_8(self, message: str = "Invalid credentials"):
        super().__init__(message, "XXinvalid_credentialsXX")
    
    def xǁInvalidCredentialsErrorǁ__init____mutmut_9(self, message: str = "Invalid credentials"):
        super().__init__(message, "INVALID_CREDENTIALS")
    
    xǁInvalidCredentialsErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInvalidCredentialsErrorǁ__init____mutmut_1': xǁInvalidCredentialsErrorǁ__init____mutmut_1, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_2': xǁInvalidCredentialsErrorǁ__init____mutmut_2, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_3': xǁInvalidCredentialsErrorǁ__init____mutmut_3, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_4': xǁInvalidCredentialsErrorǁ__init____mutmut_4, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_5': xǁInvalidCredentialsErrorǁ__init____mutmut_5, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_6': xǁInvalidCredentialsErrorǁ__init____mutmut_6, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_7': xǁInvalidCredentialsErrorǁ__init____mutmut_7, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_8': xǁInvalidCredentialsErrorǁ__init____mutmut_8, 
        'xǁInvalidCredentialsErrorǁ__init____mutmut_9': xǁInvalidCredentialsErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInvalidCredentialsErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInvalidCredentialsErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInvalidCredentialsErrorǁ__init____mutmut_orig)
    xǁInvalidCredentialsErrorǁ__init____mutmut_orig.__name__ = 'xǁInvalidCredentialsErrorǁ__init__'


class MFARequiredError(AuthenticationError):
    """MFA verification is required."""
    
    def xǁMFARequiredErrorǁ__init____mutmut_orig(self, message: str = "MFA verification required"):
        super().__init__(message, "mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_1(self, message: str = "XXMFA verification requiredXX"):
        super().__init__(message, "mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_2(self, message: str = "mfa verification required"):
        super().__init__(message, "mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_3(self, message: str = "MFA VERIFICATION REQUIRED"):
        super().__init__(message, "mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_4(self, message: str = "MFA verification required"):
        super().__init__(None, "mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_5(self, message: str = "MFA verification required"):
        super().__init__(message, None)
    
    def xǁMFARequiredErrorǁ__init____mutmut_6(self, message: str = "MFA verification required"):
        super().__init__("mfa_required")
    
    def xǁMFARequiredErrorǁ__init____mutmut_7(self, message: str = "MFA verification required"):
        super().__init__(message, )
    
    def xǁMFARequiredErrorǁ__init____mutmut_8(self, message: str = "MFA verification required"):
        super().__init__(message, "XXmfa_requiredXX")
    
    def xǁMFARequiredErrorǁ__init____mutmut_9(self, message: str = "MFA verification required"):
        super().__init__(message, "MFA_REQUIRED")
    
    xǁMFARequiredErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFARequiredErrorǁ__init____mutmut_1': xǁMFARequiredErrorǁ__init____mutmut_1, 
        'xǁMFARequiredErrorǁ__init____mutmut_2': xǁMFARequiredErrorǁ__init____mutmut_2, 
        'xǁMFARequiredErrorǁ__init____mutmut_3': xǁMFARequiredErrorǁ__init____mutmut_3, 
        'xǁMFARequiredErrorǁ__init____mutmut_4': xǁMFARequiredErrorǁ__init____mutmut_4, 
        'xǁMFARequiredErrorǁ__init____mutmut_5': xǁMFARequiredErrorǁ__init____mutmut_5, 
        'xǁMFARequiredErrorǁ__init____mutmut_6': xǁMFARequiredErrorǁ__init____mutmut_6, 
        'xǁMFARequiredErrorǁ__init____mutmut_7': xǁMFARequiredErrorǁ__init____mutmut_7, 
        'xǁMFARequiredErrorǁ__init____mutmut_8': xǁMFARequiredErrorǁ__init____mutmut_8, 
        'xǁMFARequiredErrorǁ__init____mutmut_9': xǁMFARequiredErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFARequiredErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMFARequiredErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMFARequiredErrorǁ__init____mutmut_orig)
    xǁMFARequiredErrorǁ__init____mutmut_orig.__name__ = 'xǁMFARequiredErrorǁ__init__'


class MFAVerificationError(AuthenticationError):
    """MFA verification failed."""
    
    def xǁMFAVerificationErrorǁ__init____mutmut_orig(self, message: str = "MFA verification failed"):
        super().__init__(message, "mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_1(self, message: str = "XXMFA verification failedXX"):
        super().__init__(message, "mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_2(self, message: str = "mfa verification failed"):
        super().__init__(message, "mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_3(self, message: str = "MFA VERIFICATION FAILED"):
        super().__init__(message, "mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_4(self, message: str = "MFA verification failed"):
        super().__init__(None, "mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_5(self, message: str = "MFA verification failed"):
        super().__init__(message, None)
    
    def xǁMFAVerificationErrorǁ__init____mutmut_6(self, message: str = "MFA verification failed"):
        super().__init__("mfa_failed")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_7(self, message: str = "MFA verification failed"):
        super().__init__(message, )
    
    def xǁMFAVerificationErrorǁ__init____mutmut_8(self, message: str = "MFA verification failed"):
        super().__init__(message, "XXmfa_failedXX")
    
    def xǁMFAVerificationErrorǁ__init____mutmut_9(self, message: str = "MFA verification failed"):
        super().__init__(message, "MFA_FAILED")
    
    xǁMFAVerificationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAVerificationErrorǁ__init____mutmut_1': xǁMFAVerificationErrorǁ__init____mutmut_1, 
        'xǁMFAVerificationErrorǁ__init____mutmut_2': xǁMFAVerificationErrorǁ__init____mutmut_2, 
        'xǁMFAVerificationErrorǁ__init____mutmut_3': xǁMFAVerificationErrorǁ__init____mutmut_3, 
        'xǁMFAVerificationErrorǁ__init____mutmut_4': xǁMFAVerificationErrorǁ__init____mutmut_4, 
        'xǁMFAVerificationErrorǁ__init____mutmut_5': xǁMFAVerificationErrorǁ__init____mutmut_5, 
        'xǁMFAVerificationErrorǁ__init____mutmut_6': xǁMFAVerificationErrorǁ__init____mutmut_6, 
        'xǁMFAVerificationErrorǁ__init____mutmut_7': xǁMFAVerificationErrorǁ__init____mutmut_7, 
        'xǁMFAVerificationErrorǁ__init____mutmut_8': xǁMFAVerificationErrorǁ__init____mutmut_8, 
        'xǁMFAVerificationErrorǁ__init____mutmut_9': xǁMFAVerificationErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAVerificationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMFAVerificationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMFAVerificationErrorǁ__init____mutmut_orig)
    xǁMFAVerificationErrorǁ__init____mutmut_orig.__name__ = 'xǁMFAVerificationErrorǁ__init__'


class AuthorizationError(AuthError):
    """Authorization failed (403)."""
    
    def xǁAuthorizationErrorǁ__init____mutmut_orig(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_1(self, message: str = "XXAccess deniedXX", 
                 code: str = "access_denied"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_2(self, message: str = "access denied", 
                 code: str = "access_denied"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_3(self, message: str = "ACCESS DENIED", 
                 code: str = "access_denied"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_4(self, message: str = "Access denied", 
                 code: str = "XXaccess_deniedXX"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_5(self, message: str = "Access denied", 
                 code: str = "ACCESS_DENIED"):
        super().__init__(message, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_6(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(None, code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_7(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(message, None)
    
    def xǁAuthorizationErrorǁ__init____mutmut_8(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(code)
    
    def xǁAuthorizationErrorǁ__init____mutmut_9(self, message: str = "Access denied", 
                 code: str = "access_denied"):
        super().__init__(message, )
    
    xǁAuthorizationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthorizationErrorǁ__init____mutmut_1': xǁAuthorizationErrorǁ__init____mutmut_1, 
        'xǁAuthorizationErrorǁ__init____mutmut_2': xǁAuthorizationErrorǁ__init____mutmut_2, 
        'xǁAuthorizationErrorǁ__init____mutmut_3': xǁAuthorizationErrorǁ__init____mutmut_3, 
        'xǁAuthorizationErrorǁ__init____mutmut_4': xǁAuthorizationErrorǁ__init____mutmut_4, 
        'xǁAuthorizationErrorǁ__init____mutmut_5': xǁAuthorizationErrorǁ__init____mutmut_5, 
        'xǁAuthorizationErrorǁ__init____mutmut_6': xǁAuthorizationErrorǁ__init____mutmut_6, 
        'xǁAuthorizationErrorǁ__init____mutmut_7': xǁAuthorizationErrorǁ__init____mutmut_7, 
        'xǁAuthorizationErrorǁ__init____mutmut_8': xǁAuthorizationErrorǁ__init____mutmut_8, 
        'xǁAuthorizationErrorǁ__init____mutmut_9': xǁAuthorizationErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthorizationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAuthorizationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAuthorizationErrorǁ__init____mutmut_orig)
    xǁAuthorizationErrorǁ__init____mutmut_orig.__name__ = 'xǁAuthorizationErrorǁ__init__'


class InsufficientScopesError(AuthorizationError):
    """Required scopes not present."""
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_orig(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_1(self, required_scopes: Optional[list] = None, 
                 message: str = "XXInsufficient permissionsXX"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_2(self, required_scopes: Optional[list] = None, 
                 message: str = "insufficient permissions"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_3(self, required_scopes: Optional[list] = None, 
                 message: str = "INSUFFICIENT PERMISSIONS"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_4(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(None, "insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_5(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, None)
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_6(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__("insufficient_scopes")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_7(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, )
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_8(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "XXinsufficient_scopesXX")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_9(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "INSUFFICIENT_SCOPES")
        self.required_scopes = required_scopes or []
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_10(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = None
    
    def xǁInsufficientScopesErrorǁ__init____mutmut_11(self, required_scopes: Optional[list] = None, 
                 message: str = "Insufficient permissions"):
        super().__init__(message, "insufficient_scopes")
        self.required_scopes = required_scopes and []
    
    xǁInsufficientScopesErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInsufficientScopesErrorǁ__init____mutmut_1': xǁInsufficientScopesErrorǁ__init____mutmut_1, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_2': xǁInsufficientScopesErrorǁ__init____mutmut_2, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_3': xǁInsufficientScopesErrorǁ__init____mutmut_3, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_4': xǁInsufficientScopesErrorǁ__init____mutmut_4, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_5': xǁInsufficientScopesErrorǁ__init____mutmut_5, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_6': xǁInsufficientScopesErrorǁ__init____mutmut_6, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_7': xǁInsufficientScopesErrorǁ__init____mutmut_7, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_8': xǁInsufficientScopesErrorǁ__init____mutmut_8, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_9': xǁInsufficientScopesErrorǁ__init____mutmut_9, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_10': xǁInsufficientScopesErrorǁ__init____mutmut_10, 
        'xǁInsufficientScopesErrorǁ__init____mutmut_11': xǁInsufficientScopesErrorǁ__init____mutmut_11
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInsufficientScopesErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInsufficientScopesErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInsufficientScopesErrorǁ__init____mutmut_orig)
    xǁInsufficientScopesErrorǁ__init____mutmut_orig.__name__ = 'xǁInsufficientScopesErrorǁ__init__'


class RateLimitError(AuthError):
    """Rate limit exceeded (429)."""
    
    def xǁRateLimitErrorǁ__init____mutmut_orig(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_1(self, message: str = "XXRate limit exceededXX", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_2(self, message: str = "rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_3(self, message: str = "RATE LIMIT EXCEEDED", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_4(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(None, "rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_5(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, None)
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_6(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__("rate_limit_exceeded")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_7(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, )
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_8(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "XXrate_limit_exceededXX")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_9(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after
    
    def xǁRateLimitErrorǁ__init____mutmut_10(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None):
        super().__init__(message, "rate_limit_exceeded")
        self.retry_after = None
    
    xǁRateLimitErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimitErrorǁ__init____mutmut_1': xǁRateLimitErrorǁ__init____mutmut_1, 
        'xǁRateLimitErrorǁ__init____mutmut_2': xǁRateLimitErrorǁ__init____mutmut_2, 
        'xǁRateLimitErrorǁ__init____mutmut_3': xǁRateLimitErrorǁ__init____mutmut_3, 
        'xǁRateLimitErrorǁ__init____mutmut_4': xǁRateLimitErrorǁ__init____mutmut_4, 
        'xǁRateLimitErrorǁ__init____mutmut_5': xǁRateLimitErrorǁ__init____mutmut_5, 
        'xǁRateLimitErrorǁ__init____mutmut_6': xǁRateLimitErrorǁ__init____mutmut_6, 
        'xǁRateLimitErrorǁ__init____mutmut_7': xǁRateLimitErrorǁ__init____mutmut_7, 
        'xǁRateLimitErrorǁ__init____mutmut_8': xǁRateLimitErrorǁ__init____mutmut_8, 
        'xǁRateLimitErrorǁ__init____mutmut_9': xǁRateLimitErrorǁ__init____mutmut_9, 
        'xǁRateLimitErrorǁ__init____mutmut_10': xǁRateLimitErrorǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimitErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRateLimitErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRateLimitErrorǁ__init____mutmut_orig)
    xǁRateLimitErrorǁ__init____mutmut_orig.__name__ = 'xǁRateLimitErrorǁ__init__'


class OAuthError(AuthError):
    """OAuth-specific error."""
    
    def xǁOAuthErrorǁ__init____mutmut_orig(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_1(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(None, oauth_error or "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_2(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, None)
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_3(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(oauth_error or "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_4(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, )
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_5(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error and "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_6(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "XXoauth_errorXX")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_7(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "OAUTH_ERROR")
        self.oauth_error = oauth_error
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_8(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "oauth_error")
        self.oauth_error = None
        self.error_description = error_description
    
    def xǁOAuthErrorǁ__init____mutmut_9(self, message: str, oauth_error: Optional[str] = None,
                 error_description: Optional[str] = None):
        super().__init__(message, oauth_error or "oauth_error")
        self.oauth_error = oauth_error
        self.error_description = None
    
    xǁOAuthErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁOAuthErrorǁ__init____mutmut_1': xǁOAuthErrorǁ__init____mutmut_1, 
        'xǁOAuthErrorǁ__init____mutmut_2': xǁOAuthErrorǁ__init____mutmut_2, 
        'xǁOAuthErrorǁ__init____mutmut_3': xǁOAuthErrorǁ__init____mutmut_3, 
        'xǁOAuthErrorǁ__init____mutmut_4': xǁOAuthErrorǁ__init____mutmut_4, 
        'xǁOAuthErrorǁ__init____mutmut_5': xǁOAuthErrorǁ__init____mutmut_5, 
        'xǁOAuthErrorǁ__init____mutmut_6': xǁOAuthErrorǁ__init____mutmut_6, 
        'xǁOAuthErrorǁ__init____mutmut_7': xǁOAuthErrorǁ__init____mutmut_7, 
        'xǁOAuthErrorǁ__init____mutmut_8': xǁOAuthErrorǁ__init____mutmut_8, 
        'xǁOAuthErrorǁ__init____mutmut_9': xǁOAuthErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁOAuthErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁOAuthErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁOAuthErrorǁ__init____mutmut_orig)
    xǁOAuthErrorǁ__init____mutmut_orig.__name__ = 'xǁOAuthErrorǁ__init__'


class StateValidationError(OAuthError):
    """OAuth state validation failed."""
    
    def xǁStateValidationErrorǁ__init____mutmut_orig(self, message: str = "Invalid state parameter"):
        super().__init__(message, "invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_1(self, message: str = "XXInvalid state parameterXX"):
        super().__init__(message, "invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_2(self, message: str = "invalid state parameter"):
        super().__init__(message, "invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_3(self, message: str = "INVALID STATE PARAMETER"):
        super().__init__(message, "invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_4(self, message: str = "Invalid state parameter"):
        super().__init__(None, "invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_5(self, message: str = "Invalid state parameter"):
        super().__init__(message, None)
    
    def xǁStateValidationErrorǁ__init____mutmut_6(self, message: str = "Invalid state parameter"):
        super().__init__("invalid_state")
    
    def xǁStateValidationErrorǁ__init____mutmut_7(self, message: str = "Invalid state parameter"):
        super().__init__(message, )
    
    def xǁStateValidationErrorǁ__init____mutmut_8(self, message: str = "Invalid state parameter"):
        super().__init__(message, "XXinvalid_stateXX")
    
    def xǁStateValidationErrorǁ__init____mutmut_9(self, message: str = "Invalid state parameter"):
        super().__init__(message, "INVALID_STATE")
    
    xǁStateValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁStateValidationErrorǁ__init____mutmut_1': xǁStateValidationErrorǁ__init____mutmut_1, 
        'xǁStateValidationErrorǁ__init____mutmut_2': xǁStateValidationErrorǁ__init____mutmut_2, 
        'xǁStateValidationErrorǁ__init____mutmut_3': xǁStateValidationErrorǁ__init____mutmut_3, 
        'xǁStateValidationErrorǁ__init____mutmut_4': xǁStateValidationErrorǁ__init____mutmut_4, 
        'xǁStateValidationErrorǁ__init____mutmut_5': xǁStateValidationErrorǁ__init____mutmut_5, 
        'xǁStateValidationErrorǁ__init____mutmut_6': xǁStateValidationErrorǁ__init____mutmut_6, 
        'xǁStateValidationErrorǁ__init____mutmut_7': xǁStateValidationErrorǁ__init____mutmut_7, 
        'xǁStateValidationErrorǁ__init____mutmut_8': xǁStateValidationErrorǁ__init____mutmut_8, 
        'xǁStateValidationErrorǁ__init____mutmut_9': xǁStateValidationErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁStateValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁStateValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁStateValidationErrorǁ__init____mutmut_orig)
    xǁStateValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁStateValidationErrorǁ__init__'


class CodeExchangeError(OAuthError):
    """OAuth code exchange failed."""
    
    def xǁCodeExchangeErrorǁ__init____mutmut_orig(self, message: str = "Code exchange failed"):
        super().__init__(message, "code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_1(self, message: str = "XXCode exchange failedXX"):
        super().__init__(message, "code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_2(self, message: str = "code exchange failed"):
        super().__init__(message, "code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_3(self, message: str = "CODE EXCHANGE FAILED"):
        super().__init__(message, "code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_4(self, message: str = "Code exchange failed"):
        super().__init__(None, "code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_5(self, message: str = "Code exchange failed"):
        super().__init__(message, None)
    
    def xǁCodeExchangeErrorǁ__init____mutmut_6(self, message: str = "Code exchange failed"):
        super().__init__("code_exchange_failed")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_7(self, message: str = "Code exchange failed"):
        super().__init__(message, )
    
    def xǁCodeExchangeErrorǁ__init____mutmut_8(self, message: str = "Code exchange failed"):
        super().__init__(message, "XXcode_exchange_failedXX")
    
    def xǁCodeExchangeErrorǁ__init____mutmut_9(self, message: str = "Code exchange failed"):
        super().__init__(message, "CODE_EXCHANGE_FAILED")
    
    xǁCodeExchangeErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodeExchangeErrorǁ__init____mutmut_1': xǁCodeExchangeErrorǁ__init____mutmut_1, 
        'xǁCodeExchangeErrorǁ__init____mutmut_2': xǁCodeExchangeErrorǁ__init____mutmut_2, 
        'xǁCodeExchangeErrorǁ__init____mutmut_3': xǁCodeExchangeErrorǁ__init____mutmut_3, 
        'xǁCodeExchangeErrorǁ__init____mutmut_4': xǁCodeExchangeErrorǁ__init____mutmut_4, 
        'xǁCodeExchangeErrorǁ__init____mutmut_5': xǁCodeExchangeErrorǁ__init____mutmut_5, 
        'xǁCodeExchangeErrorǁ__init____mutmut_6': xǁCodeExchangeErrorǁ__init____mutmut_6, 
        'xǁCodeExchangeErrorǁ__init____mutmut_7': xǁCodeExchangeErrorǁ__init____mutmut_7, 
        'xǁCodeExchangeErrorǁ__init____mutmut_8': xǁCodeExchangeErrorǁ__init____mutmut_8, 
        'xǁCodeExchangeErrorǁ__init____mutmut_9': xǁCodeExchangeErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodeExchangeErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCodeExchangeErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCodeExchangeErrorǁ__init____mutmut_orig)
    xǁCodeExchangeErrorǁ__init____mutmut_orig.__name__ = 'xǁCodeExchangeErrorǁ__init__'


class APIKeyError(AuthError):
    """API key error."""
    
    def xǁAPIKeyErrorǁ__init____mutmut_orig(self, message: str = "Invalid API key"):
        super().__init__(message, "invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_1(self, message: str = "XXInvalid API keyXX"):
        super().__init__(message, "invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_2(self, message: str = "invalid api key"):
        super().__init__(message, "invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_3(self, message: str = "INVALID API KEY"):
        super().__init__(message, "invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_4(self, message: str = "Invalid API key"):
        super().__init__(None, "invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_5(self, message: str = "Invalid API key"):
        super().__init__(message, None)
    
    def xǁAPIKeyErrorǁ__init____mutmut_6(self, message: str = "Invalid API key"):
        super().__init__("invalid_api_key")
    
    def xǁAPIKeyErrorǁ__init____mutmut_7(self, message: str = "Invalid API key"):
        super().__init__(message, )
    
    def xǁAPIKeyErrorǁ__init____mutmut_8(self, message: str = "Invalid API key"):
        super().__init__(message, "XXinvalid_api_keyXX")
    
    def xǁAPIKeyErrorǁ__init____mutmut_9(self, message: str = "Invalid API key"):
        super().__init__(message, "INVALID_API_KEY")
    
    xǁAPIKeyErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyErrorǁ__init____mutmut_1': xǁAPIKeyErrorǁ__init____mutmut_1, 
        'xǁAPIKeyErrorǁ__init____mutmut_2': xǁAPIKeyErrorǁ__init____mutmut_2, 
        'xǁAPIKeyErrorǁ__init____mutmut_3': xǁAPIKeyErrorǁ__init____mutmut_3, 
        'xǁAPIKeyErrorǁ__init____mutmut_4': xǁAPIKeyErrorǁ__init____mutmut_4, 
        'xǁAPIKeyErrorǁ__init____mutmut_5': xǁAPIKeyErrorǁ__init____mutmut_5, 
        'xǁAPIKeyErrorǁ__init____mutmut_6': xǁAPIKeyErrorǁ__init____mutmut_6, 
        'xǁAPIKeyErrorǁ__init____mutmut_7': xǁAPIKeyErrorǁ__init____mutmut_7, 
        'xǁAPIKeyErrorǁ__init____mutmut_8': xǁAPIKeyErrorǁ__init____mutmut_8, 
        'xǁAPIKeyErrorǁ__init____mutmut_9': xǁAPIKeyErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAPIKeyErrorǁ__init____mutmut_orig)
    xǁAPIKeyErrorǁ__init____mutmut_orig.__name__ = 'xǁAPIKeyErrorǁ__init__'


class APIKeyRevokedError(APIKeyError):
    """API key has been revoked."""
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_orig(self, message: str = "API key revoked"):
        super().__init__(message)
        self.code = "api_key_revoked"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_1(self, message: str = "XXAPI key revokedXX"):
        super().__init__(message)
        self.code = "api_key_revoked"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_2(self, message: str = "api key revoked"):
        super().__init__(message)
        self.code = "api_key_revoked"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_3(self, message: str = "API KEY REVOKED"):
        super().__init__(message)
        self.code = "api_key_revoked"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_4(self, message: str = "API key revoked"):
        super().__init__(None)
        self.code = "api_key_revoked"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_5(self, message: str = "API key revoked"):
        super().__init__(message)
        self.code = None
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_6(self, message: str = "API key revoked"):
        super().__init__(message)
        self.code = "XXapi_key_revokedXX"
    
    def xǁAPIKeyRevokedErrorǁ__init____mutmut_7(self, message: str = "API key revoked"):
        super().__init__(message)
        self.code = "API_KEY_REVOKED"
    
    xǁAPIKeyRevokedErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyRevokedErrorǁ__init____mutmut_1': xǁAPIKeyRevokedErrorǁ__init____mutmut_1, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_2': xǁAPIKeyRevokedErrorǁ__init____mutmut_2, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_3': xǁAPIKeyRevokedErrorǁ__init____mutmut_3, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_4': xǁAPIKeyRevokedErrorǁ__init____mutmut_4, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_5': xǁAPIKeyRevokedErrorǁ__init____mutmut_5, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_6': xǁAPIKeyRevokedErrorǁ__init____mutmut_6, 
        'xǁAPIKeyRevokedErrorǁ__init____mutmut_7': xǁAPIKeyRevokedErrorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyRevokedErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyRevokedErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAPIKeyRevokedErrorǁ__init____mutmut_orig)
    xǁAPIKeyRevokedErrorǁ__init____mutmut_orig.__name__ = 'xǁAPIKeyRevokedErrorǁ__init__'


class SessionError(AuthError):
    """Session-related error."""
    
    def xǁSessionErrorǁ__init____mutmut_orig(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_1(self, message: str = "XXSession errorXX", code: str = "session_error"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_2(self, message: str = "session error", code: str = "session_error"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_3(self, message: str = "SESSION ERROR", code: str = "session_error"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_4(self, message: str = "Session error", code: str = "XXsession_errorXX"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_5(self, message: str = "Session error", code: str = "SESSION_ERROR"):
        super().__init__(message, code)
    
    def xǁSessionErrorǁ__init____mutmut_6(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(None, code)
    
    def xǁSessionErrorǁ__init____mutmut_7(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(message, None)
    
    def xǁSessionErrorǁ__init____mutmut_8(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(code)
    
    def xǁSessionErrorǁ__init____mutmut_9(self, message: str = "Session error", code: str = "session_error"):
        super().__init__(message, )
    
    xǁSessionErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSessionErrorǁ__init____mutmut_1': xǁSessionErrorǁ__init____mutmut_1, 
        'xǁSessionErrorǁ__init____mutmut_2': xǁSessionErrorǁ__init____mutmut_2, 
        'xǁSessionErrorǁ__init____mutmut_3': xǁSessionErrorǁ__init____mutmut_3, 
        'xǁSessionErrorǁ__init____mutmut_4': xǁSessionErrorǁ__init____mutmut_4, 
        'xǁSessionErrorǁ__init____mutmut_5': xǁSessionErrorǁ__init____mutmut_5, 
        'xǁSessionErrorǁ__init____mutmut_6': xǁSessionErrorǁ__init____mutmut_6, 
        'xǁSessionErrorǁ__init____mutmut_7': xǁSessionErrorǁ__init____mutmut_7, 
        'xǁSessionErrorǁ__init____mutmut_8': xǁSessionErrorǁ__init____mutmut_8, 
        'xǁSessionErrorǁ__init____mutmut_9': xǁSessionErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSessionErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSessionErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSessionErrorǁ__init____mutmut_orig)
    xǁSessionErrorǁ__init____mutmut_orig.__name__ = 'xǁSessionErrorǁ__init__'


class SessionExpiredError(SessionError):
    """Session has expired."""
    
    def xǁSessionExpiredErrorǁ__init____mutmut_orig(self, message: str = "Session expired"):
        super().__init__(message, "session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_1(self, message: str = "XXSession expiredXX"):
        super().__init__(message, "session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_2(self, message: str = "session expired"):
        super().__init__(message, "session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_3(self, message: str = "SESSION EXPIRED"):
        super().__init__(message, "session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_4(self, message: str = "Session expired"):
        super().__init__(None, "session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_5(self, message: str = "Session expired"):
        super().__init__(message, None)
    
    def xǁSessionExpiredErrorǁ__init____mutmut_6(self, message: str = "Session expired"):
        super().__init__("session_expired")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_7(self, message: str = "Session expired"):
        super().__init__(message, )
    
    def xǁSessionExpiredErrorǁ__init____mutmut_8(self, message: str = "Session expired"):
        super().__init__(message, "XXsession_expiredXX")
    
    def xǁSessionExpiredErrorǁ__init____mutmut_9(self, message: str = "Session expired"):
        super().__init__(message, "SESSION_EXPIRED")
    
    xǁSessionExpiredErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSessionExpiredErrorǁ__init____mutmut_1': xǁSessionExpiredErrorǁ__init____mutmut_1, 
        'xǁSessionExpiredErrorǁ__init____mutmut_2': xǁSessionExpiredErrorǁ__init____mutmut_2, 
        'xǁSessionExpiredErrorǁ__init____mutmut_3': xǁSessionExpiredErrorǁ__init____mutmut_3, 
        'xǁSessionExpiredErrorǁ__init____mutmut_4': xǁSessionExpiredErrorǁ__init____mutmut_4, 
        'xǁSessionExpiredErrorǁ__init____mutmut_5': xǁSessionExpiredErrorǁ__init____mutmut_5, 
        'xǁSessionExpiredErrorǁ__init____mutmut_6': xǁSessionExpiredErrorǁ__init____mutmut_6, 
        'xǁSessionExpiredErrorǁ__init____mutmut_7': xǁSessionExpiredErrorǁ__init____mutmut_7, 
        'xǁSessionExpiredErrorǁ__init____mutmut_8': xǁSessionExpiredErrorǁ__init____mutmut_8, 
        'xǁSessionExpiredErrorǁ__init____mutmut_9': xǁSessionExpiredErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSessionExpiredErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSessionExpiredErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSessionExpiredErrorǁ__init____mutmut_orig)
    xǁSessionExpiredErrorǁ__init____mutmut_orig.__name__ = 'xǁSessionExpiredErrorǁ__init__'


class SessionNotFoundError(SessionError):
    """Session not found."""
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_orig(self, message: str = "Session not found"):
        super().__init__(message, "session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_1(self, message: str = "XXSession not foundXX"):
        super().__init__(message, "session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_2(self, message: str = "session not found"):
        super().__init__(message, "session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_3(self, message: str = "SESSION NOT FOUND"):
        super().__init__(message, "session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_4(self, message: str = "Session not found"):
        super().__init__(None, "session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_5(self, message: str = "Session not found"):
        super().__init__(message, None)
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_6(self, message: str = "Session not found"):
        super().__init__("session_not_found")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_7(self, message: str = "Session not found"):
        super().__init__(message, )
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_8(self, message: str = "Session not found"):
        super().__init__(message, "XXsession_not_foundXX")
    
    def xǁSessionNotFoundErrorǁ__init____mutmut_9(self, message: str = "Session not found"):
        super().__init__(message, "SESSION_NOT_FOUND")
    
    xǁSessionNotFoundErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSessionNotFoundErrorǁ__init____mutmut_1': xǁSessionNotFoundErrorǁ__init____mutmut_1, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_2': xǁSessionNotFoundErrorǁ__init____mutmut_2, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_3': xǁSessionNotFoundErrorǁ__init____mutmut_3, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_4': xǁSessionNotFoundErrorǁ__init____mutmut_4, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_5': xǁSessionNotFoundErrorǁ__init____mutmut_5, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_6': xǁSessionNotFoundErrorǁ__init____mutmut_6, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_7': xǁSessionNotFoundErrorǁ__init____mutmut_7, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_8': xǁSessionNotFoundErrorǁ__init____mutmut_8, 
        'xǁSessionNotFoundErrorǁ__init____mutmut_9': xǁSessionNotFoundErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSessionNotFoundErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSessionNotFoundErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSessionNotFoundErrorǁ__init____mutmut_orig)
    xǁSessionNotFoundErrorǁ__init____mutmut_orig.__name__ = 'xǁSessionNotFoundErrorǁ__init__'

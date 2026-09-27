# Source Generated with Decompyle++
# File: ssl.pyc (Python 3.14)

__doc__ = 'This module provides some more Pythonic support for SSL.\n\nObject types:\n\n  SSLSocket -- subtype of socket.socket which does SSL over the socket\n\nExceptions:\n\n  SSLError -- exception raised for I/O errors\n\nFunctions:\n\n  cert_time_to_seconds -- convert time string used for certificate\n                          notBefore and notAfter functions to integer\n                          seconds past the Epoch (the time values\n                          returned from time.time())\n\n  get_server_certificate (addr, ssl_version, ca_certs, timeout) -- Retrieve the\n                          certificate from the server at the specified\n                          address and return it as a PEM-encoded string\n\n\nInteger constants:\n\nSSL_ERROR_ZERO_RETURN\nSSL_ERROR_WANT_READ\nSSL_ERROR_WANT_WRITE\nSSL_ERROR_WANT_X509_LOOKUP\nSSL_ERROR_SYSCALL\nSSL_ERROR_SSL\nSSL_ERROR_WANT_CONNECT\n\nSSL_ERROR_EOF\nSSL_ERROR_INVALID_ERROR_CODE\n\nThe following group define certificate requirements that one side is\nallowing/requiring from the other side:\n\nCERT_NONE - no certificates from the other side are required (or will\n            be looked at if provided)\nCERT_OPTIONAL - certificates are not required, but if provided will be\n                validated, and if validation fails, the connection will\n                also fail\nCERT_REQUIRED - certificates are required, and will be validated, and\n                if validation fails, the connection will also fail\n\nThe following constants identify various SSL protocol variants:\n\nPROTOCOL_SSLv2\nPROTOCOL_SSLv3\nPROTOCOL_SSLv23\nPROTOCOL_TLS\nPROTOCOL_TLS_CLIENT\nPROTOCOL_TLS_SERVER\nPROTOCOL_TLSv1\nPROTOCOL_TLSv1_1\nPROTOCOL_TLSv1_2\n\nThe following constants identify various SSL alert message descriptions as per\nhttp://www.iana.org/assignments/tls-parameters/tls-parameters.xml#tls-parameters-6\n\nALERT_DESCRIPTION_CLOSE_NOTIFY\nALERT_DESCRIPTION_UNEXPECTED_MESSAGE\nALERT_DESCRIPTION_BAD_RECORD_MAC\nALERT_DESCRIPTION_RECORD_OVERFLOW\nALERT_DESCRIPTION_DECOMPRESSION_FAILURE\nALERT_DESCRIPTION_HANDSHAKE_FAILURE\nALERT_DESCRIPTION_BAD_CERTIFICATE\nALERT_DESCRIPTION_UNSUPPORTED_CERTIFICATE\nALERT_DESCRIPTION_CERTIFICATE_REVOKED\nALERT_DESCRIPTION_CERTIFICATE_EXPIRED\nALERT_DESCRIPTION_CERTIFICATE_UNKNOWN\nALERT_DESCRIPTION_ILLEGAL_PARAMETER\nALERT_DESCRIPTION_UNKNOWN_CA\nALERT_DESCRIPTION_ACCESS_DENIED\nALERT_DESCRIPTION_DECODE_ERROR\nALERT_DESCRIPTION_DECRYPT_ERROR\nALERT_DESCRIPTION_PROTOCOL_VERSION\nALERT_DESCRIPTION_INSUFFICIENT_SECURITY\nALERT_DESCRIPTION_INTERNAL_ERROR\nALERT_DESCRIPTION_USER_CANCELLED\nALERT_DESCRIPTION_NO_RENEGOTIATION\nALERT_DESCRIPTION_UNSUPPORTED_EXTENSION\nALERT_DESCRIPTION_CERTIFICATE_UNOBTAINABLE\nALERT_DESCRIPTION_UNRECOGNIZED_NAME\nALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE\nALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE\nALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY\n'
import sys
import os
from collections import namedtuple
from enum import Enum as _Enum, IntEnum as _IntEnum, IntFlag as _IntFlag
from enum import _simple_enum
import _ssl
from _ssl import OPENSSL_VERSION_NUMBER, OPENSSL_VERSION_INFO, OPENSSL_VERSION
from _ssl import _SSLContext, MemoryBIO, SSLSession
from _ssl import SSLError, SSLZeroReturnError, SSLWantReadError, SSLWantWriteError, SSLSyscallError, SSLEOFError, SSLCertVerificationError
from _ssl import txt2obj as _txt2obj, nid2obj as _nid2obj
from _ssl import RAND_status, RAND_add, RAND_bytes

try:
    from _ssl import RAND_egd
except ImportError:
    pass

from _ssl import HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN, HAS_SSLv2, HAS_SSLv3, HAS_TLSv1, HAS_TLSv1_1, HAS_TLSv1_2, HAS_TLSv1_3, HAS_PSK, HAS_PHA
from _ssl import _DEFAULT_CIPHERS, _OPENSSL_API_VERSION
_IntEnum._convert_('_SSLMethod', __name__, (lambda name: name.startswith('PROTOCOL_') and name != 'PROTOCOL_SSLv23'), source = _ssl)
_IntFlag._convert_('Options', __name__, (lambda name: name.startswith('OP_')), source = _ssl)
_IntEnum._convert_('AlertDescription', __name__, (lambda name: name.startswith('ALERT_DESCRIPTION_')), source = _ssl)
_IntEnum._convert_('SSLErrorNumber', __name__, (lambda name: name.startswith('SSL_ERROR_')), source = _ssl)
_IntFlag._convert_('VerifyFlags', __name__, (lambda name: name.startswith('VERIFY_')), source = _ssl)
_IntEnum._convert_('VerifyMode', __name__, (lambda name: name.startswith('CERT_')), source = _ssl)
PROTOCOL_SSLv23 = _SSLMethod.PROTOCOL_TLS
_SSLMethod.PROTOCOL_SSLv23 = _SSLMethod.PROTOCOL_TLS
_PROTOCOL_NAMES = None
_SSLv2_IF_EXISTS = getattr(_SSLMethod, 'PROTOCOL_SSLv2', None)
TLSVersion = <NODE:12>()
_TLSContentType = <NODE:12>()
_TLSAlertType = <NODE:12>()
_TLSMessageType = <NODE:12>()
if sys.platform == 'win32':
    pass
from socket import socket, SOCK_STREAM, create_connection
from socket import SOL_SOCKET, SO_TYPE, _GLOBAL_DEFAULT_TIMEOUT

def _ASN1Object():
    '''_ASN1Object'''
    __doc__ = 'ASN.1 object identifier lookup\n    '
    __slots__ = ()
    
    def __new__(cls, oid):
        # unsupported opcode LOAD_SUPER_ATTR
        # unsupported CALL_INTRINSIC_1 6
        return cls()
    # WARNING: Decompyle incomplete

    fromnid = (lambda cls, nid: # unsupported opcode LOAD_SUPER_ATTR# unsupported CALL_INTRINSIC_1 6cls()# WARNING: Decompyle incomplete
)()
    fromname = (lambda cls, name: # unsupported opcode LOAD_SUPER_ATTR# unsupported CALL_INTRINSIC_1 6cls()# WARNING: Decompyle incomplete
)()

SSLContext.sslsocket_class = SSLSocket
SSLContext.sslobject_class = SSLObject
return None
# WARNING: Decompyle incomplete

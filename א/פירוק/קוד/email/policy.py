# Source Generated with Decompyle++
# File: policy.pyc (Python 3.14)

'''This will be the home for the policy that hooks in the new
code that adds all the email6 features.
'''
import re
import sys
from email._policybase import Compat32, Policy, _extend_docstrings, compat32, validate_header_name
from email.utils import _has_surrogates
from email.headerregistry import HeaderRegistry
from email.contentmanager import raw_data_manager
from email.message import EmailMessage
__all__ = [
    'Compat32',
    'compat32',
    'Policy',
    'EmailPolicy',
    'default',
    'strict',
    'SMTP',
    'HTTP']
linesep_splitter = re.compile('\\n|\\r\\n?')
EmailPolicy = <NODE:12>()
default = EmailPolicy()
del default.header_factory
strict = default.clone(raise_on_defect = True)
SMTP = default.clone(linesep = '\r\n')
HTTP = default.clone(linesep = '\r\n', max_line_length = None)
SMTPUTF8 = SMTP.clone(utf8 = True)

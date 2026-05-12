"""
Privacy and Security Module for AMS JobAssist.

Enforces zero-network access, PII filtering, and DSGVO compliance.

Components:
- network_block: Prevents all external network access
- logging_rules: Filters sensitive data from logs
- data_deletion: Hard delete for user data
- compliance: DSGVO compliance verification

Philosophy: Privacy-first by default. All data stays on the machine.
"""

from .network_block import NetworkBlocker
from .logging_rules import PrivacyFilter
from .data_deletion import DataDeletion
from .compliance import ComplianceChecker

__all__ = ['NetworkBlocker', 'PrivacyFilter', 'DataDeletion', 'ComplianceChecker']

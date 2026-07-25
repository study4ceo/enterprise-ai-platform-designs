"""Router protocol adapters for device discovery."""

from app.adapters.arp_scanner import ARPScanner
from app.adapters.base import BaseAdapter, ConnectionTestResult, DeviceConnection
from app.adapters.http_adapter import HTTPAPIAdapter
from app.adapters.snmp_adapter import SNMPAdapter
from app.adapters.ssh_adapter import SSHAdapter

__all__ = [
    "BaseAdapter",
    "DeviceConnection",
    "ConnectionTestResult",
    "SNMPAdapter",
    "SSHAdapter",
    "HTTPAPIAdapter",
    "ARPScanner",
]

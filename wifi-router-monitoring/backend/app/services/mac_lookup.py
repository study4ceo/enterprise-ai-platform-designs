"""MAC vendor lookup service for device identification."""

from typing import Optional

from manuf import manuf


class MACVendorLookup:
    """
    Service for looking up device manufacturers from MAC addresses.
    
    Uses the Wireshark OUI database via the 'manuf' library.
    Implements caching to reduce repeated lookups.
    """
    
    def __init__(self):
        """Initialize MAC vendor lookup service."""
        self._parser = manuf.MacParser(update=True)
        self._cache: dict[str, Optional[str]] = {}
    
    def get_vendor(self, mac_address: str) -> Optional[str]:
        """
        Get vendor name for a MAC address.
        
        Args:
            mac_address: MAC address in any standard format
        
        Returns:
            Vendor name or None if not found
        
        Example:
            >>> lookup = MACVendorLookup()
            >>> lookup.get_vendor("00:50:56:C0:00:08")
            'VMware, Inc.'
        """
        # Normalize MAC address
        normalized_mac = self._normalize_mac(mac_address)
        
        # Check cache first
        if normalized_mac in self._cache:
            return self._cache[normalized_mac]
        
        # Look up vendor
        try:
            vendor = self._parser.get_manuf(normalized_mac)
            
            # Handle long vendor names
            if vendor and len(vendor) > 255:
                vendor = vendor[:252] + "..."
            
            # Cache result
            self._cache[normalized_mac] = vendor
            
            return vendor
        except Exception:
            # Return None if lookup fails
            self._cache[normalized_mac] = None
            return None
    
    def get_vendor_long(self, mac_address: str) -> Optional[str]:
        """
        Get full vendor name (long form) for a MAC address.
        
        Args:
            mac_address: MAC address in any standard format
        
        Returns:
            Full vendor name or None if not found
        """
        normalized_mac = self._normalize_mac(mac_address)
        
        try:
            vendor = self._parser.get_manuf_long(normalized_mac)
            return vendor
        except Exception:
            return None
    
    def get_comment(self, mac_address: str) -> Optional[str]:
        """
        Get vendor comment for a MAC address.
        
        Args:
            mac_address: MAC address in any standard format
        
        Returns:
            Vendor comment or None if not found
        """
        normalized_mac = self._normalize_mac(mac_address)
        
        try:
            comment = self._parser.get_comment(normalized_mac)
            return comment
        except Exception:
            return None
    
    def clear_cache(self) -> None:
        """Clear the vendor cache."""
        self._cache.clear()
    
    def _normalize_mac(self, mac_address: str) -> str:
        """
        Normalize MAC address to standard format (XX:XX:XX:XX:XX:XX).
        
        Args:
            mac_address: MAC address in various formats
        
        Returns:
            Normalized MAC address
        """
        # Remove common separators and convert to uppercase
        mac = mac_address.replace(":", "").replace("-", "").replace(".", "").upper()
        
        # Insert colons every 2 characters
        if len(mac) == 12:
            return ":".join(mac[i:i+2] for i in range(0, 12, 2))
        
        return mac_address
    
    def update_database(self) -> bool:
        """
        Update the OUI database from Wireshark.
        
        Returns:
            True if update successful, False otherwise
        """
        try:
            self._parser = manuf.MacParser(update=True)
            self.clear_cache()
            return True
        except Exception:
            return False

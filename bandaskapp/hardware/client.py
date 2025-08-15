import requests
import logging
import time
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class EVOKClient:
    """Client for communicating with EVOK API (Unipi1.1 interface)"""
    
    def __init__(self, base_url: str = None):
        # Use configuration from settings if no URL provided
        if base_url is None:
            base_url = settings.BANDASKAPP_CONFIG['EVOK_BASE_URL']
            
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 5
        self.last_error = None
        
        # Set headers for EVOK API
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        logger.info(f"EVOK Client initialized with base URL: {self.base_url}")
    
    def get_temperature(self, circuit_id: str) -> Optional[Dict[str, Any]]:
        """
        Read temperature from a sensor
        
        Args:
            circuit_id: EVOK circuit ID for the temperature sensor
            
        Returns:
            Dictionary with temperature data or None on error
        """
        try:
            url = f"{self.base_url}/json/temp/{circuit_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            self.last_error = None
            
            logger.debug(f"Temperature reading for {circuit_id}: {data.get('value')}°C")
            return data
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout reading temperature sensor {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error reading temperature sensor {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error reading temperature sensor {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error reading temperature sensor {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
    
    def get_relay_state(self, circuit_id: str) -> Optional[Dict[str, Any]]:
        """
        Read relay state
        
        Args:
            circuit_id: EVOK circuit ID for the relay
            
        Returns:
            Dictionary with relay state or None on error
        """
        try:
            url = f"{self.base_url}/json/ro/{circuit_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            self.last_error = None
            
            logger.debug(f"Relay state for {circuit_id}: {data.get('value')}")
            return data
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout reading relay {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error reading relay {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error reading relay {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error reading relay {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
    
    def set_relay_state(self, circuit_id: str, value: bool) -> Optional[Dict[str, Any]]:
        """
        Set relay state
        
        Args:
            circuit_id: EVOK circuit ID for the relay
            value: True for ON, False for OFF
            
        Returns:
            Dictionary with result or None on error
        """
        try:
            url = f"{self.base_url}/json/ro/{circuit_id}"
            payload = {"value": int(value)}
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            self.last_error = None
            
            if data.get('success'):
                state = "ON" if value else "OFF"
                logger.info(f"Relay {circuit_id} set to {state}")
            else:
                logger.error(f"Failed to set relay {circuit_id}: {data}")
            
            return data
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout setting relay {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error setting relay {circuit_id}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error setting relay {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error setting relay {circuit_id}: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return None
    
    def test_connection(self) -> bool:
        """
        Test connection to EVOK API
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get a simple endpoint
            url = f"{self.base_url}/json/ro/1_01"  # Test with furnace relay
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            self.last_error = None
            logger.info("EVOK API connection test successful")
            return True
            
        except Exception as e:
            error_msg = f"EVOK API connection test failed: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            return False
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error


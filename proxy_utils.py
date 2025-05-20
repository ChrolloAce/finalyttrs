import requests
import random
import time
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self, max_retries: int = 5, refresh_interval: int = 3600):
        """
        Initialize the proxy manager.
        
        Args:
            max_retries: Maximum number of proxies to try before giving up
            refresh_interval: Time in seconds before refreshing the proxy list
        """
        self.proxies = []
        self.last_refresh = 0
        self.max_retries = max_retries
        self.refresh_interval = refresh_interval
        self.current_index = 0
        self.used_proxies = set()
        self.refresh_proxies()
    
    def refresh_proxies(self) -> None:
        """Refresh the list of proxies from ProxyScrape API."""
        try:
            # Use a higher timeout for more reliable proxies
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=elite"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Split the response by newlines to get individual proxies
                proxy_list = response.text.strip().split('\n')
                
                # Format proxies for use with requests
                self.proxies = [f"http://{proxy.strip()}" for proxy in proxy_list if proxy.strip()]
                self.used_proxies = set()
                self.current_index = 0
                self.last_refresh = time.time()
                
                logger.info(f"Successfully refreshed proxies. Total proxies: {len(self.proxies)}")
            else:
                logger.error(f"Failed to refresh proxies. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error refreshing proxies: {str(e)}")
            # If we couldn't get new proxies, keep using the existing ones
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the next proxy in rotation.
        
        Returns:
            A proxy dictionary for requests, or None if no proxies are available
        """
        # Check if we need to refresh proxies
        if time.time() - self.last_refresh > self.refresh_interval:
            self.refresh_proxies()
        
        # If no proxies available, return None
        if not self.proxies:
            return None
        
        # Get next proxy
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return {"http": proxy, "https": proxy}
    
    def execute_with_proxy_rotation(self, func, *args, **kwargs) -> Tuple[any, Optional[str]]:
        """
        Execute a function with proxy rotation, trying different proxies until one works.
        
        Args:
            func: The function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Tuple of (result, used_proxy) where used_proxy is the proxy that worked
        """
        errors = []
        
        # Try without proxy first (direct connection)
        try:
            logger.info("Trying direct connection first...")
            result = func(*args, **kwargs)
            logger.info("Direct connection successful")
            return result, None
        except Exception as e:
            error_msg = str(e)
            errors.append(f"Direct connection failed: {error_msg}")
            logger.warning(f"Direct connection failed: {error_msg}")
        
        # Then try with proxies
        retries = 0
        while retries < self.max_retries:
            proxy = self.get_proxy()
            
            if not proxy:
                logger.error("No proxies available")
                break
            
            proxy_str = proxy.get("http", "unknown")
            
            # Skip already used proxies in this session
            if proxy_str in self.used_proxies:
                continue
                
            try:
                logger.info(f"Trying with proxy: {proxy_str}")
                # Add proxy to the kwargs
                kwargs['proxy'] = proxy
                result = func(*args, **kwargs)
                
                # If we got here, the proxy worked - add it to used proxies
                self.used_proxies.add(proxy_str)
                logger.info(f"Request successful with proxy: {proxy_str}")
                return result, proxy_str
            except Exception as e:
                error_msg = str(e)
                errors.append(f"Proxy {proxy_str} failed: {error_msg}")
                logger.warning(f"Proxy {proxy_str} failed: {error_msg}")
                retries += 1
        
        # If we get here, all proxies failed
        all_errors = "\n".join(errors)
        logger.error(f"All proxies failed. Errors:\n{all_errors}")
        raise Exception(f"All proxies failed after {retries} attempts. Last error: {errors[-1] if errors else 'No error recorded'}")


# Create a global proxy manager instance
proxy_manager = ProxyManager(max_retries=10) 
import requests
import concurrent.futures
import time
from bs4 import BeautifulSoup
import json
import os

def fetch_free_proxies():
    """Fetch free proxies from multiple sources"""
    proxies = []
    
    # Source 1: free-proxy-list.net
    try:
        response = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='proxylisttable')
        
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) >= 7:
                ip = columns[0].text.strip()
                port = columns[1].text.strip()
                https = columns[6].text.strip()
                
                if https == 'yes':  # Only get HTTPS proxies
                    proxies.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"Error fetching from free-proxy-list.net: {e}")
    
    # Source 2: geonode
    try:
        response = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc')
        data = response.json()
        
        for proxy in data.get('data', []):
            ip = proxy.get('ip')
            port = proxy.get('port')
            if ip and port:
                proxies.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"Error fetching from geonode: {e}")
    
    return list(set(proxies))  # Remove duplicates

def test_proxy(proxy):
    """Test if a proxy works with YouTube"""
    try:
        proxies = {
            'http': proxy,
            'https': proxy.replace('http://', 'https://') if proxy.startswith('http://') else proxy
        }
        
        # First test with a quick timeout to filter out very slow proxies
        response = requests.get('https://www.youtube.com', 
                                proxies=proxies, 
                                timeout=5)
        
        if response.status_code == 200:
            # Test with youtube-transcript-api specific endpoint
            response = requests.get('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 
                                    proxies=proxies, 
                                    timeout=10)
            
            return proxy if response.status_code == 200 else None
    except Exception:
        pass
    
    return None

def find_working_proxies(proxy_list, max_workers=10):
    """Test proxies in parallel and return working ones"""
    working_proxies = []
    total = len(proxy_list)
    
    print(f"Testing {total} proxies...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxy_list}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_proxy)):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result:
                    print(f"✅ Working proxy found: {proxy}")
                    working_proxies.append(proxy)
                else:
                    print(f"❌ Failed proxy: {proxy}")
            except Exception as e:
                print(f"❌ Error testing {proxy}: {e}")
            
            # Print progress
            if (i + 1) % 10 == 0 or (i + 1) == total:
                print(f"Progress: {i + 1}/{total} ({(i + 1) / total * 100:.1f}%)")
    
    return working_proxies

def save_proxies(proxies, filename='working_proxies.json'):
    """Save working proxies to a file"""
    with open(filename, 'w') as f:
        json.dump(proxies, f, indent=2)
    print(f"Saved {len(proxies)} working proxies to {filename}")

def update_env_file(proxies):
    """Update .env file with working proxies"""
    proxy_list = ','.join(proxies)
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Look for PROXY_LIST in .env
        proxy_line_found = False
        for i, line in enumerate(lines):
            if line.startswith('PROXY_LIST='):
                lines[i] = f'PROXY_LIST={proxy_list}\n'
                proxy_line_found = True
                break
        
        # If not found, add it
        if not proxy_line_found:
            lines.append(f'PROXY_LIST={proxy_list}\n')
        
        with open('.env', 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open('.env', 'w') as f:
            f.write(f'PROXY_LIST={proxy_list}\n')
    
    print(f"Updated .env file with {len(proxies)} proxies")

if __name__ == "__main__":
    start_time = time.time()
    
    # Get free proxies
    print("Fetching proxy lists...")
    proxies = fetch_free_proxies()
    print(f"Found {len(proxies)} proxies to test")
    
    # Test proxies
    working_proxies = find_working_proxies(proxies)
    print(f"\nFound {len(working_proxies)} working proxies out of {len(proxies)} tested")
    
    # Save to file and update .env
    if working_proxies:
        save_proxies(working_proxies)
        update_env_file(working_proxies)
    
    elapsed_time = time.time() - start_time
    print(f"Total time: {elapsed_time:.1f} seconds") 
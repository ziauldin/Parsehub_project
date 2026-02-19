"""
ParseHub Project Fetcher with Pagination
Handles fetching all projects from ParseHub API with automatic pagination
"""

import requests
import logging
from typing import List, Dict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

logger = logging.getLogger(__name__)

# ParseHub API configuration
PARSEHUB_BASE_URL = "https://www.parsehub.com/api/v2/projects"
REQUEST_TIMEOUT = 10  # seconds per request

# Cache configuration
CACHE_TTL = 300  # 5 minutes in seconds
_projects_cache = None
_cache_timestamp = None
_cache_lock = None  # Prevent multiple simultaneous fetches

def _is_cache_valid():
    """Check if cache exists and is still valid"""
    global _projects_cache, _cache_timestamp
    if _projects_cache is None or _cache_timestamp is None:
        return False
    elapsed = time.time() - _cache_timestamp
    is_valid = elapsed < CACHE_TTL
    if is_valid:
        logger.info(f"[CACHE] Cache is valid (age: {elapsed:.1f}s)")
    else:
        logger.info(f"[CACHE] Cache expired (age: {elapsed:.1f}s > TTL: {CACHE_TTL}s)")
    return is_valid

def get_all_projects_with_cache(api_key: str) -> List[Dict]:
    """
    Get all projects with caching - returns cached data if available
    
    Args:
        api_key: ParseHub API key
        
    Returns:
        List of all project dictionaries (from cache or fresh fetch)
    """
    global _projects_cache, _cache_timestamp
    
    # Return cached data if valid
    if _is_cache_valid() and _projects_cache is not None:
        logger.info(f"[CACHE] Returning {len(_projects_cache)} cached projects")
        return _projects_cache
    
    # Fetch fresh data
    logger.info("[CACHE] Cache miss or expired - fetching from ParseHub API...")
    projects = fetch_all_projects(api_key)
    
    # Store in cache
    _projects_cache = projects
    _cache_timestamp = time.time()
    logger.info(f"[CACHE] Cached {len(projects)} projects (expires in {CACHE_TTL}s)")
    
    return projects


def create_session_with_retries():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_all_projects(api_key: str) -> List[Dict]:
    """
    Fetch ALL projects from ParseHub API with pagination
    
    ParseHub returns projects in pages of 20. This function handles pagination
    to fetch all available projects by making multiple requests with different offsets.
    
    Args:
        api_key: ParseHub API key
        
    Returns:
        List of all project dictionaries
        
    Raises:
        Exception: If API key is invalid or request fails
    """
    if not api_key or not api_key.strip():
        logger.error("[FETCH] Invalid API key provided")
        raise ValueError("API key cannot be empty")
    
    try:
        logger.info(f"[FETCH] Making initial API call to get total project count...")
        
        # First request to get total count
        response = requests.get(
            PARSEHUB_BASE_URL,
            params={"api_key": api_key, "offset": 0},
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        data = response.json()
        
        total_projects = data.get("total_projects", 0)
        projects = data.get("projects", [])
        
        logger.info(f"[FETCH] Total projects available: {total_projects}")
        logger.info(f"[FETCH] First page: {len(projects)} projects")
        
        # If there are more projects, fetch them with pagination
        if total_projects > 20:
            logger.info(f"[FETCH] Pagination needed - fetching remaining {total_projects - 20} projects...")
            
            # Calculate number of pages needed (20 projects per page)
            pages_needed = (total_projects + 19) // 20  # Ceiling division
            
            for page in range(1, pages_needed):
                offset = page * 20
                logger.info(f"[FETCH] Fetching page {page + 1}/{pages_needed} (offset={offset})...")
                
                page_response = requests.get(
                    PARSEHUB_BASE_URL,
                    params={"api_key": api_key, "offset": offset},
                    timeout=REQUEST_TIMEOUT
                )
                
                page_response.raise_for_status()
                page_data = page_response.json()
                page_projects = page_data.get("projects", [])
                projects.extend(page_projects)
                logger.info(f"[FETCH] Page {page + 1} retrieved: {len(page_projects)} projects (total so far: {len(projects)})")
        
        logger.info(f"[FETCH] ✅ Successfully fetched all {len(projects)} projects from {total_projects} total")
        return projects
            
    except requests.Timeout:
        logger.error(f"[FETCH] Request timeout")
        raise Exception("ParseHub API request timeout")
    except requests.RequestException as e:
        logger.error(f"[FETCH] Request error: {str(e)}")
        if "401" in str(e) or "Unauthorized" in str(e):
            logger.error("[FETCH] ❌ Invalid API key or unauthorized access")
            raise ValueError("Invalid API key or unauthorized access")
        raise Exception(f"Failed to fetch projects: {str(e)}")
    except ValueError as e:
        logger.error(f"[FETCH] JSON decode error: {str(e)}")
        raise Exception(f"Invalid response format from ParseHub: {str(e)}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        try:
            projects = fetch_all_projects(api_key)
            print(f"\n✅ Successfully fetched {len(projects)} projects")
            for i, proj in enumerate(projects[:5], 1):
                print(f"  {i}. {proj.get('name', 'Unknown')}")
            if len(projects) > 5:
                print(f"  ... and {len(projects) - 5} more")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    else:
        print("Usage: python fetch_projects.py <api_key>")
        sys.exit(1)

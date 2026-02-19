"""
Flask API Server for ParseHub Real-Time Monitoring
Exposes REST endpoints for the Next.js frontend to control and monitor real-time data collection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from typing import Optional, Dict, List
import json
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Dynamic import handling - works from both root and backend directories
import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import local services
try:
    from backend.database import ParseHubDatabase
    from backend.monitoring_service import MonitoringService
    from backend.analytics_service import AnalyticsService
    from backend.excel_import_service import ExcelImportService
    from backend.auto_runner_service import AutoRunnerService
    from backend.fetch_projects import fetch_all_projects, get_all_projects_with_cache
except ImportError:
    # Fallback for when running from backend directory
    from database import ParseHubDatabase
    from monitoring_service import MonitoringService
    from analytics_service import AnalyticsService
    from excel_import_service import ExcelImportService
    from auto_runner_service import AutoRunnerService
    from fetch_projects import fetch_all_projects, get_all_projects_with_cache

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
db = ParseHubDatabase()
monitoring_service = MonitoringService()
analytics_service = AnalyticsService()
excel_import_service = ExcelImportService(db)
auto_runner_service = AutoRunnerService()

# API Key validation
BACKEND_API_KEY = os.getenv('BACKEND_API_KEY', 't_hmXetfMCq3')

def validate_api_key(request_obj):
    """Validate API key from Authorization header"""
    auth_header = request_obj.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.replace('Bearer ', '')
    return token == BACKEND_API_KEY

# ========== MONITORING ENDPOINTS ==========

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """
    Start real-time monitoring of a ParseHub run
    
    Request body:
    {
        "run_token": "...",
        "pages": 1,
        "project_id": 1 (optional)
    }
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        run_token = data.get('run_token')
        pages = data.get('pages', 1)
        project_id = data.get('project_id')
        
        if not run_token:
            return jsonify({'error': 'Missing required field: run_token'}), 400
        
        # If project_id not provided, infer from run token in active runs
        if not project_id:
            try:
                with open('../active_runs.json', 'r') as f:
                    active_runs = json.load(f)
                    for project in active_runs.get('projects', []):
                        for run in project.get('runs', []):
                            if run.get('run_token') == run_token:
                                project_id = project.get('id')
                                break
            except:
                pass
        
        if not project_id:
            return jsonify({'error': 'Could not determine project_id'}), 400
        
        # Create monitoring session in database
        session_id = db.create_monitoring_session(project_id, run_token, pages)
        
        if not session_id:
            return jsonify({'error': 'Failed to create monitoring session'}), 500
        
        # Start real-time monitoring in background
        # This will run the monitoring loop in the monitoring service
        try:
            monitoring_service.monitor_run_realtime(project_id, run_token, pages)
        except Exception as e:
            logger.error(f'Error starting real-time monitoring: {e}')
            # Still return success since session was created, monitoring will retry
        
        return jsonify({
            'session_id': session_id,
            'run_token': run_token,
            'project_id': project_id,
            'target_pages': pages,
            'status': 'monitoring_started'
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/monitor/start: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """
    Get current monitoring status
    
    Query parameters:
    - session_id: Monitoring session ID (optional)
    - project_id: Project ID (optional)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        session_id = request.args.get('session_id', type=int)
        project_id = request.args.get('project_id', type=int)
        
        if not session_id and not project_id:
            return jsonify({'error': 'Missing required parameter: session_id or project_id'}), 400
        
        # Get session summary
        if session_id:
            summary = db.get_session_summary(session_id)
        else:  # project_id provided
            summary = db.get_monitoring_status_for_project(project_id)
        
        if not summary:
            return jsonify({'error': 'Monitoring session not found'}), 404
        
        return jsonify({
            'success': True,
            'status': summary['status'],
            'session_id': summary.get('session_id'),
            'project_id': summary.get('project_id'),
            'run_token': summary.get('run_token'),
            'target_pages': summary.get('target_pages'),
            'total_pages': summary.get('total_pages'),
            'total_records': summary.get('total_records'),
            'progress_percentage': summary.get('progress_percentage'),
            'current_url': summary.get('current_url'),
            'error_message': summary.get('error_message'),
            'start_time': summary.get('start_time'),
            'end_time': summary.get('end_time'),
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/monitor/status: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/data', methods=['GET'])
def get_monitor_data():
    """
    Get scraped data from a monitoring session
    
    Query parameters:
    - session_id: Monitoring session ID (required)
    - limit: Number of records to fetch (default: 100)
    - offset: Number of records to skip (default: 0)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        session_id = request.args.get('session_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not session_id:
            return jsonify({'error': 'Missing required parameter: session_id'}), 400
        
        # Validate limit and offset
        limit = min(max(limit, 1), 1000)  # Clamp between 1 and 1000
        offset = max(offset, 0)
        
        # Get records from database
        records = db.get_session_records(session_id, limit, offset)
        total = db.get_session_records_count(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'records': records,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total,
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/monitor/data: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/data/csv', methods=['GET'])
def get_monitor_data_csv():
    """
    Export monitoring session data as CSV
    
    Query parameters:
    - session_id: Monitoring session ID (required)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        session_id = request.args.get('session_id', type=int)
        
        if not session_id:
            return jsonify({'error': 'Missing required parameter: session_id'}), 400
        
        # Get CSV data
        csv_data = db.get_data_as_csv(session_id)
        
        if not csv_data:
            return jsonify({'error': 'No records found for session'}), 404
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="session_{session_id}_data.csv"'
        }
    
    except Exception as e:
        logger.error(f'Error in /api/monitor/data/csv: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """
    Stop real-time monitoring of a run
    
    Request body:
    {
        "session_id": 1 (optional),
        "run_token": "..." (optional)
    }
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        run_token = data.get('run_token')
        
        if not session_id and not run_token:
            return jsonify({'error': 'Missing required field: session_id or run_token'}), 400
        
        # Update session status to cancelled
        if session_id:
            db.update_monitoring_session(session_id, status='cancelled')
            summary = db.get_session_summary(session_id)
        else:
            # Find session by run_token (get most recent)
            # This would need a database method to find by run_token
            return jsonify({'error': 'Session ID required for stopping'}), 400
        
        return jsonify({
            'success': True,
            'status': 'cancelled',
            'session_id': session_id,
            'total_records': summary.get('total_records') if summary else 0,
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/monitor/stop: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/runs/<run_token>/cancel', methods=['POST'])
def cancel_run(run_token: str):
    """
    Cancel a running ParseHub job
    
    URL parameter:
    - run_token: The token of the run to cancel
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        api_key = os.getenv('PARSEHUB_API_KEY')
        
        if not api_key:
            logger.error('[API] Missing PARSEHUB_API_KEY for cancel run')
            return jsonify({'error': 'Missing API key configuration'}), 500
        
        if not run_token:
            return jsonify({'error': 'Missing required parameter: run_token'}), 400
        
        logger.info(f'[API] Cancelling run: {run_token}')
        
        # Call ParseHub API to cancel the run
        cancel_url = f'https://www.parsehub.com/api/v2/runs/{run_token}/cancel'
        
        response = requests.post(
            cancel_url,
            data={'api_key': api_key},
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f'[API] ParseHub cancel failed: {response.status_code} - {response.text}')
            return jsonify({
                'error': 'Failed to cancel run',
                'details': response.text
            }), response.status_code
        
        result = response.json()
        
        logger.info(f'[API] Run cancelled successfully: {run_token}')
        
        return jsonify({
            'success': True,
            'message': f'Run {run_token} cancelled successfully',
            'run': result
        }), 200
    
    except requests.exceptions.Timeout:
        logger.error(f'[API] Timeout while cancelling run {run_token}')
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f'[API] Network error cancelling run {run_token}: {e}')
        return jsonify({'error': 'Network error', 'details': str(e)}), 500
    except json.JSONDecodeError:
        logger.error(f'[API] Invalid JSON response from ParseHub')
        return jsonify({'error': 'Invalid response from ParseHub API'}), 500
    except Exception as e:
        logger.error(f'[API] Error cancelling run {run_token}: {e}')
        return jsonify({'error': str(e)}), 500


# ========== METADATA MANAGEMENT ENDPOINTS ==========

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """
    Get metadata records with optional filtering
    
    Query parameters:
    - region: Filter by region
    - country: Filter by country
    - brand: Filter by brand
    - limit: Records per page (default: 100)
    - offset: Pagination offset (default: 0)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        region = request.args.get('region')
        country = request.args.get('country')
        brand = request.args.get('brand')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        records = db.get_metadata_filtered(region, country, brand, limit, offset)
        
        return jsonify({
            'success': True,
            'records': records,
            'count': len(records),
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/metadata: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/<int:metadata_id>', methods=['GET'])
def get_metadata_by_id(metadata_id):
    """Get a specific metadata record"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        record = db.get_metadata_by_id(metadata_id)
        
        if not record:
            return jsonify({'error': 'Metadata not found'}), 404
        
        return jsonify({
            'success': True,
            'record': record
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/metadata/{metadata_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/<int:metadata_id>', methods=['PUT'])
def update_metadata(metadata_id):
    """
    Update metadata record
    
    Request body:
    {
        "current_page_scraped": 5,
        "current_product_scraped": 100,
        "last_known_url": "..."
    }
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        success = db.update_metadata_progress(
            metadata_id,
            current_page_scraped=data.get('current_page_scraped'),
            current_product_scraped=data.get('current_product_scraped'),
            last_known_url=data.get('last_known_url')
        )
        
        if not success:
            return jsonify({'error': 'Failed to update metadata'}), 500
        
        record = db.get_metadata_by_id(metadata_id)
        
        return jsonify({
            'success': True,
            'message': 'Metadata updated',
            'record': record
        }), 200
    
    except Exception as e:
        logger.error(f'Error updating /api/metadata/{metadata_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/<int:metadata_id>', methods=['DELETE'])
def delete_metadata(metadata_id):
    """Delete a metadata record"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        success = db.delete_metadata(metadata_id)
        
        if not success:
            return jsonify({'error': 'Failed to delete metadata'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Metadata {metadata_id} deleted'
        }), 200
    
    except Exception as e:
        logger.error(f'Error deleting /api/metadata/{metadata_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/<int:metadata_id>/completion-status', methods=['GET'])
def get_completion_status(metadata_id):
    """Get completion status for a metadata record"""
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        result = auto_runner_service.check_scraping_completion(metadata_id)
        
        if not result.get('success'):
            return jsonify({'error': result.get('error')}), 400
        
        return jsonify({
            'success': True,
            **result
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/metadata/{metadata_id}/completion-status: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/import', methods=['POST'])
def import_metadata():
    """
    Import metadata from Excel file
    
    Request form data:
    - file: Excel file (multipart/form-data)
    - uploaded_by: Username of uploader (optional)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        uploaded_by = request.form.get('uploaded_by', 'api')
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Only .xlsx and .xls files are supported'}), 400
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Import metadata
            result = excel_import_service.bulk_import_metadata(temp_path, uploaded_by)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return jsonify(result), 200 if result.get('success') else 400
        
        except Exception as e:
            os.remove(temp_path)
            raise e
    
    except Exception as e:
        logger.error(f'Error in /api/metadata/import: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/metadata/import-history', methods=['GET'])
def get_import_history():
    """
    Get import batch history
    
    Query parameters:
    - limit: Records per page (default: 50)
    - offset: Pagination offset (default: 0)
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        batches = db.get_import_batches(limit, offset)
        
        return jsonify({
            'success': True,
            'batches': batches,
            'count': len(batches),
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/metadata/import-history: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/filters/values', methods=['GET'])
def get_filter_values():
    """
    Get distinct values for filter fields
    
    Query parameters:
    - field: 'region', 'country', or 'brand'
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        field = request.args.get('field')
        
        if field not in ['region', 'country', 'brand']:
            return jsonify({'error': 'Invalid field. Must be: region, country, or brand'}), 400
        
        values = db.get_distinct_filter_values(field)
        
        return jsonify({
            'success': True,
            'field': field,
            'values': values,
            'count': len(values)
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/filters/values: {e}')
        return jsonify({'error': str(e)}), 500


# ========== BATCH OPERATIONS ENDPOINTS ==========

@app.route('/api/runs/batch-execute', methods=['POST'])
def batch_execute_runs():
    """
    Execute multiple projects sequentially
    
    Request body:
    {
        "metadata_ids": [1, 2, 3],
        "pages_per_iteration": 5 (optional)
    }
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        metadata_ids = data.get('metadata_ids', [])
        pages_per_run = data.get('pages_per_run', 1)
        
        if not metadata_ids:
            return jsonify({'error': 'Missing required field: metadata_ids'}), 400
        
        run_queue = []
        
        for metadata_id in metadata_ids:
            metadata = db.get_metadata_by_id(metadata_id)
            
            if not metadata:
                logger.warning(f"Metadata {metadata_id} not found, skipping")
                continue
            
            project_token = metadata.get('project_token')
            if not project_token:
                logger.warning(f"Metadata {metadata_id} has no project_token, skipping")
                continue
            
            run_queue.append({
                'metadata_id': metadata_id,
                'project_token': project_token,
                'project_name': metadata.get('project_name'),
                'status': 'queued'
            })
        
        if not run_queue:
            return jsonify({'error': 'No valid projects to execute'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Queued {len(run_queue)} projects for execution',
            'queue_id': datetime.now().isoformat(),
            'run_queue': run_queue
        }), 200
    
    except Exception as e:
        logger.error(f'Error in /api/runs/batch-execute: {e}')
        return jsonify({'error': str(e)}), 500


# ========== PROJECTS ENDPOINTS ==========

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """
    Fetch all projects from ParseHub with automatic pagination
    Returns all available projects, grouped by website domain
    Each project is enriched with metadata from the metadata table
    """
    try:
        api_key = request.args.get('api_key') or os.getenv('PARSEHUB_API_KEY')
        
        if not api_key:
            logger.error('[API] Missing API key for projects fetch')
            return jsonify({'error': 'Missing API key'}), 400
        
        logger.info('[API] Fetching all projects (with cache)...')
        projects = get_all_projects_with_cache(api_key)
        
        logger.info(f'[API] Retrieved {len(projects)} projects from cache/API')
        
        # Enrich projects with metadata in batch (more efficient)
        projects = db.match_projects_to_metadata_batch(projects)
        
        # Count matches
        metadata_matches = sum(1 for p in projects if p.get('metadata'))
        logger.info(f'[API] Matched {metadata_matches}/{len(projects)} projects with metadata')
        
        # Group projects by website domain (extracted from title)
        websites_dict = {}
        for proj in projects:
            title = proj.get('title', 'Unknown')
            website = db.extract_website_from_title(title)
            
            # Initialize website group if needed
            if website not in websites_dict:
                websites_dict[website] = {
                    'website': website,
                    'projects': [],
                    'project_count': 0
                }
            
            # Add project to website group
            websites_dict[website]['projects'].append(proj)
            websites_dict[website]['project_count'] += 1
        
        # Convert to list format
        by_website = list(websites_dict.values())
        
        logger.info(f'[API] Grouped {len(projects)} projects into {len(by_website)} website groups')
        
        response_data = {
            'success': True,
            'total': len(projects),
            'metadata_matches': metadata_matches,
            'by_website': by_website,
            'by_project': projects
        }
        
        logger.info(f'[API] ✅ Returning response with {len(by_website)} website groups and {metadata_matches} enriched projects')
        return jsonify(response_data), 200
        
    except ValueError as e:
        logger.error(f'[API] Validation error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'[API] Error fetching projects: {str(e)}')
        return jsonify({'error': 'Failed to fetch projects'}), 500


@app.route('/api/projects/sync', methods=['POST'])
def sync_projects():
    """
    Sync projects from ParseHub API to database
    Fetches all projects and stores them in the database
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        api_key = request.json.get('api_key') if request.json else None
        api_key = api_key or os.getenv('PARSEHUB_API_KEY')
        
        if not api_key:
            return jsonify({'error': 'Missing API key'}), 400
        
        logger.info('[API] Starting project sync from ParseHub API...')
        
        # Fetch all projects from API
        projects = get_all_projects_with_cache(api_key)
        
        if not projects:
            return jsonify({'error': 'Failed to fetch projects from API'}), 500
        
        # Sync to database
        result = db.sync_projects(projects)
        
        logger.info(f'[API] Project sync complete: {result}')
        
        return jsonify({
            'success': result['success'],
            'message': f"Synced {result.get('total', 0)} projects to database",
            **result
        }), 200
        
    except Exception as e:
        logger.error(f'[API] Error syncing projects: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/search', methods=['GET'])
def search_projects():
    """
    Search projects from database with optional filtering
    Query parameters: region, country, brand, limit, offset, group_by_website
    Returns projects with linked metadata, grouped by website if requested
    """
    try:
        # Get filter parameters
        region = request.args.get('region')
        country = request.args.get('country')
        brand = request.args.get('brand')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        group_by_website = request.args.get('group_by_website', 'true').lower() == 'true'
        
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            limit = 100
        if offset < 0:
            offset = 0
        
        logger.info(f'[API] Searching projects - region:{region}, country:{country}, brand:{brand}, group:{group_by_website}')
        
        # Get projects with filters and website grouping
        result = db.get_projects_with_website_grouping(
            limit=limit,
            offset=offset,
            region=region,
            country=country,
            brand=brand
        )
        
        if group_by_website:
            return jsonify({
                'success': result.get('success', False),
                'projects': result.get('by_website', []),
                'total': result.get('total', 0),
                'grouped_by': 'website',
                'limit': limit,
                'offset': offset
            }), 200 if result.get('success') else 500
        else:
            return jsonify({
                'success': result.get('success', False),
                'projects': result.get('by_project', []),
                'total': result.get('total', 0),
                'grouped_by': 'none',
                'limit': limit,
                'offset': offset
            }), 200 if result.get('success') else 500
        
    except ValueError as e:
        logger.error(f'[API] Invalid parameters: {str(e)}')
        return jsonify({'error': 'Invalid parameters', 'details': str(e)}), 400
    except Exception as e:
        logger.error(f'[API] Error searching projects: {str(e)}')
        return jsonify({'error': 'Failed to search projects', 'details': str(e)}), 500


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """
    Get all available filter options
    Returns regions, countries, brands, and websites
    """
    if not validate_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        logger.info('[API] Getting filter options...')
        
        filters = {
            'regions': db.get_distinct_metadata_values('region'),
            'countries': db.get_distinct_metadata_values('country'),
            'brands': db.get_distinct_metadata_values('brand'),
            'websites': db.get_distinct_project_websites()
        }
        
        logger.info(f'[API] Filters - Regions: {len(filters["regions"])}, Countries: {len(filters["countries"])}, Brands: {len(filters["brands"])}, Websites: {len(filters["websites"])}')
        
        return jsonify({
            'success': True,
            'filters': filters
        }), 200
        
    except Exception as e:
        logger.error(f'[API] Error getting filters: {str(e)}')
        return jsonify({'error': str(e)}), 500


# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {error}')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    from datetime import datetime
    
    port = os.getenv('BACKEND_PORT', 5000)
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f'Starting ParseHub API Server on port {port}')
    app.run(host='0.0.0.0', port=int(port), debug=debug)

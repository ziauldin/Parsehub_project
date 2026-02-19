#!/usr/bin/env python
import sys
sys.path.insert(0, 'backend')

from api_server import app
import os

# Create an alternative simple route for testing
@app.route('/api/projects-sample', methods=['GET'])
def get_projects_sample():
    """
    Get small sample of projects with metadata for testing
    """
    from api_server import get_all_projects_with_cache, db
    from flask import jsonify
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        api_key = os.getenv('PARSEHUB_API_KEY') or 't_hmXetfMCq3'
        logger.info('[API] Fetching sample projects...')
        
        projects = get_all_projects_with_cache(api_key)
        projects = projects[:10]  # Only first 10
        
        logger.info(f'[API] Retrieved {len(projects)} sample projects')
        
        # Batch match to metadata
        projects = db.match_projects_to_metadata_batch(projects)
        metadata_matches = sum(1 for p in projects if p.get('metadata'))
        
        logger.info(f'[API] Matched {metadata_matches} projects with metadata')
        
        return jsonify({
            'success': True,
            'total': len(projects),
            'metadata_matches': metadata_matches,
            'projects': projects
        }), 200
        
    except Exception as e:
        logger.error(f'[API] Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = os.getenv('BACKEND_PORT', 5000)
    print(f'Starting server on port {port}...')
    print('Test endpoint: http://localhost:5000/api/projects-sample')
    try:
        app.run(host='0.0.0.0', port=int(port), debug=False)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

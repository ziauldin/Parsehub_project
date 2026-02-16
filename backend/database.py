import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ParseHubDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'd:\\Parsehub\\parsehub.db')
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def init_db(self):
        """Initialize database schema"""
        conn = self.connect()
        cursor = conn.cursor()

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                owner_email TEXT,
                main_site TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Runs table - tracks each execution
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                run_token TEXT UNIQUE NOT NULL,
                status TEXT,
                pages_scraped INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                records_count INTEGER DEFAULT 0,
                data_file TEXT,
                is_empty BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        # Scraped data table - stores individual records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                data_key TEXT,
                data_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES runs(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        # Key metrics table - for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                date DATE,
                total_pages INTEGER DEFAULT 0,
                total_records INTEGER DEFAULT 0,
                runs_count INTEGER DEFAULT 0,
                avg_duration REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, date),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        conn.commit()
        self.disconnect()

    def add_project(self, token: str, title: str, owner_email: str = None, main_site: str = None):
        """Add or update project"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO projects (token, title, owner_email, main_site, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (token, title, owner_email, main_site))

        conn.commit()
        self.disconnect()

    def add_run(self, project_token: str, run_token: str, status: str, pages: int, 
                start_time: str, end_time: str = None, data_file: str = None, is_empty: bool = False):
        """Add a new run record"""
        conn = self.connect()
        cursor = conn.cursor()

        # Get project ID
        cursor.execute('SELECT id FROM projects WHERE token = ?', (project_token,))
        project = cursor.fetchone()
        
        if not project:
            self.disconnect()
            return None

        project_id = project['id']
        duration = None

        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration = int((end - start).total_seconds())
            except:
                pass

        cursor.execute('''
            INSERT INTO runs 
            (project_id, run_token, status, pages_scraped, start_time, end_time, duration_seconds, data_file, is_empty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, run_token, status, pages, start_time, end_time, duration, data_file, is_empty))

        conn.commit()
        run_id = cursor.lastrowid
        self.disconnect()

        return run_id

    def store_scraped_data(self, run_id: int, project_id: int = None, data: dict | list = None):
        """Store scraped data from JSON"""
        conn = self.connect()
        cursor = conn.cursor()

        # If project_id not provided, get it from run
        if project_id is None:
            cursor.execute('SELECT project_id FROM runs WHERE id = ?', (run_id,))
            run = cursor.fetchone()
            if run:
                project_id = run['project_id']
            else:
                self.disconnect()
                return 0

        records = 0

        if isinstance(data, list):
            # Array of records
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        cursor.execute('''
                            INSERT INTO scraped_data (run_id, project_id, data_key, data_value)
                            VALUES (?, ?, ?, ?)
                        ''', (run_id, project_id, key, str(value)))
                    records += 1
        elif isinstance(data, dict):
            # Check if it contains an array (like { product: [...] })
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    # This is the data array
                    for item in value:
                        for field, field_value in item.items():
                            cursor.execute('''
                                INSERT INTO scraped_data (run_id, project_id, data_key, data_value)
                                VALUES (?, ?, ?, ?)
                            ''', (run_id, project_id, field, str(field_value)))
                        records += 1
                    break

        # Update records count in runs table
        cursor.execute('UPDATE runs SET records_count = ? WHERE id = ?', (records, run_id))

        conn.commit()
        self.disconnect()

        return records

    def get_project_analytics(self, project_token: str) -> dict:
        """Get analytics for a specific project"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM projects WHERE token = ?', (project_token,))
        project = cursor.fetchone()

        if not project:
            self.disconnect()
            return None

        project_id = project['id']

        # Total runs
        cursor.execute('SELECT COUNT(*) as count FROM runs WHERE project_id = ?', (project_id,))
        total_runs = cursor.fetchone()['count']

        # Completed runs
        cursor.execute('SELECT COUNT(*) as count FROM runs WHERE project_id = ? AND status = ?', 
                      (project_id, 'complete'))
        completed_runs = cursor.fetchone()['count']

        # Total records scraped
        cursor.execute('SELECT SUM(records_count) as total FROM runs WHERE project_id = ?', (project_id,))
        total_records = cursor.fetchone()['total'] or 0

        # Average duration
        cursor.execute('''
            SELECT AVG(duration_seconds) as avg_duration FROM runs 
            WHERE project_id = ? AND duration_seconds IS NOT NULL AND status = ?
        ''', (project_id, 'complete'))
        avg_duration = cursor.fetchone()['avg_duration'] or 0

        # Latest run
        cursor.execute('''
            SELECT run_token, status, pages_scraped, start_time, records_count FROM runs 
            WHERE project_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (project_id,))
        latest_run = cursor.fetchone()

        # Pages scraped trend (last 10 runs)
        cursor.execute('''
            SELECT pages_scraped, start_time FROM runs 
            WHERE project_id = ? ORDER BY created_at DESC LIMIT 10
        ''', (project_id,))
        pages_trend = [dict(row) for row in cursor.fetchall()]

        self.disconnect()

        return {
            'project_token': project_token,
            'total_runs': total_runs,
            'completed_runs': completed_runs,
            'total_records': int(total_records),
            'avg_duration': round(avg_duration, 2),
            'latest_run': dict(latest_run) if latest_run else None,
            'pages_trend': pages_trend
        }

    def get_all_analytics(self) -> list:
        """Get analytics for all projects"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT token FROM projects')
        projects = cursor.fetchall()
        self.disconnect()

        analytics = []
        for project in projects:
            analytics.append(self.get_project_analytics(project['token']))

        return analytics

    def import_from_json(self, json_file: str, project_token: str, run_token: str, 
                        status: str, pages: int, start_time: str, end_time: str = None):
        """Import data from JSON file into database"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Ensure project exists
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM projects WHERE token = ?', (project_token,))
            project = cursor.fetchone()
            self.disconnect()

            if not project:
                return None

            project_id = project['id']

            # Add run record
            run_id = self.add_run(
                project_token=project_token,
                run_token=run_token,
                status=status,
                pages=pages,
                start_time=start_time,
                end_time=end_time,
                data_file=json_file,
                is_empty=len(str(data)) < 10
            )

            if run_id:
                # Store the data with proper project_id
                records = self.store_scraped_data(run_id, project_id, data)
                return {'run_id': run_id, 'records': records}
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return None

    def export_data(self, project_token: str, format: str = 'json') -> str | None:
        """Export all project data"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM projects WHERE token = ?', (project_token,))
        project = cursor.fetchone()

        if not project:
            self.disconnect()
            return None

        project_id = project['id']

        cursor.execute('''
            SELECT run_token, status, pages_scraped, start_time, records_count 
            FROM runs WHERE project_id = ? ORDER BY created_at DESC
        ''', (project_id,))
        
        runs = [dict(row) for row in cursor.fetchall()]

        if format == 'json':
            self.disconnect()
            return json.dumps({'runs': runs, 'project_token': project_token}, indent=2)
        
        self.disconnect()
        return None


if __name__ == '__main__':
    db = ParseHubDatabase()
    
    # Test
    db.add_project('test_token', 'Test Project', 'test@example.com', 'https://example.com')
    print("✅ Database initialized successfully!")
    print(f"Database file: {db.db_path}")

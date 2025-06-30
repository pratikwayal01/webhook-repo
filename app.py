from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
from datetime import datetime
import json
import os
from typing import Optional, Dict, Any

app = Flask(__name__)

# Load environment variables from .env file in the root directory
from dotenv import load_dotenv
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming GitHub webhooks"""
    try:
        # Get the event type from headers
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        # Process different event types
        action_data = None
        
        if event_type == 'push':
            action_data = process_push_event(payload)
        elif event_type == 'pull_request':
            action_data = process_pull_request_event(payload)
        elif event_type == 'pull_request' and payload.get('action') == 'closed' and payload.get('pull_request', {}).get('merged'):
            # This is a merge event
            action_data = process_merge_event(payload)
        
        if action_data:
            # Store to Supabase
            result = supabase.table('github_actions').insert(action_data).execute()
            print(f"Stored action with ID: {result.data[0]['id'] if result.data else 'unknown'}")
            return jsonify({'status': 'success', 'data': result.data}), 200
        else:
            return jsonify({'status': 'ignored', 'event': event_type}), 200
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_push_event(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process push events"""
    try:
        author = payload['pusher']['name']
        ref = payload['ref']
        branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else ref
        timestamp = datetime.utcnow().isoformat()
        
        return {
            'action': 'push',
            'author': author,
            'to_branch': branch,
            'from_branch': None,
            'timestamp': timestamp,
            'request_id': payload.get('head_commit', {}).get('id', '')[:8]
        }
    except KeyError as e:
        print(f"Missing key in push payload: {e}")
        return None

def process_pull_request_event(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process pull request events"""
    try:
        action = payload['action']
        
        # Only process 'opened' pull requests
        if action != 'opened':
            return None
            
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow().isoformat()
        
        return {
            'action': 'pull_request',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'request_id': str(payload['pull_request']['number'])
        }
    except KeyError as e:
        print(f"Missing key in pull request payload: {e}")
        return None

def process_merge_event(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process merge events (when a PR is closed and merged)"""
    try:
        pull_request = payload['pull_request']
        
        # Check if it's actually merged
        if not pull_request.get('merged', False):
            return None
            
        author = pull_request['merged_by']['login']
        from_branch = pull_request['head']['ref']
        to_branch = pull_request['base']['ref']
        timestamp = datetime.utcnow().isoformat()
        
        return {
            'action': 'merge',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'request_id': str(pull_request['number'])
        }
    except KeyError as e:
        print(f"Missing key in merge payload: {e}")
        return None

@app.route('/api/actions', methods=['GET'])
def get_actions():
    """API endpoint to get recent actions for the UI"""
    try:
        # Get the latest 50 actions, sorted by timestamp (newest first)
        result = supabase.table('github_actions').select('*').order('timestamp', desc=True).limit(50).execute()
        
        actions = result.data
        
        # Format timestamp for display
        for action in actions:
            action['formatted_timestamp'] = format_timestamp(action['timestamp'])
        
        return jsonify(actions)
    except Exception as e:
        print(f"Error fetching actions: {str(e)}")
        return jsonify({'error': str(e)}), 500

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        # Parse ISO format timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return timestamp.strftime('%d %B %Y - %I:%M %p UTC')
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return timestamp_str

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Supabase connection
        result = supabase.table('github_actions').select('count', count='exact').limit(1).execute()
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'total_actions': result.count
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/setup-database', methods=['POST'])
def setup_database():
    """Setup the database table (run once)"""
    try:
        # This endpoint helps create the table if it doesn't exist
        # In production, you'd run this once or use Supabase dashboard
        
        # Test if table exists by trying to query it
        try:
            supabase.table('github_actions').select('id').limit(1).execute()
            return jsonify({'status': 'Table already exists'})
        except:
            return jsonify({
                'status': 'Please create the table using Supabase dashboard',
                'sql': '''
                CREATE TABLE github_actions (
                    id SERIAL PRIMARY KEY,
                    action VARCHAR(50) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    from_branch VARCHAR(255),
                    to_branch VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    request_id VARCHAR(255),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                -- Add index for better query performance
                CREATE INDEX idx_github_actions_timestamp ON github_actions(timestamp DESC);
                CREATE INDEX idx_github_actions_action ON github_actions(action);
                '''
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting GitHub Webhook Receiver with Supabase...")
    print(f"Supabase URL: {SUPABASE_URL}")
    
    # Test Supabase connection
    try:
        result = supabase.table('github_actions').select('count', count='exact').limit(1).execute()
        print("✓ Supabase connection successful")
        print(f"✓ Current actions count: {result.count}")
    except Exception as e:
        print(f"✗ Supabase connection failed: {e}")
        print("Please check your SUPABASE_URL and SUPABASE_KEY")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
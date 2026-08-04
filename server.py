from flask import Flask, jsonify, request, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Parse DATABASE_URL connection string
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Parse the connection string
    url = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'host': url.hostname,
        'port': url.port or 5432,  # Default PostgreSQL port
        'database': url.path[1:],  # Remove leading '/'
        'user': url.username,
        'password': url.password
    }
    
    # Parse query parameters (like sslmode=require)
    if url.query:
        params = parse_qs(url.query)
        if 'sslmode' in params:
            DB_CONFIG['sslmode'] = params['sslmode'][0]
else:
    # Fallback to individual parameters (for backward compatibility)
    DB_CONFIG = {
        'host': os.getenv('LAKEBASE_HOST', 'your-lakebase-host.cloud.databricks.com'),
        'port': os.getenv('LAKEBASE_PORT', 5432),
        'database': 'databricks_postgres',
        'user': os.getenv('LAKEBASE_USER', 'your-username'),
        'password': os.getenv('LAKEBASE_PASSWORD', 'your-password')
    }

# Database connection helper
def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# Error handler decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error in {f.__name__}: {e}")
            return jsonify({'error': str(e)}), 500
    return decorated_function

# Serve static HTML files
@app.route('/')
def index():
    return send_from_directory('views', 'index.html')

@app.route('/editticket')
def edit_ticket_page():
    return send_from_directory('views', 'editticket.html')

@app.route('/editticketdetails')
def edit_ticket_details_page():
    return send_from_directory('views', 'editticketdetails.html')

# API Endpoints

# 1. GET all tickets
@app.route('/api/tickets', methods=['GET'])
@handle_errors
def get_tickets():
    """Fetch all tickets"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ticket_id, title, status, created_at, created_by
        FROM tickets
        ORDER BY created_at DESC
    """)
    
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(tickets)

# 2. GET single ticket
@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
@handle_errors
def get_ticket(ticket_id):
    """Fetch a single ticket by ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ticket_id, title, status, created_at, created_by
        FROM tickets
        WHERE ticket_id = %s
    """, (ticket_id,))
    
    ticket = cur.fetchone()
    cur.close()
    conn.close()
    
    if ticket is None:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify(ticket)

# 3. CREATE new ticket
@app.route('/api/tickets', methods=['POST'])
@handle_errors
def create_ticket():
    """Create a new ticket"""
    data = request.json
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO tickets (title, status, created_by, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING ticket_id, title, status, created_at, created_by
    """, (
        data.get('title'),
        data.get('status', 'open'),
        data.get('created_by'),
        datetime.now()
    ))
    
    new_ticket = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(new_ticket), 201

# 4. UPDATE ticket (full update)
@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@handle_errors
def update_ticket(ticket_id):
    """Update a ticket's details"""
    data = request.json
    
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # First, get the old values for history tracking
    cur.execute("""
        SELECT title, status FROM tickets WHERE ticket_id = %s
    """, (ticket_id,))
    
    old_ticket = cur.fetchone()
    if old_ticket is None:
        cur.close()
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Update the ticket
    cur.execute("""
        UPDATE tickets
        SET title = %s, status = %s
        WHERE ticket_id = %s
        RETURNING ticket_id, title, status, created_at, created_by
    """, (
        data.get('title'),
        data.get('status'),
        ticket_id
    ))
    
    updated_ticket = cur.fetchone()
    
    # Record history (if you have a ticket_history table)
    # This is optional - you can create this table later
    try:
        if old_ticket['title'] != data.get('title'):
            cur.execute("""
                INSERT INTO ticket_history (ticket_id, change_type, old_value, new_value, changed_at, changed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                'title_change',
                old_ticket['title'],
                data.get('title'),
                datetime.now(),
                data.get('changed_by', 'system')
            ))
        
        if old_ticket['status'] != data.get('status'):
            cur.execute("""
                INSERT INTO ticket_history (ticket_id, change_type, old_value, new_value, changed_at, changed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                'status_change',
                old_ticket['status'],
                data.get('status'),
                datetime.now(),
                data.get('changed_by', 'system')
            ))
    except Exception as e:
        # If ticket_history table doesn't exist, just skip it
        print(f"History tracking skipped: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(updated_ticket)

# 5. UPDATE ticket status only
@app.route('/api/tickets/<int:ticket_id>/status', methods=['PATCH'])
@handle_errors
def update_ticket_status(ticket_id):
    """Update only the ticket status"""
    data = request.json
    
    if not data.get('status'):
        return jsonify({'error': 'Status is required'}), 400
    
    if data['status'] not in ['open', 'in_progress', 'resolved']:
        return jsonify({'error': 'Invalid status value'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get old status for history
    cur.execute("""
        SELECT status FROM tickets WHERE ticket_id = %s
    """, (ticket_id,))
    
    old_ticket = cur.fetchone()
    if old_ticket is None:
        cur.close()
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Update status
    cur.execute("""
        UPDATE tickets
        SET status = %s
        WHERE ticket_id = %s
        RETURNING ticket_id, title, status, created_at, created_by
    """, (data.get('status'), ticket_id))
    
    updated_ticket = cur.fetchone()
    
    # Record history
    try:
        cur.execute("""
            INSERT INTO ticket_history (ticket_id, change_type, old_value, new_value, changed_at, changed_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            ticket_id,
            'status_change',
            old_ticket['status'],
            data.get('status'),
            datetime.now(),
            data.get('changed_by', 'system')
        ))
    except Exception as e:
        print(f"History tracking skipped: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(updated_ticket)

# 6. DELETE ticket (and its messages)
@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
@handle_errors
def delete_ticket(ticket_id):
    """Delete a ticket and all its messages"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # First, delete all messages for this ticket
    cur.execute("""
        DELETE FROM ticket_messages WHERE ticket_id = %s
    """, (ticket_id,))
    
    # Then, delete the ticket
    cur.execute("""
        DELETE FROM tickets WHERE ticket_id = %s RETURNING ticket_id
    """, (ticket_id,))
    
    deleted_ticket = cur.fetchone()
    
    if deleted_ticket is None:
        cur.close()
        conn.close()
        return jsonify({'error': 'Ticket not found'}), 404
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Ticket and associated messages deleted successfully'})

# 7. GET ticket messages
@app.route('/api/tickets/<int:ticket_id>/messages', methods=['GET'])
@handle_errors
def get_ticket_messages(ticket_id):
    """Fetch all messages for a ticket"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT message_id, ticket_id, message_text, author, created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC
    """, (ticket_id,))
    
    messages = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(messages)

# 8. CREATE new message
@app.route('/api/tickets/<int:ticket_id>/messages', methods=['POST'])
@handle_errors
def create_message(ticket_id):
    """Add a new message to a ticket"""
    data = request.json
    
    if not data.get('message_text'):
        return jsonify({'error': 'Message text is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO ticket_messages (ticket_id, message_text, author, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING message_id, ticket_id, message_text, author, created_at
    """, (
        ticket_id,
        data.get('message_text'),
        data.get('author'),
        datetime.now()
    ))
    
    new_message = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(new_message), 201

# 9. GET ticket history/timeline
@app.route('/api/tickets/<int:ticket_id>/history', methods=['GET'])
@handle_errors
def get_ticket_history(ticket_id):
    """Fetch ticket change history for timeline"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                change_type,
                old_value,
                new_value,
                changed_at,
                changed_by,
                field_name
            FROM ticket_history
            WHERE ticket_id = %s
            ORDER BY changed_at DESC
        """, (ticket_id,))
        
        history = cur.fetchall()
    except Exception as e:
        # If ticket_history table doesn't exist, return empty array
        print(f"History table not found: {e}")
        history = []
    
    cur.close()
    conn.close()
    
    return jsonify(history)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    # Databricks Apps sets DATABRICKS_APP_PORT, fallback to PORT or 8080
    port = int(os.getenv('DATABRICKS_APP_PORT', os.getenv('PORT', 8080)))
    app.run(host='0.0.0.0', port=port, debug=True)
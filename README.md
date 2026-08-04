# Support Tickets App

A full-stack support ticket management system using Flask, Lakebase Postgres, and modern web technologies.

## Features

* View all support tickets in a dashboard
* Create, read, update, and delete tickets
* Add messages to tickets
* Update ticket status (open, in_progress, resolved)
* View ticket edit history timeline
* Responsive design with modern UI

## Tech Stack

* **Backend**: Flask (Python)
* **Database**: Lakebase Postgres (Databricks)
* **Frontend**: HTML, CSS, JavaScript (Vanilla)
* **Deployment**: Databricks Apps

## Project Structure

```
support-tickets-app/
├── server.py                  # Flask server with CRUD endpoints
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (don't commit!)
├── setup_history_table.sql    # SQL script for ticket history table
├── views/
│   ├── index.html            # Main dashboard
│   ├── editticket.html       # Ticket details & timeline
│   └── editticketdetails.html # Edit ticket form
└── README.md
```

## Setup Instructions

### 1. Configure Environment Variables

Update the `.env` file with your Lakebase credentials:

```bash
LAKEBASE_HOST=your-lakebase-host.cloud.databricks.com
LAKEBASE_PORT=5432
LAKEBASE_USER=your-username
LAKEBASE_PASSWORD=your-password
PORT=8080
```

### 2. Set Up Database Tables

Your Lakebase database should have these tables:

**tickets table** (already exists):
```sql
-- ticket_id (bigint, identity)
-- title (varchar)
-- status (varchar)
-- created_at (timestamp with time zone)
-- created_by (varchar)
```

**ticket_messages table** (already exists):
```sql
-- message_id (bigint, identity)
-- ticket_id (bigint)
-- message_text (varchar(100))
-- author (varchar(50))
-- created_at (timestamp with time zone)
```

**ticket_history table** (optional, for timeline feature):
```bash
# Run the SQL script to create the history table:
python -c "import psycopg2; conn = psycopg2.connect(...); cur = conn.cursor(); cur.execute(open('setup_history_table.sql').read()); conn.commit()"
```

Or run the SQL directly in your Lakebase database.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
python server.py
```

The server will start on `http://localhost:8080`

## API Endpoints

### Tickets

* `GET /api/tickets` - Get all tickets
* `GET /api/tickets/<id>` - Get single ticket
* `POST /api/tickets` - Create new ticket
* `PUT /api/tickets/<id>` - Update ticket (full)
* `PATCH /api/tickets/<id>/status` - Update ticket status only
* `DELETE /api/tickets/<id>` - Delete ticket and its messages

### Messages

* `GET /api/tickets/<id>/messages` - Get all messages for a ticket
* `POST /api/tickets/<id>/messages` - Add new message

### History

* `GET /api/tickets/<id>/history` - Get ticket change history

### Health

* `GET /api/health` - Health check endpoint

## Usage

1. **Dashboard** (`/`): View all tickets, create new tickets, delete tickets
2. **Edit Ticket** (`/editticket?id=<ticket_id>`): View ticket details, update status, see timeline
3. **Edit Details** (`/editticketdetails?id=<ticket_id>`): Edit ticket title and status

## Database Connection

The app connects to Lakebase Postgres using the credentials from `.env`. Make sure your Lakebase endpoint is running and accessible.

## Deployment to Databricks Apps

1. Create a Databricks App in your workspace
2. Upload all files to the app directory
3. Configure environment variables in the app settings
4. Deploy the app

## Current Data

The database currently has:
* 3 tickets (open, in_progress, resolved)
* 9 messages (3 per ticket)

## Next Steps

* [ ] Add authentication/authorization
* [ ] Add ticket assignment feature
* [ ] Add file attachments
* [ ] Add email notifications
* [ ] Add search and filtering
* [ ] Add pagination for large datasets
* [ ] Implement CDC (Change Data Feed) with Spark

## Notes

* The `ticket_history` table is optional but recommended for the timeline feature
* Message text is limited to 100 characters (adjust schema if needed)
* Status values are: `open`, `in_progress`, `resolved`

## License

MIT
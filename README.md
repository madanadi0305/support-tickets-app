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

**Option A: Complete Fresh Setup**
Run the complete database setup script in your Lakebase database:
```bash
# This creates all tables with the correct schema
psql -h <LAKEBASE_HOST> -U <LAKEBASE_USER> -d databricks_postgres -f setup_database.sql
```

**Option B: Add Missing Column to Existing Table**
If your tables already exist but are missing the `updated_at` column:
```bash
# This adds the updated_at column to the tickets table
psql -h <LAKEBASE_HOST> -U <LAKEBASE_USER> -d databricks_postgres -f add_updated_at_column.sql
```

**Required Table Schema:**

**tickets table**:
```sql
CREATE TABLE tickets (
    ticket_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL  -- REQUIRED for edit functionality!
);
```

**ticket_messages table**:
```sql
CREATE TABLE ticket_messages (
    message_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL,
    message_text VARCHAR(100) NOT NULL,
    author VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

**ticket_history table** (optional, for timeline feature):
```sql
CREATE TABLE ticket_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_by VARCHAR(100)
);
```

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
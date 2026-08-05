-- Complete Database Setup for Support Tickets App
-- Run this script in your Lakebase Postgres database

-- 1. Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT chk_status CHECK (status IN ('open', 'in_progress', 'resolved'))
);

-- Create index on status for faster filtering
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);

-- 2. Create ticket_messages table
CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL,
    message_text VARCHAR(100) NOT NULL,
    author VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_ticket FOREIGN KEY (ticket_id) 
        REFERENCES tickets(ticket_id) ON DELETE CASCADE
);

-- Create index for faster message queries
CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_created_at ON ticket_messages(created_at ASC);

-- 3. Create ticket_history table (for timeline feature)
CREATE TABLE IF NOT EXISTS ticket_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_by VARCHAR(100),
    CONSTRAINT fk_ticket_history FOREIGN KEY (ticket_id) 
        REFERENCES tickets(ticket_id) ON DELETE CASCADE
);

-- Create indexes for faster history queries
CREATE INDEX IF NOT EXISTS idx_ticket_history_ticket_id ON ticket_history(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_history_changed_at ON ticket_history(changed_at DESC);

-- 4. Insert sample data (optional)
INSERT INTO tickets (title, status, created_at, created_by, updated_at)
VALUES 
    ('Login issue on mobile app', 'open', NOW() - INTERVAL '2 days', 'john.doe@example.com', NOW() - INTERVAL '2 days'),
    ('Feature request: Dark mode', 'in_progress', NOW() - INTERVAL '5 days', 'jane.smith@example.com', NOW() - INTERVAL '1 day'),
    ('Water Leak from the ceiling of my room', 'open', NOW() - INTERVAL '1 hour', 'madanadi0305@gmail.com', NOW() - INTERVAL '1 hour')
ON CONFLICT DO NOTHING;

-- Verify setup
SELECT 'Tables created successfully!' as status;
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('tickets', 'ticket_messages', 'ticket_history')
ORDER BY table_name, ordinal_position;
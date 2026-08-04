-- Optional: Create ticket_history table for timeline feature
-- This table tracks all changes made to tickets

CREATE TABLE IF NOT EXISTS ticket_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL,
    change_type VARCHAR(50) NOT NULL,  -- 'status_change', 'title_change', 'created', etc.
    field_name VARCHAR(50),             -- Name of the field that changed
    old_value TEXT,                     -- Previous value
    new_value TEXT,                     -- New value
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_by VARCHAR(100)             -- User who made the change
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_ticket_history_ticket_id ON ticket_history(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_history_changed_at ON ticket_history(changed_at);

-- Optional: Add a record for each existing ticket showing when it was created
INSERT INTO ticket_history (ticket_id, change_type, new_value, changed_at, changed_by)
SELECT 
    ticket_id,
    'created' as change_type,
    title as new_value,
    created_at,
    created_by
FROM tickets
WHERE ticket_id NOT IN (SELECT DISTINCT ticket_id FROM ticket_history WHERE change_type = 'created');
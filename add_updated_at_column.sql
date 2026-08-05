-- Add updated_at column to tickets table
-- This column tracks when a ticket was last modified

-- Add the column if it doesn't exist
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Set initial values for existing tickets (use created_at as initial value)
UPDATE tickets 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Make the column NOT NULL after setting initial values
ALTER TABLE tickets 
ALTER COLUMN updated_at SET NOT NULL;

-- Verify the change
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'tickets' 
    AND column_name = 'updated_at';
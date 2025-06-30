-- GitHub Webhook Actions Table
-- Run this SQL in your Supabase SQL Editor

-- Create the main table for storing GitHub webhook events
CREATE TABLE IF NOT EXISTS github_actions (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL CHECK (action IN ('push', 'pull_request', 'merge')),
    author VARCHAR(255) NOT NULL,
    from_branch VARCHAR(255),
    to_branch VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_github_actions_timestamp ON github_actions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_github_actions_action ON github_actions(action);
CREATE INDEX IF NOT EXISTS idx_github_actions_author ON github_actions(author);
CREATE INDEX IF NOT EXISTS idx_github_actions_to_branch ON github_actions(to_branch);

-- Add a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_github_actions_updated_at 
    BEFORE UPDATE ON github_actions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Add Row Level Security (RLS) for production
-- ALTER TABLE github_actions ENABLE ROW LEVEL SECURITY;

-- Optional: Create a policy for read access (uncomment for production)
-- CREATE POLICY "Allow read access for all users" ON github_actions FOR SELECT USING (true);

-- Optional: Create a policy for insert access (uncomment for production)
-- CREATE POLICY "Allow insert access for authenticated users" ON github_actions FOR INSERT WITH CHECK (true);

-- Create a view for recent actions (last 30 days)
CREATE OR REPLACE VIEW recent_github_actions AS
SELECT 
    id,
    action,
    author,
    from_branch,
    to_branch,
    timestamp,
    request_id,
    created_at
FROM github_actions
WHERE timestamp >= NOW() - INTERVAL '30 days'
ORDER BY timestamp DESC;

-- Create a function to get action statistics
CREATE OR REPLACE FUNCTION get_action_stats()
RETURNS TABLE(
    action_type VARCHAR(50),
    count BIGINT,
    latest_timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ga.action,
        COUNT(*) as count,
        MAX(ga.timestamp) as latest_timestamp
    FROM github_actions ga
    WHERE ga.timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY ga.action
    ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data for testing (optional)
INSERT INTO github_actions (action, author, from_branch, to_branch, timestamp, request_id) VALUES
('push', 'john_doe', NULL, 'main', NOW() - INTERVAL '1 hour', 'abc123'),
('pull_request', 'jane_smith', 'feature-branch', 'main', NOW() - INTERVAL '2 hours', '42'),
('merge', 'bob_wilson', 'hotfix', 'main', NOW() - INTERVAL '3 hours', '43');

-- Verify the setup
SELECT 'Setup completed successfully! 🎉' as status;
SELECT COUNT(*) as total_records FROM github_actions;
SELECT * FROM get_action_stats();
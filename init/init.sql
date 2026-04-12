CREATE TABLE IF NOT EXISTS threads (
  thread_id UUID PRIMARY KEY,
  user_id TEXT,
  title TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE TABLE IF NOT EXISTS messages (
  message_id UUID PRIMARY KEY,
  thread_id UUID REFERENCES threads(thread_id),
  role TEXT,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE TABLE IF NOT EXISTS tasks (
   task_id UUID PRIMARY KEY,
    task_type TEXT NOT NULL,          -- email_fetch, send_email, notify, etc.
    status TEXT NOT NULL,             -- pending, queued, processing, done, failed
    priority TEXT NOT NULL,           -- from urgency/LLM
    payload JSONB,                    -- actual task data (email id, content etc.)
    result JSONB,                     -- output/result
    schedule_type TEXT,               -- one_time / interval
    scheduled_time TIMESTAMP,         -- for one-time tasks
    interval_seconds INT,             -- for recurring tasks
    next_run_time TIMESTAMP,          -- important for scheduler
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INT DEFAULT 0,
);
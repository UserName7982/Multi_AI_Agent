CREATE TABLE IF NOT EXISTS threads (
  thread_id UUID PRIMARY KEY,
  user_id TEXT,
  title TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  message_id UUID PRIMARY KEY,
  thread_id UUID REFERENCES threads(thread_id),
  role TEXT,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
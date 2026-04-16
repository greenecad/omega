DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL,
  gift TEXT NOT NULL,
  grade INTEGER NOT NULL,
  email TEXT NOT NULL UNIQUE,
  admin INTEGER DEFAULT 0,
  participating INTEGER DEFAULT 0,
  points INTEGER DEFAULT 0,
  id_image TEXT, 
  completed TEXT DEFAULT '{"codes": [], "challenges": {} }',
  notifications TEXT DEFAULT '{"list": []}',
  hint_count INTEGER DEFAULT 5,
  hints_used TEXT DEFAULT '{"list": []}',
  friends TEXT DEFAULT '{"list": []}',
  friend_requests TEXT DEFAULT '{"list": []}',
  pfp TEXT DEFAULT 'img/placeholder-pfp.png',
  click_points INTEGER DEFAULT 0,
  umessage TEXT,
  target TEXT,
  targeted_by TEXT,
  target_pic TEXT,
  platform_hi INTEGER DEFAULT 0
);

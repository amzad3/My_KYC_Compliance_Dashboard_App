CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, country TEXT, risk_level TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Pending', beneficial_owner TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE documents (id INTEGER PRIMARY KEY, customer_id INTEGER, document_type TEXT, verified INTEGER DEFAULT 0, expiry_date TEXT, FOREIGN KEY(customer_id) REFERENCES customers(id));
CREATE TABLE reviews (id INTEGER PRIMARY KEY, customer_id INTEGER, reviewer TEXT, decision TEXT, notes TEXT, reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, customer_id INTEGER, action TEXT, details TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);

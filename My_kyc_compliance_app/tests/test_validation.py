import sqlite3
from validate_data import validate_database

def test_missing_database(tmp_path):
    ok, errors = validate_database(tmp_path / "missing.db")
    assert not ok
    assert "Database file does not exist" in errors

def test_valid_database(tmp_path):
    db = tmp_path / "test.db"
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE documents(id INTEGER);
    CREATE TABLE reviews(id INTEGER);
    CREATE TABLE audit_log(id INTEGER);
    INSERT INTO customers(name) VALUES ('Test Customer');
    """)
    con.close()
    ok, errors = validate_database(db)
    assert ok
    assert errors == []

def test_customer_without_name_fails(tmp_path):
    db = tmp_path / "test.db"
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE documents(id INTEGER);
    CREATE TABLE reviews(id INTEGER);
    CREATE TABLE audit_log(id INTEGER);
    INSERT INTO customers(name) VALUES ('');
    """)
    con.close()
    ok, errors = validate_database(db)
    assert not ok
    assert any("missing a name" in e for e in errors)

import sqlite3
from pathlib import Path

def validate_database(path="kyc.db"):
    if not Path(path).exists():
        return False, ["Database file does not exist"]
    con = sqlite3.connect(path)
    errors = []
    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in ("customers","documents","reviews","audit_log"):
        if table not in names:
            errors.append(f"Missing table: {table}")
    if "customers" in names:
        bad = con.execute("SELECT COUNT(*) FROM customers WHERE name IS NULL OR trim(name)=''").fetchone()[0]
        if bad: errors.append(f"{bad} customer(s) missing a name")
    con.close()
    return not errors, errors

if __name__ == "__main__":
    ok, errors = validate_database()
    print("Validation passed" if ok else "\\n".join(errors))

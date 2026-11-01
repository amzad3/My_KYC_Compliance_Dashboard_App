import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path("kyc.db")

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, country TEXT,
          risk_level TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Pending',
          beneficial_owner TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY, customer_id INTEGER, document_type TEXT,
          verified INTEGER DEFAULT 0, expiry_date TEXT,
          FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY, customer_id INTEGER, reviewer TEXT,
          decision TEXT, notes TEXT, reviewed_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY, customer_id INTEGER, action TEXT,
          details TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if count == 0:
            con.executemany("""INSERT INTO customers
                (name,email,country,risk_level,status,beneficial_owner)
                VALUES (?,?,?,?,?,?)""", [
                ("Aarav Mehta","aarav@example.test","India","Low","Approved","Aarav Mehta"),
                ("Maya Chen","maya@example.test","Singapore","Medium","Pending","Maya Chen"),
                ("Noah Williams","noah@example.test","United Kingdom","High","Review","Northstar Holdings Ltd")
            ])
            con.executemany("""INSERT INTO documents
                (customer_id,document_type,verified,expiry_date) VALUES (?,?,?,?)""", [
                (1,"Passport",1,"2028-05-30"),(1,"Proof of Address",1,"2027-03-15"),
                (2,"Passport",1,"2027-01-10"),(2,"Proof of Address",0,"2026-12-01"),
                (3,"Passport",0,"2026-11-15")
            ])

def get_customers(search=""):
    with connect() as con:
        return pd.read_sql_query(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ? ORDER BY id DESC",
            con, params=(f"%{search}%", f"%{search}%"))

def log_action(customer_id, action, details):
    with connect() as con:
        con.execute("INSERT INTO audit_log(customer_id,action,details) VALUES (?,?,?)",
                    (customer_id, action, details))

init_db()
st.set_page_config(page_title="KYC Compliance Dashboard", layout="wide")
st.title("KYC Compliance Dashboard")
st.caption("Customer due diligence • document verification • risk review • audit trail")

with connect() as con:
    total = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    pending = con.execute("SELECT COUNT(*) FROM customers WHERE status IN ('Pending','Review')").fetchone()[0]
    high = con.execute("SELECT COUNT(*) FROM customers WHERE risk_level='High'").fetchone()[0]
    docs_due = con.execute("SELECT COUNT(*) FROM documents WHERE expiry_date <= date('now','+90 day')").fetchone()[0]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Customers", total); c2.metric("Pending / Review", pending)
c3.metric("High risk", high); c4.metric("Documents expiring ≤90 days", docs_due)

pages = ["Customer register","Customer details & review","Expiry alerts","Audit history"]
page = st.sidebar.radio("Navigate", pages)

if page == "Customer register":
    st.subheader("Customer register")
    q = st.text_input("Search by name or email")
    df = get_customers(q)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.subheader("Add customer")
    with st.form("add_customer"):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        country = st.text_input("Country")
        risk = st.selectbox("Risk level", ["Low","Medium","High"])
        owner = st.text_input("Beneficial owner")
        submitted = st.form_submit_button("Add customer")
        if submitted:
            if not name.strip():
                st.error("Customer name is required.")
            else:
                with connect() as con:
                    cur = con.execute("""INSERT INTO customers(name,email,country,risk_level,beneficial_owner)
                        VALUES (?,?,?,?,?)""", (name.strip(),email.strip(),country.strip(),risk,owner.strip()))
                    cid = cur.lastrowid
                log_action(cid,"Customer created",f"Created {name.strip()}")
                st.success("Customer added.")
                st.rerun()

elif page == "Customer details & review":
    st.subheader("Customer details and review")
    customers = get_customers()
    if customers.empty:
        st.info("No customers available.")
    else:
        options = {f"{r['name']} (#{r['id']})": int(r['id']) for _,r in customers.iterrows()}
        selected = st.selectbox("Select customer", list(options))
        cid = options[selected]
        with connect() as con:
            customer = con.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
            docs = pd.read_sql_query("SELECT * FROM documents WHERE customer_id=?",con,params=(cid,))
        st.write({"Name":customer[1],"Email":customer[2],"Country":customer[3],
                  "Risk":customer[4],"Status":customer[5],"Beneficial owner":customer[6]})
        st.markdown("**Documents**")
        st.dataframe(docs, use_container_width=True, hide_index=True)
        with st.form("document_form"):
            st.markdown("**Add / verify document**")
            doc_type = st.selectbox("Document type",["Passport","National ID","Proof of Address","Business Registration","Other"])
            expiry = st.date_input("Expiry date")
            verified = st.checkbox("Mark as verified")
            add_doc = st.form_submit_button("Save document")
            if add_doc:
                with connect() as con:
                    con.execute("INSERT INTO documents(customer_id,document_type,verified,expiry_date) VALUES (?,?,?,?)",
                                (cid,doc_type,int(verified),str(expiry)))
                log_action(cid,"Document added",f"{doc_type}; verified={verified}; expiry={expiry}")
                st.success("Document saved."); st.rerun()
        with st.form("review_form"):
            st.markdown("**Record KYC review**")
            reviewer = st.text_input("Reviewer")
            decision = st.selectbox("Decision",["Pending","Approved","Rejected","Review"])
            notes = st.text_area("Review notes")
            save = st.form_submit_button("Save review")
            if save:
                with connect() as con:
                    con.execute("INSERT INTO reviews(customer_id,reviewer,decision,notes) VALUES (?,?,?,?)",
                                (cid,reviewer,decision,notes))
                    con.execute("UPDATE customers SET status=? WHERE id=?",(decision,cid))
                log_action(cid,"KYC decision",f"{decision}: {notes}")
                st.success("Review recorded."); st.rerun()

elif page == "Expiry alerts":
    st.subheader("Document expiry alerts")
    with connect() as con:
        alerts = pd.read_sql_query("""SELECT c.name,d.document_type,d.expiry_date,d.verified
            FROM documents d JOIN customers c ON c.id=d.customer_id
            WHERE date(d.expiry_date) <= date('now','+90 day')
            ORDER BY date(d.expiry_date)""",con)
    if alerts.empty: st.success("No documents expiring within 90 days.")
    else: st.dataframe(alerts,use_container_width=True,hide_index=True)

else:
    st.subheader("Audit history")
    with connect() as con:
        audit = pd.read_sql_query("""SELECT a.id,c.name,a.action,a.details,a.created_at
            FROM audit_log a LEFT JOIN customers c ON c.id=a.customer_id
            ORDER BY a.id DESC""",con)
    st.dataframe(audit,use_container_width=True,hide_index=True)

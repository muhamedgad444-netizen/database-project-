# ============================================================
#   db.py — Bulletproof Database Connection Helper
#   Hospital Information System
# ============================================================

import mysql.connector
from mysql.connector import errorcode

# ---- Your MySQL settings ----
HOST     = "127.0.0.1"  # Using IP is often more stable than 'localhost' on Windows
USER     = "root"
PASSWORD = ""           # Matches your successful Workbench command
DATABASE = "hospital_db"
PORT     = 3306

def get_connection():
    try:
        # Attempt connection with native password plugin
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            port=PORT,
            auth_plugin='mysql_native_password'
        )
        print(f"✅ [SUCCESS] Connected to {DATABASE} at {HOST}:{PORT}")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ [ERROR] Username or password incorrect.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ [ERROR] Database 'hospital_db' does not exist. Run the SQL script in Workbench!")
        else:
            print(f"❌ [ERROR] {err}")
        
        # Fallback: Try without the auth_plugin for older MySQL versions
        try:
            print("🔄 [RETRY] Attempting connection without specific auth_plugin...")
            conn = mysql.connector.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE,
                port=PORT
            )
            print("✅ [SUCCESS] Connected via fallback method.")
            return conn
        except:
            return None

def run_query(sql, params=None, fetch=True):
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"⚠️ [QUERY ERROR] {err}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

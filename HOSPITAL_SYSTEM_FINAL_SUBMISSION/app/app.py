import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import db, shutil, os
from datetime import datetime

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
#  PREMIUM HELPERS
# ─────────────────────────────────────────────
def safe_query(query, params=None, fetch=True):
    result = db.run_query(query, params, fetch)
    if result is None:
        messagebox.showerror("System Error", "Database communication failed.\nPlease check your MySQL connection.")
    return result

def make_tree(parent, columns, col_width=140):
    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="both", expand=True, padx=5, pady=5)
    search_fr = tk.Frame(frame, bg="white"); search_fr.pack(fill="x", pady=5)
    tk.Label(search_fr, text="🔍 Search:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=5)
    search_ent = ttk.Entry(search_fr, width=30); search_ent.pack(side="left", padx=5)
    sb = ttk.Scrollbar(frame, orient="vertical")
    tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=sb.set)
    sb.config(command=tree.yview)
    for c in columns: tree.heading(c, text=c); tree.column(c, width=col_width, anchor="center")
    tree.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
    def on_search(e):
        q = search_ent.get().lower()
        for i in tree.get_children():
            if q in " ".join([str(v) for v in tree.item(i, "values")]).lower(): tree.reattach(i, "", "end")
            else: tree.detach(i)
    search_ent.bind("<KeyRelease>", on_search)
    return tree

# ─────────────────────────────────────────────
#  MAIN APPLICATION - A++ EDITION
# ─────────────────────────────────────────────
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Information System | Professional Edition")
        self.geometry("1270x900")
        self.configure(bg="#f8fafc")
        style = ttk.Style(); style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TNotebook.Tab", font=("Segoe UI", 11), padding=[15, 6])
        self.current_user = None; self.container = tk.Frame(self, bg="#f8fafc"); self.container.pack(fill="both", expand=True)
        self.show_login()

    def clear(self):
        for w in self.container.winfo_children(): w.destroy()

    def top_bar(self, parent, title, role_icon="👤"):
        bar = tk.Frame(parent, bg="#1e3a8a", height=70); bar.pack(fill="x"); bar.pack_propagate(False)
        tk.Label(bar, text=f"{role_icon} {title}", font=("Segoe UI", 20, "bold"), bg="#1e3a8a", fg="white").pack(side="left", padx=25)
        ttk.Button(bar, text="🚪 Logout", command=self.show_login).pack(side="right", padx=25, pady=15)

    def show_login(self):
        self.current_user = None; self.clear()
        f = tk.Frame(self.container, bg="#f1f5f9"); f.pack(fill="both", expand=True)
        tk.Label(f, text="🏥 Hospital Management System", font=("Segoe UI", 34, "bold"), bg="#f1f5f9", fg="#1e3a8a").pack(pady=(120, 40))
        card = tk.Frame(f, bg="white", padx=40, pady=40, highlightbackground="#cbd5e1", highlightthickness=1); card.pack()
        tk.Label(card, text="Username", bg="white").pack(anchor="w"); eu = ttk.Entry(card, font=("Segoe UI", 14), width=30); eu.pack(pady=(0, 20))
        tk.Label(card, text="Password", bg="white").pack(anchor="w"); ep = ttk.Entry(card, font=("Segoe UI", 14), show="*", width=30); ep.pack(pady=(0, 30))
        def do_login():
            res = safe_query("SELECT * FROM USER_ACCOUNT WHERE username=%s AND password_hash=%s", (eu.get().strip(), ep.get().strip()))
            if res: 
                self.current_user = res[0]; r = self.current_user['role']; 
                # FIX: Logic for Option B Subtype Mapping
                if r == "Admin": self.show_admin()
                else:
                    # Detect which ID to use based on the role
                    self.current_user['profile_id'] = (res[0]['patient_id'] or res[0]['doctor_id'] or 
                                                       res[0]['nurse_id'] or res[0]['employee_id'])
                    if r == "Patient": self.show_patient()
                    elif r == "Doctor": self.show_doctor()
                    else: messagebox.showerror("Error", "Invalid role configuration.")
            else: messagebox.showerror("Error", "Invalid credentials.")
        ttk.Button(card, text="SECURE LOGIN", command=do_login).pack(fill="x")
        ttk.Button(card, text="REGISTER NEW ACCOUNT", command=self.show_register).pack(fill="x", pady=(10,0))

    def show_register(self):
        self.clear(); f = tk.Frame(self.container, padx=80, pady=50, bg="#f8fafc"); f.pack(fill="both", expand=True)
        tk.Label(f, text="✨ Create Your Account", font=("Segoe UI", 24, "bold"), bg="#f8fafc").pack(pady=20)
        grid = tk.Frame(f, bg="#f8fafc"); grid.pack(); fields = [("Full Name", "name"), ("SSN", "ssn"), ("Username", "user"), ("Password", "pass"), ("Email", "email"), ("Patient ID (Int)", "pid")]
        entries = {k: ttk.Entry(grid, font=("Segoe UI", 12), width=30) for _, k in fields}
        for i, (lbl, key) in enumerate(fields):
            tk.Label(grid, text=lbl+":", font=("Segoe UI", 12), bg="#f8fafc").grid(row=i, column=0, sticky="e", pady=8, padx=10)
            if key == "pass": entries[key].config(show="*"); entries[key].grid(row=i, column=1, pady=8)
        def do_reg():
            v = {k: e.get().strip() for k, e in entries.items()}
            # First create the patient record
            safe_query("INSERT INTO PATIENT (patient_number,ssn,name) VALUES (%s,%s,%s)", (v['pid'], v['ssn'], v['name']), fetch=False)
            # Then create the user account with the typed FK (Option B)
            safe_query("INSERT INTO USER_ACCOUNT (username,password_hash,email,role,patient_id) VALUES (%s,%s,%s,'Patient',%s)", (v['user'], v['pass'], v['email'], v['pid']), fetch=False)
            messagebox.showinfo("Done", "Account Created!"); self.show_login()
        ttk.Button(f, text="CREATE ACCOUNT", command=do_reg).pack(pady=25); ttk.Button(f, text="Back to Login", command=self.show_login).pack()

    def show_admin(self):
        self.clear(); f = tk.Frame(self.container); f.pack(fill="both", expand=True); self.top_bar(f, "Hospital Administration", "🛠️")
        s_fr = tk.Frame(f, bg="#f8fafc", pady=15); s_fr.pack(fill="x", padx=20)
        rev = safe_query("SELECT SUM(fee) as t FROM APPOINTMENT WHERE payment_status='Paid'")[0]['t'] or 0
        pc = safe_query("SELECT COUNT(*) as c FROM PATIENT")[0]['c']; ac = safe_query("SELECT COUNT(*) as c FROM APPOINTMENT WHERE status='Scheduled'")[0]['c']
        def card(parent, l, v, c):
            cd = tk.Frame(parent, bg="white", padx=15, pady=10, highlightbackground="#e2e8f0", highlightthickness=1); cd.pack(side="left", padx=10, expand=True, fill="x")
            tk.Label(cd, text=l, font=("Segoe UI", 10), bg="white", fg="#64748b").pack(); tk.Label(cd, text=v, font=("Segoe UI", 16, "bold"), bg="white", fg=c).pack()
        card(s_fr, "💰 REVENUE", f"${rev:,.2f}", "#16a34a"); card(s_fr, "👥 PATIENTS", pc, "#2563eb"); card(s_fr, "📅 PENDING", ac, "#ea580c")
        nb = ttk.Notebook(f); nb.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        tabs = [("📋 Visits", "SELECT * FROM vw_AppointmentReport", ("ID", "Patient", "Doctor", "Dept", "Date/Time", "Status", "Fee", "Pay")),
                ("🛏️ Rooms", "SELECT * FROM vw_RoomAllocation", ("Room", "Type", "Dept", "Status", "Occupant", "Admitted")),
                ("👥 Personnel", "SELECT employee_id, name, role, department_code FROM EMPLOYEE", ("ID", "Name", "Role", "Dept")),
                ("📬 Feedback", "SELECT form_id, user_id, rating, subject, status, submitted_at FROM CONTACT_FORM", ("ID", "User", "⭐", "Subject", "Status", "Date"))]
        for t, s, c in tabs:
            tab = tk.Frame(nb); nb.add(tab, text=f" {t} "); tree = make_tree(tab, c)
            for r in (safe_query(s) or []): tree.insert("", "end", values=list(r.values()))

    def show_patient(self):
        self.clear(); pid = self.current_user['profile_id']; pat = safe_query("SELECT * FROM PATIENT WHERE patient_number=%s", (pid,))[0]
        f = tk.Frame(self.container); f.pack(fill="both", expand=True); self.top_bar(f, f"Patient Portal: {pat['name']}", "🩹")
        s_fr = tk.Frame(f, bg="#f8fafc", pady=10); s_fr.pack(fill="x", padx=20)
        spent = safe_query("SELECT SUM(fee) as t FROM APPOINTMENT WHERE patient_number=%s AND payment_status='Paid'", (pid,))[0]['t'] or 0
        tk.Label(s_fr, text=f"Total Spending: ${spent:,.2f} | My Patient ID: {pid}", font=("Segoe UI", 12), bg="#f8fafc", fg="#1e3a8a").pack()
        nb = ttk.Notebook(f); nb.pack(fill="both", expand=True, padx=20, pady=20)
        t_prof = tk.Frame(nb, bg="white", padx=30, pady=30); nb.add(t_prof, text=" 🏥 My Medical Profile ")
        tk.Label(t_prof, text="My Medical History", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Label(t_prof, text=pat['medical_history'] or "No history recorded.", font=("Segoe UI", 12), bg="white", wraplength=800, justify="left").pack(anchor="w", pady=10)
        v_fr = tk.Frame(t_prof, bg="white"); v_fr.pack(anchor="w", pady=20)
        tk.Label(v_fr, text=f"🩸 BP: {pat['blood_pressure'] or '--'}", font=("Segoe UI", 14), bg="white").pack(side="left", padx=20); 
        tk.Label(v_fr, text=f"💓 HR: {pat['heart_rate'] or '--'} bpm", font=("Segoe UI", 14), bg="white").pack(side="left", padx=20); 
        tk.Label(v_fr, text=f"🌡️ Temp: {pat['temperature'] or '--'}°C", font=("Segoe UI", 14), bg="white").pack(side="left", padx=20);
        tk.Label(v_fr, text=f"🧪 Type: {pat['blood_type'] or '--'}", font=("Segoe UI", 14), bg="white").pack(side="left", padx=20)
        t1 = tk.Frame(nb); nb.add(t1, text=" 📅 My Visits "); tree = make_tree(t1, ("ID", "Doctor", "Scheduled At", "Status", "Payment"))
        def load():
            for i in tree.get_children(): tree.delete(i)
            for r in (safe_query("SELECT a.appointment_id, d.name, a.scheduled_at, a.status, a.payment_status FROM APPOINTMENT a JOIN DOCTOR d ON a.doctor_id=d.doctor_id WHERE a.patient_number=%s", (pid,)) or []): tree.insert("", "end", values=list(r.values()))
        load(); ttk.Button(t1, text="❌ Request Cancellation", command=lambda: [safe_query("UPDATE APPOINTMENT SET status='Cancelled', payment_status='Refunded' WHERE appointment_id=%s", (tree.item(tree.focus(), "values")[0],), fetch=False), load()]).pack(pady=5)
        t2 = tk.Frame(nb, padx=40, pady=20); nb.add(t2, text=" ➕ Book Appointment ")
        docs = safe_query("SELECT doctor_id, name, consultation_fee FROM DOCTOR") or []
        doc_map = {f"{d['name']} (${d['consultation_fee']})": (d['doctor_id'], d['consultation_fee']) for d in docs}
        cbo = ttk.Combobox(t2, values=list(doc_map.keys()), state="readonly", width=40); cbo.pack(pady=5); de = ttk.Entry(t2, width=30); de.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M")); de.pack(pady=5)
        def book():
            did, fee = doc_map[cbo.get()]; aid = int(datetime.now().timestamp() * 10) % 1000000
            safe_query("INSERT INTO APPOINTMENT (appointment_id,patient_number,doctor_id,scheduled_at,status,fee,payment_status) VALUES (%s,%s,%s,%s,'Scheduled',%s,'Paid')", (aid, pid, did, de.get(), fee), fetch=False); messagebox.showinfo("Success", "Visit Booked!"); load()
        ttk.Button(t2, text="SECURE BOOKING", command=book).pack(pady=10)
        
        # ── FEEDBACK TAB (NEW FEATURE)
        t_feed = tk.Frame(nb, bg="white", padx=40, pady=30); nb.add(t_feed, text=" 🌟 Send Feedback ")
        tk.Label(t_feed, text="How was your experience?", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Label(t_feed, text="Rating (1-5 Stars):", bg="white").pack(anchor="w", pady=(15,5))
        rcbo = ttk.Combobox(t_feed, values=["5 - Excellent", "4 - Good", "3 - Average", "2 - Poor", "1 - Terrible"], state="readonly", width=20); rcbo.pack(anchor="w"); rcbo.current(0)
        tk.Label(t_feed, text="Subject:", bg="white").pack(anchor="w", pady=(15,5))
        sub_e = ttk.Entry(t_feed, width=50); sub_e.pack(anchor="w")
        tk.Label(t_feed, text="Your Message:", bg="white").pack(anchor="w", pady=(15,5))
        msg_t = tk.Text(t_feed, height=6, width=50); msg_t.pack(anchor="w")
        def send_f():
            fid = int(datetime.now().timestamp()) % 100000; rating = rcbo.get()[0]
            safe_query("INSERT INTO CONTACT_FORM (form_id, user_id, subject, message, rating, submitted_at, status) VALUES (%s,%s,%s,%s,%s,NOW(),'Pending')", (fid, self.current_user['user_id'], sub_e.get(), msg_t.get("1.0", tk.END), rating), fetch=False)
            messagebox.showinfo("Success", "Thank you for your feedback! It has been sent to the Admins."); sub_e.delete(0, tk.END); msg_t.delete("1.0", tk.END)
        ttk.Button(t_feed, text="SUBMIT FEEDBACK", command=send_f).pack(anchor="w", pady=20)

    def show_doctor(self):
        self.clear(); did = self.current_user['profile_id']; doc = safe_query("SELECT * FROM DOCTOR WHERE doctor_id=%s", (did,))[0]
        f = tk.Frame(self.container); f.pack(fill="both", expand=True); self.top_bar(f, f"Doctor Portal: Dr. {doc['name']} (Lic: {doc['license_number'] or 'N/A'})", "🩺")
        s_fr = tk.Frame(f, bg="#f8fafc", pady=10); s_fr.pack(fill="x", padx=20)
        t_pats = safe_query("SELECT COUNT(DISTINCT patient_number) as c FROM APPOINTMENT WHERE doctor_id=%s", (did,))[0]['c']; t_earn = safe_query("SELECT SUM(fee) as t FROM APPOINTMENT WHERE doctor_id=%s AND status='Completed'", (did,))[0]['t'] or 0
        tk.Label(s_fr, text=f"Patients Treated: {t_pats} | Total Career Earnings: ${t_earn:,.2f}", font=("Segoe UI", 12, "bold"), bg="#f8fafc", fg="#1e3a8a").pack()
        nb = ttk.Notebook(f); nb.pack(fill="both", expand=True, padx=20, pady=20)
        t1 = tk.Frame(nb); nb.add(t1, text=" 📋 My Schedule "); tree = make_tree(t1, ("ID", "Patient", "Date/Time", "Status"))
        def load():
            for i in tree.get_children(): tree.delete(i)
            for r in (safe_query("SELECT a.appointment_id, p.name, a.scheduled_at, a.status FROM APPOINTMENT a JOIN PATIENT p ON a.patient_number=p.patient_number WHERE a.doctor_id=%s", (did,)) or []): tree.insert("", "end", values=list(r.values()))
        load(); ttk.Button(t1, text="✅ Mark Completed", command=lambda: [safe_query("UPDATE APPOINTMENT SET status='Completed' WHERE appointment_id=%s", (tree.item(tree.focus(), "values")[0],), fetch=False), load()]).pack(pady=5)
        t_presc = tk.Frame(nb, bg="white", padx=40, pady=30); nb.add(t_presc, text=" 💊 Write Prescription ")
        pats = safe_query("SELECT patient_number, name FROM PATIENT") or []
        p_map = {p['name']: p['patient_number'] for p in pats}
        pcbo = ttk.Combobox(t_presc, values=list(p_map.keys()), state="readonly", width=40); pcbo.pack(anchor="w", pady=5)
        tk.Label(t_presc, text="Medication & Dosage:", bg="white").pack(anchor="w")
        ptext = tk.Text(t_presc, height=4, width=50); ptext.pack(anchor="w", pady=5)
        tk.Label(t_presc, text="Directions (Usage):", bg="white").pack(anchor="w")
        dir_e = ttk.Entry(t_presc, width=50); dir_e.pack(anchor="w", pady=5)
        def save_p():
            pid = p_map[pcbo.get()]; prid = int(datetime.now().timestamp()) % 100000; 
            safe_query("INSERT INTO PRESCRIPTION (prescription_id, doctor_id, patient_number, prescription_date) VALUES (%s,%s,%s,NOW())", (prid, did, pid), fetch=False); 
            # Sync with the new Directions field in the associative table
            safe_query("INSERT INTO PRESCRIPTION_MEDICATION (prescription_id, medication_id, directions) VALUES (%s, 1, %s)", (prid, dir_e.get()), fetch=False)
            messagebox.showinfo("Success", "Prescription Saved!"); ptext.delete("1.0", tk.END); dir_e.delete(0, tk.END)
        ttk.Button(t_presc, text="SAVE & PRINT", command=save_p).pack(anchor="w", pady=10)
        t2 = tk.Frame(nb); nb.add(t2, text=" 🖼️ Patient Scans "); stree = make_tree(t2, ("ID", "Patient", "Path", "Type", "Date"))
        for r in (safe_query("SELECT s.scan_id, p.name, s.file_path, s.file_type, s.uploaded_at FROM SCAN_FILE s JOIN PATIENT p ON s.patient_number=p.patient_number WHERE s.doctor_id=%s", (did,)) or []): stree.insert("", "end", values=list(r.values()))

if __name__ == "__main__": HospitalApp().mainloop()

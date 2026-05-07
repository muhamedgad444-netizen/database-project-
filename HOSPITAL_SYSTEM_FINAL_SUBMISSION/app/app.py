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
                    elif r == "Nurse": self.show_nurse()
                    else: messagebox.showerror("Error", "Invalid role configuration.")
            else: messagebox.showerror("Error", "Invalid credentials.")
        ttk.Button(card, text="SECURE LOGIN", command=do_login).pack(fill="x")
        ttk.Button(card, text="REGISTER NEW ACCOUNT", command=self.show_register).pack(fill="x", pady=(10,0))

    def show_register(self):
        self.clear()
        f = tk.Frame(self.container, padx=80, pady=30, bg="#f8fafc"); f.pack(fill="both", expand=True)
        tk.Label(f, text="✨ Create Your Account", font=("Segoe UI", 24, "bold"), bg="#f8fafc").pack(pady=(10, 15))

        # ── Role Selector
        role_fr = tk.Frame(f, bg="#f8fafc"); role_fr.pack(pady=(0, 10))
        tk.Label(role_fr, text="Register as:", font=("Segoe UI", 13, "bold"), bg="#f8fafc").pack(side="left", padx=10)
        role_var = tk.StringVar(value="Patient")
        for r in ["Patient", "Doctor", "Nurse"]:
            ttk.Radiobutton(role_fr, text=r, variable=role_var, value=r, command=lambda: update_fields()).pack(side="left", padx=10)

        # ── Dynamic Fields Container
        grid = tk.Frame(f, bg="#f8fafc"); grid.pack()
        entries = {}

        def update_fields():
            for w in grid.winfo_children(): w.destroy()
            entries.clear()
            role = role_var.get()
            # Common fields for all roles
            common = [("Full Name", "name"), ("SSN", "ssn"), ("Username", "user"), ("Password", "pass"), ("Email", "email")]
            if role == "Patient":
                fields = common + [("Patient ID (Int)", "pid"), ("Blood Type", "blood"), ("Sex (Male/Female)", "sex")]
            elif role == "Doctor":
                fields = common + [("Doctor ID (Int)", "did"), ("Specialty", "major"), ("License Number", "lic"), ("Department Code", "dept"), ("Sex (Male/Female)", "sex")]
            elif role == "Nurse":
                fields = common + [("Nurse ID (Int)", "nid"), ("Department Code", "dept"), ("Phone", "phone"), ("Sex (Male/Female)", "sex")]

            for i, (lbl, key) in enumerate(fields):
                tk.Label(grid, text=lbl + ":", font=("Segoe UI", 11), bg="#f8fafc").grid(row=i, column=0, sticky="e", pady=5, padx=10)
                ent = ttk.Entry(grid, font=("Segoe UI", 11), width=30)
                if key == "pass": ent.config(show="*")
                ent.grid(row=i, column=1, pady=5)
                entries[key] = ent

        update_fields()  # Initialize with Patient fields

        def do_reg():
            v = {k: e.get().strip() for k, e in entries.items()}
            if not v.get('name') or not v.get('ssn') or not v.get('user') or not v.get('pass') or not v.get('email'):
                messagebox.showwarning("Missing Fields", "Please fill in all required fields."); return
            role = role_var.get()
            try:
                if role == "Patient":
                    safe_query("INSERT INTO PATIENT (patient_number,ssn,name,blood_type,sex) VALUES (%s,%s,%s,%s,%s)",
                               (v['pid'], v['ssn'], v['name'], v.get('blood',''), v.get('sex','Male')), fetch=False)
                    safe_query("INSERT INTO USER_ACCOUNT (username,password_hash,email,role,patient_id) VALUES (%s,%s,%s,'Patient',%s)",
                               (v['user'], v['pass'], v['email'], v['pid']), fetch=False)
                elif role == "Doctor":
                    safe_query("INSERT INTO DOCTOR (doctor_id,ssn,name,major_area,license_number,department_code,sex) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                               (v['did'], v['ssn'], v['name'], v.get('major',''), v.get('lic',''), v.get('dept','1'), v.get('sex','Male')), fetch=False)
                    safe_query("INSERT INTO USER_ACCOUNT (username,password_hash,email,role,doctor_id) VALUES (%s,%s,%s,'Doctor',%s)",
                               (v['user'], v['pass'], v['email'], v['did']), fetch=False)
                elif role == "Nurse":
                    safe_query("INSERT INTO NURSE (nurse_id,ssn,name,department_code,phone,sex) VALUES (%s,%s,%s,%s,%s,%s)",
                               (v['nid'], v['ssn'], v['name'], v.get('dept','1'), v.get('phone',''), v.get('sex','Male')), fetch=False)
                    safe_query("INSERT INTO USER_ACCOUNT (username,password_hash,email,role,nurse_id) VALUES (%s,%s,%s,'Nurse',%s)",
                               (v['user'], v['pass'], v['email'], v['nid']), fetch=False)
                messagebox.showinfo("Done", f"{role} account created successfully!"); self.show_login()
            except Exception as ex:
                messagebox.showerror("Error", f"Registration failed: {ex}")

        ttk.Button(f, text="CREATE ACCOUNT", command=do_reg).pack(pady=15)
        ttk.Button(f, text="Back to Login", command=self.show_login).pack()

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
        # ── Visits Tab (with Drop Appointment)
        t_visits = tk.Frame(nb); nb.add(t_visits, text=" 📋 Visits ")
        visit_tree = make_tree(t_visits, ("ID", "Patient", "Doctor", "Dept", "Date/Time", "Status", "Fee", "Pay"))
        def load_visits():
            for i in visit_tree.get_children(): visit_tree.delete(i)
            for r in (safe_query("SELECT * FROM vw_AppointmentReport") or []): visit_tree.insert("", "end", values=list(r.values()))
        load_visits()
        btn_fr = tk.Frame(t_visits); btn_fr.pack(pady=5)
        def admin_drop():
            sel = visit_tree.focus()
            if not sel: messagebox.showwarning("Warning", "Select an appointment first."); return
            aid = visit_tree.item(sel, "values")[0]
            safe_query("UPDATE APPOINTMENT SET status='Cancelled', payment_status='Refunded' WHERE appointment_id=%s", (aid,), fetch=False)
            messagebox.showinfo("Done", f"Appointment {aid} has been dropped."); load_visits()
        ttk.Button(btn_fr, text="❌ Drop Appointment", command=admin_drop).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="✅ Mark Completed", command=lambda: [safe_query("UPDATE APPOINTMENT SET status='Completed' WHERE appointment_id=%s", (visit_tree.item(visit_tree.focus(), "values")[0],), fetch=False), load_visits()]).pack(side="left", padx=5)
        # ── Other Tabs
        other_tabs = [("🛏️ Rooms", "SELECT * FROM vw_RoomAllocation", ("Room", "Type", "Dept", "Status", "Occupant", "Admitted")),
                      ("👥 Personnel", "SELECT employee_id, name, role, department_code FROM EMPLOYEE", ("ID", "Name", "Role", "Dept")),
                      ("📬 Feedback", "SELECT form_id, user_id, rating, subject, status, submitted_at FROM CONTACT_FORM", ("ID", "User", "⭐", "Subject", "Status", "Date"))]
        for t, s, c in other_tabs:
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
        load()
        doc_btn_fr = tk.Frame(t1); doc_btn_fr.pack(pady=5)
        def doc_drop():
            sel = tree.focus()
            if not sel: messagebox.showwarning("Warning", "Select an appointment first."); return
            aid = tree.item(sel, "values")[0]
            safe_query("UPDATE APPOINTMENT SET status='Cancelled', payment_status='Refunded' WHERE appointment_id=%s", (aid,), fetch=False)
            messagebox.showinfo("Done", f"Appointment {aid} has been dropped."); load()
        ttk.Button(doc_btn_fr, text="✅ Mark Completed", command=lambda: [safe_query("UPDATE APPOINTMENT SET status='Completed' WHERE appointment_id=%s", (tree.item(tree.focus(), "values")[0],), fetch=False), load()]).pack(side="left", padx=5)
        ttk.Button(doc_btn_fr, text="❌ Drop Appointment", command=doc_drop).pack(side="left", padx=5)
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

    def show_nurse(self):
        self.clear(); nid = self.current_user['profile_id']
        nurse = safe_query("SELECT * FROM NURSE WHERE nurse_id=%s", (nid,))[0]
        f = tk.Frame(self.container); f.pack(fill="both", expand=True)
        self.top_bar(f, f"Nurse Portal: {nurse['name']}", "🏥")

        # ── Stats Bar
        s_fr = tk.Frame(f, bg="#f8fafc", pady=10); s_fr.pack(fill="x", padx=20)
        dept = safe_query("SELECT name FROM DEPARTMENT WHERE department_code=%s", (nurse['department_code'],))
        dept_name = dept[0]['name'] if dept else 'N/A'
        room_info = 'Not Assigned'
        if nurse.get('room_id'):
            rm = safe_query("SELECT room_number, room_type, status FROM ROOM WHERE room_id=%s", (nurse['room_id'],))
            if rm: room_info = f"{rm[0]['room_number']} ({rm[0]['room_type']}) - {rm[0]['status']}"
        tk.Label(s_fr, text=f"Department: {dept_name} | Assigned Room: {room_info} | Nurse ID: {nid}",
                 font=("Segoe UI", 12, "bold"), bg="#f8fafc", fg="#1e3a8a").pack()

        nb = ttk.Notebook(f); nb.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Tab 1: Admitted Patients in My Department
        t1 = tk.Frame(nb); nb.add(t1, text=" 🛏️ My Department Patients ")
        tree1 = make_tree(t1, ("Adm.ID", "Patient", "Admitted On", "Status"))
        for r in (safe_query(
            "SELECT a.admission_id, p.name, a.admission_date, a.status "
            "FROM ADMISSION a JOIN PATIENT p ON a.patient_number=p.patient_number "
            "WHERE a.department_code=%s", (nurse['department_code'],)) or []):
            tree1.insert("", "end", values=list(r.values()))

        # ── Tab 2: Room Allocation in My Department
        t2 = tk.Frame(nb); nb.add(t2, text=" 🏨 Room Status ")
        tree2 = make_tree(t2, ("Room ID", "Room #", "Type", "Status", "Capacity"))
        for r in (safe_query(
            "SELECT room_id, room_number, room_type, status, capacity "
            "FROM ROOM WHERE department_code=%s", (nurse['department_code'],)) or []):
            tree2.insert("", "end", values=list(r.values()))

        # ── Tab 3: Today's Appointments in My Department
        t3 = tk.Frame(nb); nb.add(t3, text=" 📋 Department Schedule ")
        tree3 = make_tree(t3, ("ID", "Patient", "Doctor", "Date/Time", "Status"))
        for r in (safe_query(
            "SELECT a.appointment_id, p.name, d.name, a.scheduled_at, a.status "
            "FROM APPOINTMENT a "
            "JOIN PATIENT p ON a.patient_number=p.patient_number "
            "JOIN DOCTOR d ON a.doctor_id=d.doctor_id "
            "WHERE d.department_code=%s ORDER BY a.scheduled_at", (nurse['department_code'],)) or []):
            tree3.insert("", "end", values=list(r.values()))

        # ── Tab 4: Send Feedback
        t_feed = tk.Frame(nb, bg="white", padx=40, pady=30); nb.add(t_feed, text=" 🌟 Send Feedback ")
        tk.Label(t_feed, text="How was your shift?", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Label(t_feed, text="Rating (1-5 Stars):", bg="white").pack(anchor="w", pady=(15, 5))
        rcbo = ttk.Combobox(t_feed, values=["5 - Excellent", "4 - Good", "3 - Average", "2 - Poor", "1 - Terrible"],
                            state="readonly", width=20); rcbo.pack(anchor="w"); rcbo.current(0)
        tk.Label(t_feed, text="Subject:", bg="white").pack(anchor="w", pady=(15, 5))
        sub_e = ttk.Entry(t_feed, width=50); sub_e.pack(anchor="w")
        tk.Label(t_feed, text="Your Message:", bg="white").pack(anchor="w", pady=(15, 5))
        msg_t = tk.Text(t_feed, height=6, width=50); msg_t.pack(anchor="w")
        def send_f():
            fid = int(datetime.now().timestamp()) % 100000; rating = rcbo.get()[0]
            safe_query("INSERT INTO CONTACT_FORM (form_id, user_id, subject, message, rating, submitted_at, status) VALUES (%s,%s,%s,%s,%s,NOW(),'Pending')",
                       (fid, self.current_user['user_id'], sub_e.get(), msg_t.get("1.0", tk.END), rating), fetch=False)
            messagebox.showinfo("Success", "Feedback submitted!"); sub_e.delete(0, tk.END); msg_t.delete("1.0", tk.END)
        ttk.Button(t_feed, text="SUBMIT FEEDBACK", command=send_f).pack(anchor="w", pady=20)

if __name__ == "__main__": HospitalApp().mainloop()

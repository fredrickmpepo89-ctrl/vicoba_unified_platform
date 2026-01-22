"""
VICOBA UNIFIED PLATFORM - COMPLETE SINGLE FILE
Combines ALL 14 files into one comprehensive application
"""

# ==================== IMPORTS ====================
import sqlite3
import hashlib
import os
import sys
import re
import json
import csv
import smtplib
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

"""
VICOBA UNIFIED PLATFORM - COMPLETE SINGLE FILE
Combines ALL 14 files into one comprehensive application
"""

# ==================== IMPORTS ====================
import sqlite3
import hashlib
import os
import sys
import re
import json
import csv
import smtplib
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

# ==================== CONFIGURATION ====================
DB_FILE = "vicoba_unified.db"
APP_NAME = "VICOBA DIGITAL 2.0"
APP_VERSION = "2.0.0"

MESSAGES = {
    "en": {
        "invalid_pin": "PIN must be 4 digits",
        "invalid_phone": "Phone must be in format 255xxxxxxxxx",
        "invalid_name": "Name must be 3-50 characters, letters and spaces only",
        "invalid_group": "Group ID must be 3-20 alphanumeric characters",
        "required": "This field is required",
        "login_success": "Login successful!",
        "login_failed": "Invalid credentials",
        "registration_success": "Registration successful! Use PIN to login.",
        "phone_exists": "Phone already registered.",
        "member_exists": "Member already exists",
        "member_not_found": "Member not found",
        "round_completed": "🎉 Round completed! {recipient} received {amount}",
        "payment_success": "Payment of {amount} from {payer} to {payee} recorded!",
        "contribution_success": "Contribution of {amount} recorded for {name}"
    },
    "sw": {
        "invalid_pin": "PIN lazima iwe tarakimu 4",
        "invalid_phone": "Namba ya simu lazima iwe 255xxxxxxxxx",
        "invalid_name": "Jina lazima liwe herufi 3-50 pekee",
        "invalid_group": "Kitambulisho cha kikundi lazima kiwe herufi 3-20",
        "required": "Sehemu hii inahitajika",
        "login_success": "Umefanikiwa kuingia!",
        "login_failed": "Umekosea namba ya siri",
        "registration_success": "Usajili umefanikiwa! Tumia PIN kuingia.",
        "phone_exists": "Namba ya simu tayari imesajiliwa.",
        "member_exists": "Mwanachama tayari yupo.",
        "member_not_failed": "Mwanachama hajapatikana"
    }
}

VALIDATION_PATTERNS = {
    "phone": r'^255\d{9}$',
    "name": r'^[\w\s]{3,50}$',
    "group_id": r'^[\w]{3,20}$',
    "pin": r'^\d{4}$'
}

# ==================== UTILITY FUNCTIONS ====================
def safe_int(value: Optional[str]) -> int:
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def generate_salt() -> str:
    return os.urandom(16).hex()

def hash_pin(pin: str, salt: str) -> str:
    return hashlib.sha256((pin + salt).encode()).hexdigest()

def format_currency(amount: int) -> str:
    return f"Tsh {amount:,}"

def validate_phone(phone: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['phone'], phone))

def validate_name(name: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['name'], name))

def validate_pin(pin: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['pin'], pin))

def validate_group_id(group_id: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['group_id'], group_id))

def confirm_action(message: str) -> bool:
    response = input(f"{message} (Y/N): ").strip().upper()
    return response == 'Y'

def get_message(key: str, language: str = "en") -> str:
    return MESSAGES.get(language, {}).get(key, key)

# ==================== UI FUNCTIONS ====================
def detect_device_type() -> str:
    if hasattr(sys, 'getandroidapilevel'):
        return "SMARTPHONE"
    elif sys.platform == 'darwin':
        return "SMARTPHONE"
    else:
        return "FEATURE_PHONE"

def detect_phone_number() -> str:
    return "255123456789"

def show_menu(menu_type: str, device_type: str, role: str = 'MEMBER') -> None:
    menu_options = {
        "AUTH": ["1. Register", "2. Login", "0. Exit"],
        "MAIN_MEMBER": [
            "1. Make Contribution", 
            "2. Make Payment", 
            "3. View Round Tracker", 
            "4. View Member Summary", 
            "5. View Transactions", 
            "6. Export Report",
            "7. Logout"
        ],
        "MAIN_ADMIN": [
            "1. Add Member", 
            "2. Make Contribution", 
            "3. Make Payment", 
            "4. View Round Tracker", 
            "5. View Member Summary", 
            "6. View Transactions", 
            "7. Manage Groups", 
            "8. Export Report",
            "9. Logout"
        ]
    }

    if menu_type == "AUTH":
        menu_items = menu_options["AUTH"]
        title = "VICOBA DIGITAL 2.0"
    elif menu_type == "MAIN":
        menu_items = menu_options["MAIN_ADMIN"] if role == 'ADMIN' else menu_options["MAIN_MEMBER"]
        title = "MAIN MENU"
    else:
        menu_items = []
        title = "MENU"

    if device_type == "FEATURE_PHONE":
        print(f"\n{title}")
        for item in menu_items:
            print(item)
    else:
        print("\n" + "="*40)
        print(f"    {title}")
        print("="*40)
        for item in menu_items:
            print(item)
        print("="*40)

# ==================== DATABASE FUNCTIONS ====================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        phone TEXT PRIMARY KEY,
        pin_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        group_ids TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'MEMBER',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Members table
    c.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_name TEXT,
        phone TEXT,
        total_contributions INTEGER NOT NULL DEFAULT 0,
        total_received INTEGER NOT NULL DEFAULT 0,
        group_id TEXT NOT NULL,
        PRIMARY KEY (member_name, group_id)
    )
    """)
    
    # Rounds table
    c.execute("""
    CREATE TABLE IF NOT EXISTS rounds (
        round_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_receiving TEXT,
        total_amount INTEGER,
        round_date TEXT,
        group_id TEXT NOT NULL
    )
    """)
    
    # Transactions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT,
        action TEXT,
        amount INTEGER,
        timestamp TEXT,
        round_id INTEGER,
        group_id TEXT NOT NULL
    )
    """)
    
    # Groups table
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        group_name TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create default admin user
    c.execute("SELECT * FROM users WHERE phone=?", ("255123456789",))
    if not c.fetchone():
        salt = generate_salt()
        pin_hash = hash_pin("1234", salt)
        c.execute(
            "INSERT INTO users (phone, pin_hash, salt, group_ids, role) VALUES (?,?,?,?,?)",
            ("255123456789", pin_hash, salt, json.dumps(["TEST_GROUP"]), 'ADMIN'))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ==================== AUTHENTICATION FUNCTIONS ====================
def register_user(device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- REGISTER ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED REGISTRATION")
        print("="*40)
    
    phone = detect_phone_number()
    if not phone:
        phone = input("Enter phone (255xxxxxxx): ").strip()
    
    if not validate_phone(phone):
        return get_message("invalid_phone")
    
    print(f"📱 Detected phone: {phone}")
    pin = input("🔐 Create 4-digit PIN: ").strip()
    if not validate_pin(pin):
        return get_message("invalid_pin")
    
    group_id = input("🏷️  Group ID: ").strip()
    if not validate_group_id(group_id):
        return get_message("invalid_group")
    
    role = input("👤 Role (ADMIN/MEMBER): ").strip().upper() or 'MEMBER'
    if role not in ['ADMIN', 'MEMBER']:
        return "Invalid role"
    
    if not confirm_action("✅ Confirm registration?"):
        return "Registration cancelled"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM users WHERE phone=?", (phone,))
        if c.fetchone():
            return get_message("phone_exists")
        
        salt = generate_salt()
        pin_hash = hash_pin(pin, salt)
        c.execute(
            "INSERT INTO users (phone, pin_hash, salt, group_ids, role) VALUES (?,?,?,?,?)",
            (phone, pin_hash, salt, json.dumps([group_id]), role)
        )
        conn.commit()
        return get_message("registration_success")
    except sqlite3.IntegrityError:
        return get_message("phone_exists")
    finally:
        conn.close()

def login_user(device_type: str) -> Optional[Dict[str, Any]]:
    if device_type == "FEATURE_PHONE":
        print("\n--- LOGIN ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED LOGIN")
        print("="*40)
    
    phone = detect_phone_number()
    if not phone:
        phone = input("Enter phone (255xxxxxxx): ").strip()
    
    if not validate_phone(phone):
        return None
    
    print(f"📱 Detected phone: {phone}")
    pin = input("🔐 Enter PIN: ").strip()
    if not validate_pin(pin):
        return None
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE phone=?", (phone,))
    user = c.fetchone()
    conn.close()
    
    if user:
        stored_hash = user['pin_hash']
        salt = user['salt']
        role = user['role']
        group_ids = json.loads(user['group_ids'])
        if hash_pin(pin, salt) == stored_hash:
            return {
                "phone": phone,
                "group_ids": group_ids,
                "role": role
            }
    
    return None

# ==================== MEMBER MANAGEMENT ====================
def get_member(name: str, group_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM members WHERE member_name=? AND group_id=?", (name, group_id))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_all_members(group_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM members WHERE group_id=? ORDER BY member_name", (group_id,))
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def save_member(member_data: Dict[str, Any], group_id: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("""
        INSERT OR REPLACE INTO members VALUES (?,?,?,?,?)
        """, (
            member_data["member_name"],
            member_data.get("phone", ""),
            safe_int(member_data["total_contributions"]),
            safe_int(member_data["total_received"]),
            group_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error saving member: {e}")
        return False
    finally:
        conn.close()

def add_member(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- ADD MEMBER ---")
    else:
        print("\n" + "="*40)
        print("        ADD NEW MEMBER")
        print("="*40)
    
    name = input("👤 Member name: ").strip()
    if not validate_name(name):
        return get_message("invalid_name")
    
    if get_member(name, group_id):
        return get_message("member_exists")
    
    phone = input("📱 Phone (optional): ").strip()
    if phone and not validate_phone(phone):
        return get_message("invalid_phone")
    
    if not confirm_action("✅ Confirm adding member?"):
        return "Cancelled"
    
    save_member({
        "member_name": name,
        "phone": phone,
        "total_contributions": 0,
        "total_received": 0
    }, group_id)
    
    return f"✅ Member {name} added successfully!"

# ==================== CONTRIBUTION SYSTEM ====================
def log_transaction(member_name: str, action: str, amount: int, 
                   round_id: Optional[int], group_id: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO transactions VALUES (NULL,?,?,?,?,?,?)",
            (member_name, action, amount, datetime.now().isoformat(), round_id, group_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error logging transaction: {e}")
        return False
    finally:
        conn.close()

def contribute(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MAKE CONTRIBUTION ---")
    else:
        print("\n" + "="*40)
        print("        MAKE CONTRIBUTION")
        print("="*40)
    
    name = input("👤 Member name: ").strip()
    if not validate_name(name):
        return get_message("invalid_name")
    
    amount_str = input("💰 Amount: ").strip()
    amount = safe_int(amount_str)
    if amount <= 0:
        return "❌ Invalid amount"
    
    member = get_member(name, group_id)
    if not member:
        return get_message("member_not_found")
    
    if not confirm_action(f"✅ Confirm contribution of {format_currency(amount)}?"):
        return "❌ Cancelled"
    
    member["total_contributions"] += amount
    save_member(member, group_id)
    
    log_transaction(name, "CONTRIBUTION", amount, None, group_id)
    
    return get_message("contribution_success").format(
        amount=format_currency(amount),
        name=name
    )

# ==================== ROUND MANAGEMENT ====================
def create_round(member_receiving: str, total_amount: int, group_id: str) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    
    round_date = datetime.now().isoformat()
    c.execute(
        "INSERT INTO rounds VALUES (NULL,?,?,?,?)", 
        (member_receiving, total_amount, round_date, group_id)
    )
    round_id = c.lastrowid
    conn.commit()
    conn.close()
    
    member = get_member(member_receiving, group_id)
    if member:
        member["total_received"] += total_amount
        save_member(member, group_id)
    
    log_transaction(member_receiving, "ROUND_RECEIVED", total_amount, round_id, group_id)
    return round_id

def get_current_round_contributions(group_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT round_id FROM rounds WHERE group_id=? ORDER BY round_id DESC LIMIT 1", (group_id,))
    latest_round = c.fetchone()
    latest_id = latest_round['round_id'] if latest_round else 0
    
    c.execute("""
        SELECT member_name, SUM(amount) AS contributed
        FROM transactions 
        WHERE action='CONTRIBUTION' AND group_id=? AND (round_id IS NULL OR round_id > ?)
        GROUP BY member_name
    """, (group_id, latest_id))
    
    contribs = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return contribs

def get_next_recipient(group_id: str) -> Optional[str]:
    members = get_all_members(group_id)
    if not members:
        return None
    
    min_received = min(m["total_received"] for m in members)
    candidates = [m["member_name"] for m in members if m["total_received"] == min_received]
    return sorted(candidates)[0] if candidates else None

def auto_finalize_round(group_id: str) -> bool:
    contribs = get_current_round_contributions(group_id)
    all_members = get_all_members(group_id)
    
    if len(contribs) == len(all_members) and all(c["contributed"] > 0 for c in contribs):
        total_amount = sum(c["contributed"] for c in contribs)
        next_recipient = get_next_recipient(group_id)
        
        if next_recipient and total_amount > 0:
            round_id = create_round(next_recipient, total_amount, group_id)
            
            conn = get_db_connection()
            c = conn.cursor()
            
            for contrib in contribs:
                c.execute("""
                    UPDATE transactions 
                    SET round_id=? 
                    WHERE member_name=? AND action='CONTRIBUTION' AND round_id IS NULL AND group_id=?
                """, (round_id, contrib["member_name"], group_id))
            conn.commit()
            conn.close()
            
            return True
    
    return False

# ==================== PAYMENT SYSTEM ====================
def make_payment(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MEMBER PAYMENT ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED PAYMENT")
        print("="*40)
    
    members = get_all_members(group_id)
    if len(members) < 2:
        return "❌ Need at least 2 members for payments"
    
    print("\n👤 Select payer:")
    for i, member in enumerate(members, 1):
        print(f"  {i}. {member['member_name']} - {format_currency(member['total_contributions'])}")
    
    try:
        payer_idx = int(input("\n📥 Payer number: ")) - 1
        if payer_idx < 0 or payer_idx >= len(members):
            return "❌ Invalid payer selection"
        
        payer = members[payer_idx]
        
        print("\n👤 Select payee:")
        payees = [m for m in members if m['member_name'] != payer['member_name']]
        for i, member in enumerate(payees, 1):
            print(f"  {i}. {member['member_name']} - {format_currency(member['total_received'])}")
        
        payee_idx = int(input("\n📤 Payee number: ")) - 1
        if payee_idx < 0 or payee_idx >= len(payees):
            return "❌ Invalid payee selection"
        
        payee = payees[payee_idx]
        
        amount_str = input("💰 Amount: ").strip()
        amount = safe_int(amount_str)
        if amount <= 0:
            return "❌ Invalid amount"
        
        if not confirm_action(f"✅ Confirm payment of {format_currency(amount)} from {payer['member_name']} to {payee['member_name']}?"):
            return "❌ Cancelled"
        
        payer["total_contributions"] += amount
        save_member(payer, group_id)
        
        payee["total_received"] += amount
        save_member(payee, group_id)
        
        log_transaction(payer["member_name"], "PAYMENT_SENT", amount, None, group_id)
        log_transaction(payee["member_name"], "PAYMENT_RECEIVED", amount, None, group_id)
        
        return get_message("payment_success").format(
            amount=format_currency(amount),
            payer=payer['member_name'],
            payee=payee['member_name']
        )
    
    except ValueError:
        return "❌ Please enter valid numbers"

# ==================== GROUP MANAGEMENT ====================
def create_group(phone: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- CREATE GROUP ---")
    else:
        print("\n" + "="*40)
        print("        CREATE GROUP")
        print("="*40)
    
    group_id = input("🏷️  Group ID: ").strip()
    if not validate_group_id(group_id):
        return get_message("invalid_group")
    
    group_name = input("🏢 Group Name: ").strip()
    if not group_name:
        return get_message("required")
    
    if not confirm_action("✅ Confirm group creation?"):
        return "❌ Cancelled"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO groups (group_id, group_name, created_by) VALUES (?,?,?)",
                  (group_id, group_name, phone))
        conn.commit()
        
        c.execute("SELECT group_ids FROM users WHERE phone=?", (phone,))
        result = c.fetchone()
        if result:
            group_ids = json.loads(result[0])
            group_ids.append(group_id)
            c.execute("UPDATE users SET group_ids=? WHERE phone=?", (json.dumps(group_ids), phone))
            conn.commit()
            
            return f"✅ Group {group_name} ({group_id}) created!"
    except sqlite3.IntegrityError:
        return "❌ Group ID already exists"
    finally:
        conn.close()

def manage_groups(user: Dict[str, Any], device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MANAGE GROUPS ---")
    else:
        print("\n" + "="*40)
        print("        GROUP MANAGEMENT")
        print("="*40)
    
    print("1. 🆕 Create New Group")
    print("2. 🔄 Switch Group")
    print("3. 👥 View All Groups")
    choice = input("📥 Choose: ").strip()
    
    if choice == "1":
        return create_group(user["phone"], device_type)
    elif choice == "2":
        print("\n🏷️  Your Groups:")
        for i, gid in enumerate(user["group_ids"], 1):
            print(f"  {i}. {gid}")
        try:
            idx = int(input("📥 Select group number: ")) - 1
            if 0 <= idx < len(user["group_ids"]):
                user["current_group_id"] = user["group_ids"][idx]
                return f"✅ Switched to group {user['current_group_id']}"
            else:
                return "❌ Invalid selection"
        except ValueError:
            return "❌ Invalid input"
    elif choice == "3":
        print("\n🏷️  All Groups:")
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM groups")
        groups = [dict(row) for row in c.fetchall()]
        conn.close()
        
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['group_id']} - {group['group_name']}")
        return "✅ Groups displayed successfully"
    else:
        return "❌ Invalid choice"

# ==================== REPORTS & ANALYTICS ====================
def view_round_tracker(group_id: str, device_type: str) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- ROUND TRACKER ---")
    else:
        print("\n" + "="*40)
        print("        ROUND TRACKER")
        print("="*40)
    
    contribs = get_current_round_contributions(group_id)
    all_members = get_all_members(group_id)
    total_pot = sum(c["contributed"] for c in contribs)
    next_recipient = get_next_recipient(group_id)
    
    print(f"💰 Total Collected: {format_currency(total_pot)}")
    print(f"🎯 Next Recipient: {next_recipient or 'None'}")
    print("\n📊 Contributions:")
    
    for member in all_members:
        contributed = next((c["contributed"] for c in contribs if c["member_name"] == member["member_name"]), 0)
        status = "✅" if contributed > 0 else "❌"
        marker = " <-- NEXT" if member["member_name"] == next_recipient else ""
        print(f"  👤 {member['member_name']}: {format_currency(contributed)} {status}{marker}")
    
    not_contributed = [m["member_name"] for m in all_members if next((c["contributed"] for c in contribs if c["member_name"] == m["member_name"]), 0) == 0]
    
    if not_contributed:
        print(f"\n⏰ Pending: {', '.join(not_contributed)}")
    else:
        print("\n🎉 All members have contributed!")

def view_member_summary(group_id: str, device_type: str) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- MEMBER SUMMARY ---")
    else:
        print("\n" + "="*40)
        print("        MEMBER SUMMARY")
        print("="*40)
    
    members = get_all_members(group_id)
    if not members:
        print("❌ No members in group")
        return
    
    for member in members:
        print(f"\n👤 {member['member_name']}:")
        print(f"  💰 Contributions: {format_currency(member['total_contributions'])}")
        print(f"  📥 Received: {format_currency(member['total_received'])}")
        balance = member['total_received'] - member['total_contributions']
        status = "🟢" if balance >= 0 else "🔴"
        print(f"  ⚖️  Balance: {format_currency(balance)} {status}")

def view_transactions(group_id: str, device_type: str, member_name: Optional[str] = None) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- TRANSACTIONS ---")
    else:
        print("\n" + "="*40)
        print("        TRANSACTION HISTORY")
        print("="*40)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE group_id=? "
    params = [group_id]
    if member_name:
        query += "AND member_name=? "
        params.append(member_name)
    query += "ORDER BY timestamp DESC LIMIT 50"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("❌ No transactions found")
        return
    
    for row in rows:
        action_icon = {
            "CONTRIBUTION": "💰",
            "PAYMENT_SENT": "📤",
            "PAYMENT_RECEIVED": "📥",
            "ROUND_RECEIVED": "🎯"
        }.get(row['action'], "📝")
        
        print(f"{row['timestamp'][:16]} {action_icon} {row['member_name']} - {row['action']} {format_currency(row['amount'])}")

# ==================== REPORT EXPORT ====================
def export_transactions_to_csv(group_id: str) -> str:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
    SELECT * FROM transactions 
    WHERE group_id=? 
    ORDER BY timestamp DESC
    """, (group_id,))
    
    transactions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    if not transactions:
        return "❌ No transactions to export"
    
    filename = f"vicoba_transactions_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)
        return f"✅ Transactions exported to {filename}"
    except Exception as e:
        return f"❌ Export failed: {e}"

# ==================== NOTIFICATIONS ====================
def simulate_notifications(group_id: str, message: str) -> None:
    members = get_all_members(group_id)
    for member in members:
        phone = member.get("phone")
        if phone:
            print(f"📱 [SIMULATED SMS to {phone}]: {message}")

# ==================== MOBILE MONEY ====================
class MobileMoneyService:
    def __init__(self):
        self.provider = "M-Pesa"
    
    def process_payment(self, phone: str, amount: int, purpose: str = "VICOBA Contribution") -> Dict[str, str]:
        print(f"[MOBILE MONEY] Processing {format_currency(amount)} to {phone}")
        return {
            "status": "success",
            "transaction_id": f"MM{phone}{amount}",
            "message": f"Payment of {format_currency(amount)} processed successfully"
        }

mobile_money_service = MobileMoneyService()

# ==================== MAIN APPLICATION ====================
def main_app(user: Dict[str, Any], device_type: str) -> None:
    if "current_group_id" not in user:
        user["current_group_id"] = user["group_ids"][0] if user["group_ids"] else None
    
    group_id = user["current_group_id"]
    if not group_id:
        print("❌ No group assigned. Please manage groups.")
        return
    
    print(f"\n🎉 Welcome! Group: {group_id}")
    
    while True:
        show_menu("MAIN", device_type, user["role"])
        choice = input("📥 Choose: ").strip()
        
        if choice == "1" and user["role"] == "MEMBER":
            print(contribute(group_id, device_type))
        elif choice == "1" and user["role"] == "ADMIN":
            print(add_member(group_id, device_type))
        elif choice == "2":
            print(contribute(group_id, device_type))
        elif choice == "3":
            print(make_payment(group_id, device_type))
        elif choice == "4":
            view_round_tracker(group_id, device_type)
        elif choice == "5":
            view_member_summary(group_id, device_type)
        elif choice == "6" and user["role"] == "MEMBER":
            view_transactions(group_id, device_type)
        elif choice == "6" and user["role"] == "ADMIN":
            view_transactions(group_id, device_type)
        elif choice == "7" and user["role"] == "MEMBER":
            print(export_transactions_to_csv(group_id))
        elif choice == "7" and user["role"] == "ADMIN":
            result = manage_groups(user, device_type)
            print(result)
            group_id = user.get("current_group_id", group_id)
        elif choice == "8" and user["role"] == "ADMIN":
            print(export_transactions_to_csv(group_id))
        elif choice == "9" and user["role"] == "ADMIN":
            print("👋 Logging out...")
            break
        elif choice == "7" and user["role"] == "MEMBER":
            print("👋 Logging out...")
            break
        else:
            print("❌ Invalid choice")

def auth_flow(device_type: str) -> bool:
    while True:
        show_menu("AUTH", device_type)
        choice = input("📥 Choose: ").strip()
        
        if choice == "1":
            result = register_user(device_type)
            print(result)
        elif choice == "2":
            user = login_user(device_type)
            if user:
                print(get_message("login_success"))
                main_app(user, device_type)
            else:
                print(get_message("login_failed"))
        elif choice == "0":
            print("👋 Goodbye!")
            return True  # Exit program
        else:
            print("❌ Invalid choice")
    
    return False

# ==================== MAIN FUNCTION ====================
def main():
    try:
        print(f"\n🎉 {APP_NAME}")
        print("="*50)
        
        init_db()
        
        device_type = detect_device_type()
        print(f"📱 Detected device: {device_type}")
        
        if device_type == "FEATURE_PHONE":
            print("📟 USSD/SMS Mode")
        else:
            print("📱 Smartphone App Mode")
        print("="*50)
        
        exit_program = False
        while not exit_program:
            exit_program = auth_flow(device_type)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print("📞 Please contact support if this persists.")

# ==================== START APPLICATION ====================
if __name__ == "__main__":
    main()

# ==================== CONFIGURATION ====================
DB_FILE = "vicoba_unified.db"
APP_NAME = "VICOBA DIGITAL 2.0"
APP_VERSION = "2.0.0"

MESSAGES = {
    "en": {
        "invalid_pin": "PIN must be 4 digits",
        "invalid_phone": "Phone must be in format 255xxxxxxxxx",
        "invalid_name": "Name must be 3-50 characters, letters and spaces only",
        "invalid_group": "Group ID must be 3-20 alphanumeric characters",
        "required": "This field is required",
        "login_success": "Login successful!",
        "login_failed": "Invalid credentials",
        "registration_success": "Registration successful! Use PIN to login.",
        "phone_exists": "Phone already registered.",
        "member_exists": "Member already exists",
        "member_not_found": "Member not found",
        "round_completed": "🎉 Round completed! {recipient} received {amount}",
        "payment_success": "Payment of {amount} from {payer} to {payee} recorded!",
        "contribution_success": "Contribution of {amount} recorded for {name}"
    },
    "sw": {
        "invalid_pin": "PIN lazima iwe tarakimu 4",
        "invalid_phone": "Namba ya simu lazima iwe 255xxxxxxxxx",
        "invalid_name": "Jina lazima liwe herufi 3-50 pekee",
        "invalid_group": "Kitambulisho cha kikundi lazima kiwe herufi 3-20",
        "required": "Sehemu hii inahitajika",
        "login_success": "Umefanikiwa kuingia!",
        "login_failed": "Umekosea namba ya siri",
        "registration_success": "Usajili umefanikiwa! Tumia PIN kuingia.",
        "phone_exists": "Namba ya simu tayari imesajiliwa.",
        "member_exists": "Mwanachama tayari yupo.",
        "member_not_failed": "Mwanachama hajapatikana"
    }
}

VALIDATION_PATTERNS = {
    "phone": r'^255\d{9}$',
    "name": r'^[\w\s]{3,50}$',
    "group_id": r'^[\w]{3,20}$',
    "pin": r'^\d{4}$'
}

# ==================== UTILITY FUNCTIONS ====================
def safe_int(value: Optional[str]) -> int:
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def generate_salt() -> str:
    return os.urandom(16).hex()

def hash_pin(pin: str, salt: str) -> str:
    return hashlib.sha256((pin + salt).encode()).hexdigest()

def format_currency(amount: int) -> str:
    return f"Tsh {amount:,}"

def validate_phone(phone: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['phone'], phone))

def validate_name(name: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['name'], name))

def validate_pin(pin: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['pin'], pin))

def validate_group_id(group_id: str) -> bool:
    return bool(re.match(VALIDATION_PATTERNS['group_id'], group_id))

def confirm_action(message: str) -> bool:
    response = input(f"{message} (Y/N): ").strip().upper()
    return response == 'Y'

def get_message(key: str, language: str = "en") -> str:
    return MESSAGES.get(language, {}).get(key, key)

# ==================== UI FUNCTIONS ====================
def detect_device_type() -> str:
    if hasattr(sys, 'getandroidapilevel'):
        return "SMARTPHONE"
    elif sys.platform == 'darwin':
        return "SMARTPHONE"
    else:
        return "FEATURE_PHONE"

def detect_phone_number() -> str:
    return "255123456789"

def show_menu(menu_type: str, device_type: str, role: str = 'MEMBER') -> None:
    menu_options = {
        "AUTH": ["1. Register", "2. Login", "0. Exit"],
        "MAIN_MEMBER": [
            "1. Make Contribution", 
            "2. Make Payment", 
            "3. View Round Tracker", 
            "4. View Member Summary", 
            "5. View Transactions", 
            "6. Export Report",
            "7. Logout"
        ],
        "MAIN_ADMIN": [
            "1. Add Member", 
            "2. Make Contribution", 
            "3. Make Payment", 
            "4. View Round Tracker", 
            "5. View Member Summary", 
            "6. View Transactions", 
            "7. Manage Groups", 
            "8. Export Report",
            "9. Logout"
        ]
    }

    if menu_type == "AUTH":
        menu_items = menu_options["AUTH"]
        title = "VICOBA DIGITAL 2.0"
    elif menu_type == "MAIN":
        menu_items = menu_options["MAIN_ADMIN"] if role == 'ADMIN' else menu_options["MAIN_MEMBER"]
        title = "MAIN MENU"
    else:
        menu_items = []
        title = "MENU"

    if device_type == "FEATURE_PHONE":
        print(f"\n{title}")
        for item in menu_items:
            print(item)
    else:
        print("\n" + "="*40)
        print(f"    {title}")
        print("="*40)
        for item in menu_items:
            print(item)
        print("="*40)

# ==================== DATABASE FUNCTIONS ====================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        phone TEXT PRIMARY KEY,
        pin_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        group_ids TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'MEMBER',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Members table
    c.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_name TEXT,
        phone TEXT,
        total_contributions INTEGER NOT NULL DEFAULT 0,
        total_received INTEGER NOT NULL DEFAULT 0,
        group_id TEXT NOT NULL,
        PRIMARY KEY (member_name, group_id)
    )
    """)
    
    # Rounds table
    c.execute("""
    CREATE TABLE IF NOT EXISTS rounds (
        round_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_receiving TEXT,
        total_amount INTEGER,
        round_date TEXT,
        group_id TEXT NOT NULL
    )
    """)
    
    # Transactions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT,
        action TEXT,
        amount INTEGER,
        timestamp TEXT,
        round_id INTEGER,
        group_id TEXT NOT NULL
    )
    """)
    
    # Groups table
    c.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        group_name TEXT NOT NULL,
        created_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create default admin user
    c.execute("SELECT * FROM users WHERE phone=?", ("255123456789",))
    if not c.fetchone():
        salt = generate_salt()
        pin_hash = hash_pin("1234", salt)
        c.execute(
            "INSERT INTO users (phone, pin_hash, salt, group_ids, role) VALUES (?,?,?,?,?)",
            ("255123456789", pin_hash, salt, json.dumps(["TEST_GROUP"]), 'ADMIN'))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ==================== AUTHENTICATION FUNCTIONS ====================
def register_user(device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- REGISTER ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED REGISTRATION")
        print("="*40)
    
    phone = detect_phone_number()
    if not phone:
        phone = input("Enter phone (255xxxxxxx): ").strip()
    
    if not validate_phone(phone):
        return get_message("invalid_phone")
    
    print(f"📱 Detected phone: {phone}")
    pin = input("🔐 Create 4-digit PIN: ").strip()
    if not validate_pin(pin):
        return get_message("invalid_pin")
    
    group_id = input("🏷️  Group ID: ").strip()
    if not validate_group_id(group_id):
        return get_message("invalid_group")
    
    role = input("👤 Role (ADMIN/MEMBER): ").strip().upper() or 'MEMBER'
    if role not in ['ADMIN', 'MEMBER']:
        return "Invalid role"
    
    if not confirm_action("✅ Confirm registration?"):
        return "Registration cancelled"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM users WHERE phone=?", (phone,))
        if c.fetchone():
            return get_message("phone_exists")
        
        salt = generate_salt()
        pin_hash = hash_pin(pin, salt)
        c.execute(
            "INSERT INTO users (phone, pin_hash, salt, group_ids, role) VALUES (?,?,?,?,?)",
            (phone, pin_hash, salt, json.dumps([group_id]), role)
        )
        conn.commit()
        return get_message("registration_success")
    except sqlite3.IntegrityError:
        return get_message("phone_exists")
    finally:
        conn.close()

def login_user(device_type: str) -> Optional[Dict[str, Any]]:
    if device_type == "FEATURE_PHONE":
        print("\n--- LOGIN ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED LOGIN")
        print("="*40)
    
    phone = detect_phone_number()
    if not phone:
        phone = input("Enter phone (255xxxxxxx): ").strip()
    
    if not validate_phone(phone):
        return None
    
    print(f"📱 Detected phone: {phone}")
    pin = input("🔐 Enter PIN: ").strip()
    if not validate_pin(pin):
        return None
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE phone=?", (phone,))
    user = c.fetchone()
    conn.close()
    
    if user:
        stored_hash = user['pin_hash']
        salt = user['salt']
        role = user['role']
        group_ids = json.loads(user['group_ids'])
        if hash_pin(pin, salt) == stored_hash:
            return {
                "phone": phone,
                "group_ids": group_ids,
                "role": role
            }
    
    return None

# ==================== MEMBER MANAGEMENT ====================
def get_member(name: str, group_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM members WHERE member_name=? AND group_id=?", (name, group_id))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_all_members(group_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM members WHERE group_id=? ORDER BY member_name", (group_id,))
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def save_member(member_data: Dict[str, Any], group_id: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("""
        INSERT OR REPLACE INTO members VALUES (?,?,?,?,?)
        """, (
            member_data["member_name"],
            member_data.get("phone", ""),
            safe_int(member_data["total_contributions"]),
            safe_int(member_data["total_received"]),
            group_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error saving member: {e}")
        return False
    finally:
        conn.close()

def add_member(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- ADD MEMBER ---")
    else:
        print("\n" + "="*40)
        print("        ADD NEW MEMBER")
        print("="*40)
    
    name = input("👤 Member name: ").strip()
    if not validate_name(name):
        return get_message("invalid_name")
    
    if get_member(name, group_id):
        return get_message("member_exists")
    
    phone = input("📱 Phone (optional): ").strip()
    if phone and not validate_phone(phone):
        return get_message("invalid_phone")
    
    if not confirm_action("✅ Confirm adding member?"):
        return "Cancelled"
    
    save_member({
        "member_name": name,
        "phone": phone,
        "total_contributions": 0,
        "total_received": 0
    }, group_id)
    
    return f"✅ Member {name} added successfully!"

# ==================== CONTRIBUTION SYSTEM ====================
def log_transaction(member_name: str, action: str, amount: int, 
                   round_id: Optional[int], group_id: str) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO transactions VALUES (NULL,?,?,?,?,?,?)",
            (member_name, action, amount, datetime.now().isoformat(), round_id, group_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error logging transaction: {e}")
        return False
    finally:
        conn.close()

def contribute(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MAKE CONTRIBUTION ---")
    else:
        print("\n" + "="*40)
        print("        MAKE CONTRIBUTION")
        print("="*40)
    
    name = input("👤 Member name: ").strip()
    if not validate_name(name):
        return get_message("invalid_name")
    
    amount_str = input("💰 Amount: ").strip()
    amount = safe_int(amount_str)
    if amount <= 0:
        return "❌ Invalid amount"
    
    member = get_member(name, group_id)
    if not member:
        return get_message("member_not_found")
    
    if not confirm_action(f"✅ Confirm contribution of {format_currency(amount)}?"):
        return "❌ Cancelled"
    
    member["total_contributions"] += amount
    save_member(member, group_id)
    
    log_transaction(name, "CONTRIBUTION", amount, None, group_id)
    
    return get_message("contribution_success").format(
        amount=format_currency(amount),
        name=name
    )

# ==================== ROUND MANAGEMENT ====================
def create_round(member_receiving: str, total_amount: int, group_id: str) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    
    round_date = datetime.now().isoformat()
    c.execute(
        "INSERT INTO rounds VALUES (NULL,?,?,?,?)", 
        (member_receiving, total_amount, round_date, group_id)
    )
    round_id = c.lastrowid
    conn.commit()
    conn.close()
    
    member = get_member(member_receiving, group_id)
    if member:
        member["total_received"] += total_amount
        save_member(member, group_id)
    
    log_transaction(member_receiving, "ROUND_RECEIVED", total_amount, round_id, group_id)
    return round_id

def get_current_round_contributions(group_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT round_id FROM rounds WHERE group_id=? ORDER BY round_id DESC LIMIT 1", (group_id,))
    latest_round = c.fetchone()
    latest_id = latest_round['round_id'] if latest_round else 0
    
    c.execute("""
        SELECT member_name, SUM(amount) AS contributed
        FROM transactions 
        WHERE action='CONTRIBUTION' AND group_id=? AND (round_id IS NULL OR round_id > ?)
        GROUP BY member_name
    """, (group_id, latest_id))
    
    contribs = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return contribs

def get_next_recipient(group_id: str) -> Optional[str]:
    members = get_all_members(group_id)
    if not members:
        return None
    
    min_received = min(m["total_received"] for m in members)
    candidates = [m["member_name"] for m in members if m["total_received"] == min_received]
    return sorted(candidates)[0] if candidates else None

def auto_finalize_round(group_id: str) -> bool:
    contribs = get_current_round_contributions(group_id)
    all_members = get_all_members(group_id)
    
    if len(contribs) == len(all_members) and all(c["contributed"] > 0 for c in contribs):
        total_amount = sum(c["contributed"] for c in contribs)
        next_recipient = get_next_recipient(group_id)
        
        if next_recipient and total_amount > 0:
            round_id = create_round(next_recipient, total_amount, group_id)
            
            conn = get_db_connection()
            c = conn.cursor()
            
            for contrib in contribs:
                c.execute("""
                    UPDATE transactions 
                    SET round_id=? 
                    WHERE member_name=? AND action='CONTRIBUTION' AND round_id IS NULL AND group_id=?
                """, (round_id, contrib["member_name"], group_id))
            conn.commit()
            conn.close()
            
            return True
    
    return False

# ==================== PAYMENT SYSTEM ====================
def make_payment(group_id: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MEMBER PAYMENT ---")
    else:
        print("\n" + "="*40)
        print("        ENHANCED PAYMENT")
        print("="*40)
    
    members = get_all_members(group_id)
    if len(members) < 2:
        return "❌ Need at least 2 members for payments"
    
    print("\n👤 Select payer:")
    for i, member in enumerate(members, 1):
        print(f"  {i}. {member['member_name']} - {format_currency(member['total_contributions'])}")
    
    try:
        payer_idx = int(input("\n📥 Payer number: ")) - 1
        if payer_idx < 0 or payer_idx >= len(members):
            return "❌ Invalid payer selection"
        
        payer = members[payer_idx]
        
        print("\n👤 Select payee:")
        payees = [m for m in members if m['member_name'] != payer['member_name']]
        for i, member in enumerate(payees, 1):
            print(f"  {i}. {member['member_name']} - {format_currency(member['total_received'])}")
        
        payee_idx = int(input("\n📤 Payee number: ")) - 1
        if payee_idx < 0 or payee_idx >= len(payees):
            return "❌ Invalid payee selection"
        
        payee = payees[payee_idx]
        
        amount_str = input("💰 Amount: ").strip()
        amount = safe_int(amount_str)
        if amount <= 0:
            return "❌ Invalid amount"
        
        if not confirm_action(f"✅ Confirm payment of {format_currency(amount)} from {payer['member_name']} to {payee['member_name']}?"):
            return "❌ Cancelled"
        
        payer["total_contributions"] += amount
        save_member(payer, group_id)
        
        payee["total_received"] += amount
        save_member(payee, group_id)
        
        log_transaction(payer["member_name"], "PAYMENT_SENT", amount, None, group_id)
        log_transaction(payee["member_name"], "PAYMENT_RECEIVED", amount, None, group_id)
        
        return get_message("payment_success").format(
            amount=format_currency(amount),
            payer=payer['member_name'],
            payee=payee['member_name']
        )
    
    except ValueError:
        return "❌ Please enter valid numbers"

# ==================== GROUP MANAGEMENT ====================
def create_group(phone: str, device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- CREATE GROUP ---")
    else:
        print("\n" + "="*40)
        print("        CREATE GROUP")
        print("="*40)
    
    group_id = input("🏷️  Group ID: ").strip()
    if not validate_group_id(group_id):
        return get_message("invalid_group")
    
    group_name = input("🏢 Group Name: ").strip()
    if not group_name:
        return get_message("required")
    
    if not confirm_action("✅ Confirm group creation?"):
        return "❌ Cancelled"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO groups (group_id, group_name, created_by) VALUES (?,?,?)",
                  (group_id, group_name, phone))
        conn.commit()
        
        c.execute("SELECT group_ids FROM users WHERE phone=?", (phone,))
        result = c.fetchone()
        if result:
            group_ids = json.loads(result[0])
            group_ids.append(group_id)
            c.execute("UPDATE users SET group_ids=? WHERE phone=?", (json.dumps(group_ids), phone))
            conn.commit()
            
            return f"✅ Group {group_name} ({group_id}) created!"
    except sqlite3.IntegrityError:
        return "❌ Group ID already exists"
    finally:
        conn.close()

def manage_groups(user: Dict[str, Any], device_type: str) -> str:
    if device_type == "FEATURE_PHONE":
        print("\n--- MANAGE GROUPS ---")
    else:
        print("\n" + "="*40)
        print("        GROUP MANAGEMENT")
        print("="*40)
    
    print("1. 🆕 Create New Group")
    print("2. 🔄 Switch Group")
    print("3. 👥 View All Groups")
    choice = input("📥 Choose: ").strip()
    
    if choice == "1":
        return create_group(user["phone"], device_type)
    elif choice == "2":
        print("\n🏷️  Your Groups:")
        for i, gid in enumerate(user["group_ids"], 1):
            print(f"  {i}. {gid}")
        try:
            idx = int(input("📥 Select group number: ")) - 1
            if 0 <= idx < len(user["group_ids"]):
                user["current_group_id"] = user["group_ids"][idx]
                return f"✅ Switched to group {user['current_group_id']}"
            else:
                return "❌ Invalid selection"
        except ValueError:
            return "❌ Invalid input"
    elif choice == "3":
        print("\n🏷️  All Groups:")
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM groups")
        groups = [dict(row) for row in c.fetchall()]
        conn.close()
        
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group['group_id']} - {group['group_name']}")
        return "✅ Groups displayed successfully"
    else:
        return "❌ Invalid choice"

# ==================== REPORTS & ANALYTICS ====================
def view_round_tracker(group_id: str, device_type: str) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- ROUND TRACKER ---")
    else:
        print("\n" + "="*40)
        print("        ROUND TRACKER")
        print("="*40)
    
    contribs = get_current_round_contributions(group_id)
    all_members = get_all_members(group_id)
    total_pot = sum(c["contributed"] for c in contribs)
    next_recipient = get_next_recipient(group_id)
    
    print(f"💰 Total Collected: {format_currency(total_pot)}")
    print(f"🎯 Next Recipient: {next_recipient or 'None'}")
    print("\n📊 Contributions:")
    
    for member in all_members:
        contributed = next((c["contributed"] for c in contribs if c["member_name"] == member["member_name"]), 0)
        status = "✅" if contributed > 0 else "❌"
        marker = " <-- NEXT" if member["member_name"] == next_recipient else ""
        print(f"  👤 {member['member_name']}: {format_currency(contributed)} {status}{marker}")
    
    not_contributed = [m["member_name"] for m in all_members if next((c["contributed"] for c in contribs if c["member_name"] == m["member_name"]), 0) == 0]
    
    if not_contributed:
        print(f"\n⏰ Pending: {', '.join(not_contributed)}")
    else:
        print("\n🎉 All members have contributed!")

def view_member_summary(group_id: str, device_type: str) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- MEMBER SUMMARY ---")
    else:
        print("\n" + "="*40)
        print("        MEMBER SUMMARY")
        print("="*40)
    
    members = get_all_members(group_id)
    if not members:
        print("❌ No members in group")
        return
    
    for member in members:
        print(f"\n👤 {member['member_name']}:")
        print(f"  💰 Contributions: {format_currency(member['total_contributions'])}")
        print(f"  📥 Received: {format_currency(member['total_received'])}")
        balance = member['total_received'] - member['total_contributions']
        status = "🟢" if balance >= 0 else "🔴"
        print(f"  ⚖️  Balance: {format_currency(balance)} {status}")

def view_transactions(group_id: str, device_type: str, member_name: Optional[str] = None) -> None:
    if device_type == "FEATURE_PHONE":
        print("\n--- TRANSACTIONS ---")
    else:
        print("\n" + "="*40)
        print("        TRANSACTION HISTORY")
        print("="*40)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE group_id=? "
    params = [group_id]
    if member_name:
        query += "AND member_name=? "
        params.append(member_name)
    query += "ORDER BY timestamp DESC LIMIT 50"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("❌ No transactions found")
        return
    
    for row in rows:
        action_icon = {
            "CONTRIBUTION": "💰",
            "PAYMENT_SENT": "📤",
            "PAYMENT_RECEIVED": "📥",
            "ROUND_RECEIVED": "🎯"
        }.get(row['action'], "📝")
        
        print(f"{row['timestamp'][:16]} {action_icon} {row['member_name']} - {row['action']} {format_currency(row['amount'])}")

# ==================== REPORT EXPORT ====================
def export_transactions_to_csv(group_id: str) -> str:
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
    SELECT * FROM transactions 
    WHERE group_id=? 
    ORDER BY timestamp DESC
    """, (group_id,))
    
    transactions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    if not transactions:
        return "❌ No transactions to export"
    
    filename = f"vicoba_transactions_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)
        return f"✅ Transactions exported to {filename}"
    except Exception as e:
        return f"❌ Export failed: {e}"

# ==================== NOTIFICATIONS ====================
def simulate_notifications(group_id: str, message: str) -> None:
    members = get_all_members(group_id)
    for member in members:
        phone = member.get("phone")
        if phone:
            print(f"📱 [SIMULATED SMS to {phone}]: {message}")

# ==================== MOBILE MONEY ====================
class MobileMoneyService:
    def __init__(self):
        self.provider = "M-Pesa"
    
    def process_payment(self, phone: str, amount: int, purpose: str = "VICOBA Contribution") -> Dict[str, str]:
        print(f"[MOBILE MONEY] Processing {format_currency(amount)} to {phone}")
        return {
            "status": "success",
            "transaction_id": f"MM{phone}{amount}",
            "message": f"Payment of {format_currency(amount)} processed successfully"
        }

mobile_money_service = MobileMoneyService()

# ==================== MAIN APPLICATION ====================
def main_app(user: Dict[str, Any], device_type: str) -> None:
    if "current_group_id" not in user:
        user["current_group_id"] = user["group_ids"][0] if user["group_ids"] else None
    
    group_id = user["current_group_id"]
    if not group_id:
        print("❌ No group assigned. Please manage groups.")
        return
    
    print(f"\n🎉 Welcome! Group: {group_id}")
    
    while True:
        show_menu("MAIN", device_type, user["role"])
        choice = input("📥 Choose: ").strip()
        
        if choice == "1" and user["role"] == "MEMBER":
            print(contribute(group_id, device_type))
        elif choice == "1" and user["role"] == "ADMIN":
            print(add_member(group_id, device_type))
        elif choice == "2":
            print(contribute(group_id, device_type))
        elif choice == "3":
            print(make_payment(group_id, device_type))
        elif choice == "4":
            view_round_tracker(group_id, device_type)
        elif choice == "5":
            view_member_summary(group_id, device_type)
        elif choice == "6" and user["role"] == "MEMBER":
            view_transactions(group_id, device_type)
        elif choice == "6" and user["role"] == "ADMIN":
            view_transactions(group_id, device_type)
        elif choice == "7" and user["role"] == "MEMBER":
            print(export_transactions_to_csv(group_id))
        elif choice == "7" and user["role"] == "ADMIN":
            result = manage_groups(user, device_type)
            print(result)
            group_id = user.get("current_group_id", group_id)
        elif choice == "8" and user["role"] == "ADMIN":
            print(export_transactions_to_csv(group_id))
        elif choice == "9" and user["role"] == "ADMIN":
            print("👋 Logging out...")
            break
        elif choice == "7" and user["role"] == "MEMBER":
            print("👋 Logging out...")
            break
        else:
            print("❌ Invalid choice")

def auth_flow(device_type: str) -> bool:
    while True:
        show_menu("AUTH", device_type)
        choice = input("📥 Choose: ").strip()
        
        if choice == "1":
            result = register_user(device_type)
            print(result)
        elif choice == "2":
            user = login_user(device_type)
            if user:
                print(get_message("login_success"))
                main_app(user, device_type)
            else:
                print(get_message("login_failed"))
        elif choice == "0":
            print("👋 Goodbye!")
            return True  # Exit program
        else:
            print("❌ Invalid choice")
    
    return False

# ==================== MAIN FUNCTION ====================
def main():
    try:
        print(f"\n🎉 {APP_NAME}")
        print("="*50)
        
        init_db()
        
        device_type = detect_device_type()
        print(f"📱 Detected device: {device_type}")
        
        if device_type == "FEATURE_PHONE":
            print("📟 USSD/SMS Mode")
        else:
            print("📱 Smartphone App Mode")
        print("="*50)
        
        exit_program = False
        while not exit_program:
            exit_program = auth_flow(device_type)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print("📞 Please contact support if this persists.")

# ==================== START APPLICATION ====================
if __name__ == "__main__":
    main()

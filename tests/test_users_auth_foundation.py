import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

# Set a secure test-only JWT_SECRET in environment before importing config
TEST_JWT_SECRET = "test-secret-key-that-is-at-least-32-chars-long-for-tests"
if os.environ.get("JWT_SECRET") in (None, "", "change-this-to-a-secure-random-secret-in-production", "dev-secret-key-placeholder-change-in-production"):
    os.environ["JWT_SECRET"] = TEST_JWT_SECRET

from app.config import DB_PATH
from app.database import init_db, seed_demo_users
from app.services.password_service import hash_password, verify_password


def run_tests():
    print("Running PLACEMENTIQ Pass 2A: Users Table and Demo Credential Foundation Test Suite...\n")

    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Test 1: users table exists
    print("Test 1: Testing users table existence...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert cursor.fetchone() is not None, "Users table does not exist in SQLite database"
    print("[PASS] Test 1: users table exists.")

    # Test 2: required columns exist
    print("Test 2: Testing required columns in users table...")
    cursor.execute("PRAGMA table_info(users)")
    cols = {row[1]: row[2] for row in cursor.fetchall()}
    required_cols = ["id", "email", "password_hash", "role", "student_id", "is_active", "created_at", "updated_at"]
    for col in required_cols:
        assert col in cols, f"Required column '{col}' missing from users table"
    print(f"[PASS] Test 2: All required columns present: {list(cols.keys())}.")

    # Test 3: email uniqueness
    print("Test 3: Testing email uniqueness enforcement...")
    test_email = "uniqueness_test@placementiq.demo"
    cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()

    pwd_hash = hash_password("testpass123")
    cursor.execute(
        "INSERT INTO users (email, password_hash, role, student_id, is_active) VALUES (?, ?, ?, ?, 1)",
        (test_email, pwd_hash, "student", "ST_DEMO_001")
    )
    conn.commit()

    duplicate_error = False
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash, role, student_id, is_active) VALUES (?, ?, ?, ?, 1)",
            (test_email, pwd_hash, "student", "ST_DEMO_002")
        )
        conn.commit()
    except sqlite3.IntegrityError:
        duplicate_error = True
    finally:
        cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()

    assert duplicate_error is True, "Database failed to enforce unique email constraint on users table"
    print("[PASS] Test 3: Email uniqueness strictly enforced via UNIQUE constraint.")

    # Test 4: password hashing
    print("Test 4: Testing password hashing...")
    sample_pwd = "mySecurePassword!9"
    hashed = hash_password(sample_pwd)
    assert hashed != sample_pwd, "Password hash must not match plaintext"
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$"), f"Expected bcrypt hash format, got {hashed[:5]}"
    print("[PASS] Test 4: Password hashing produces valid bcrypt salted hash.")

    # Test 5: correct password verification
    print("Test 5: Testing correct password verification...")
    assert verify_password(sample_pwd, hashed) is True, "Valid password verification failed"
    print("[PASS] Test 5: Correct password verified successfully.")

    # Test 6: incorrect password verification failure
    print("Test 6: Testing incorrect password verification failure...")
    assert verify_password("WrongPassword", hashed) is False, "Incorrect password unexpectedly verified as True"
    assert verify_password("", hashed) is False, "Empty password unexpectedly verified as True"
    assert verify_password(None, hashed) is False, "None password unexpectedly verified as True"
    print("[PASS] Test 6: Incorrect passwords securely rejected.")

    # Test 7: demo user seeding
    print("Test 7: Testing demo user seeding...")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count_before = cursor.fetchone()[0]
    assert user_count_before >= 15, f"Expected at least 15 seeded users, found {user_count_before}"
    print(f"[PASS] Test 7: Demo users seeded successfully (Total users: {user_count_before}).")

    # Test 8: idempotent seeding
    print("Test 8: Testing seeding idempotency...")
    seed_demo_users(cursor)
    conn.commit()
    seed_demo_users(cursor)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count_after = cursor.fetchone()[0]
    assert user_count_before == user_count_after, f"Seeding created duplicate records: before={user_count_before}, after={user_count_after}"
    print(f"[PASS] Test 8: Seeding is 100% idempotent (User count unchanged: {user_count_after}).")

    # Test 9: student users reference student IDs
    print("Test 9: Testing student users reference student IDs...")
    demo_expected = {
        "ananya@placementiq.demo": "ST_DEMO_001",
        "rahul@placementiq.demo": "ST_DEMO_002",
        "priya@placementiq.demo": "ST_DEMO_003",
        "sneha@placementiq.demo": "ST_DEMO_004",
        "arjun@placementiq.demo": "ST_DEMO_005",
        "meera@placementiq.demo": "ST_DEMO_006",
        "karan@placementiq.demo": "ST_DEMO_007",
        "divya@placementiq.demo": "ST_DEMO_008",
        "rohan@placementiq.demo": "ST_DEMO_009",
        "nisha@placementiq.demo": "ST_DEMO_010",
        "vivek@placementiq.demo": "ST_DEMO_011",
        "pooja@placementiq.demo": "ST_DEMO_012",
        "aditya@placementiq.demo": "ST_DEMO_013",
    }
    for email, sid in demo_expected.items():
        cursor.execute("SELECT student_id, role, password_hash, is_active FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        assert row is not None, f"Seeded user for {email} not found"
        assert row[0] == sid, f"Expected student_id {sid} for {email}, got {row[0]}"
        assert row[1] == "student", f"Expected role 'student' for {email}, got {row[1]}"
        assert row[3] == 1, f"Expected is_active=1 for {email}"
        assert verify_password("demo123", row[2]) is True, f"Demo password verification failed for {email}"
    print("[PASS] Test 9: All 13 demo student personas correctly reference their student IDs and credentials.")

    # Test 10 and 11: TPO user role and nullable student_id
    print("Test 10 and 11: Testing TPO/RPO accounts, role, and nullable student_id...")
    for tpo_email in ["tpo@placementiq.demo", "rpo@placementiq.demo"]:
        cursor.execute("SELECT student_id, role, password_hash, is_active FROM users WHERE email = ?", (tpo_email,))
        tpo_row = cursor.fetchone()
        assert tpo_row is not None, f"TPO user {tpo_email} not found"
        assert tpo_row[1] == "tpo", f"Expected role 'tpo' for {tpo_email}, got {tpo_row[1]}"
        assert tpo_row[0] is None, f"Expected student_id to be NULL for {tpo_email}, got {tpo_row[0]}"
        assert verify_password("tpo123", tpo_row[2]) is True, f"TPO password verification failed for {tpo_email}"
    print("[PASS] Test 10 and 11: TPO/RPO accounts have role tpo, student_id=NULL, and correct password hash.")

    # Test 12: 610 student records intact
    print("Test 12: Testing 610 student dataset preservation...")
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    assert student_count == 610, f"Expected 610 students in students table, got {student_count}"
    print(f"[PASS] Test 12: All {student_count} student records remain intact.")

    conn.close()

    print("\n=======================================================")
    print("ALL 12 PASS 2A AUTH FOUNDATION TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()

import os
import sys
import time
import jwt
import sqlite3
import unittest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.main import app
from app.config import settings, DB_PATH
from app.services.auth_service import create_access_token, decode_access_token

client = TestClient(app)


class TestAuthJWT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email IN ('newstudent@example.com', 'inactive@placementiq.demo')")
        cursor.execute("DELETE FROM students WHERE email IN ('newstudent@example.com')")
        cursor.execute("""
            INSERT INTO users (email, password_hash, role, student_id, is_active)
            VALUES ('inactive@placementiq.demo', '$2b$12$eXampleHashedPasswordForTestOnly999', 'student', NULL, 0)
        """)
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email IN ('newstudent@example.com', 'inactive@placementiq.demo')")
        cursor.execute("DELETE FROM students WHERE email IN ('newstudent@example.com')")
        conn.commit()
        conn.close()

    def test_01_public_endpoints_accessible(self):
        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json()["platform"], "PLACEMENTIQ")

        res_health = client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "healthy")

        res_info = client.get("/api/model-info")
        self.assertEqual(res_info.status_code, 200)
        self.assertIn("model_governance", res_info.json())

    def test_02_student_login_success(self):
        res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["authenticated"])
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["role"], "student")
        self.assertEqual(data["user"]["email"], "student@placementiq.demo")
        self.assertEqual(data["user"]["student_id"], "ST_DEMO_001")
        self.assertNotIn("password_hash", data["user"])

        res_demo = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "demo123"
        })
        self.assertEqual(res_demo.status_code, 200)

    def test_03_tpo_login_success(self):
        res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["authenticated"])
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "tpo")
        self.assertEqual(data["user"]["email"], "tpo@placementiq.demo")
        self.assertNotIn("password_hash", data["user"])

    def test_04_login_wrong_password_fails(self):
        res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "wrongpassword123"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid email or password", res.json()["detail"])

    def test_05_login_nonexistent_user_fails(self):
        res = client.post("/api/auth/login", json={
            "email": "unknown_ghost_user@domain.com",
            "password": "somepassword"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid email or password", res.json()["detail"])

    def test_06_login_inactive_user_fails(self):
        res = client.post("/api/auth/login", json={
            "email": "inactive@placementiq.demo",
            "password": "any"
        })
        self.assertEqual(res.status_code, 401)

    def test_07_auth_me_endpoint_student(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        user = me_res.json()["user"]
        self.assertEqual(user["email"], "student@placementiq.demo")
        self.assertEqual(user["role"], "student")
        self.assertEqual(user["student_id"], "ST_DEMO_001")

    def test_08_auth_me_endpoint_tpo(self):
        login_res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        token = login_res.json()["access_token"]

        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        user = me_res.json()["user"]
        self.assertEqual(user["email"], "tpo@placementiq.demo")
        self.assertEqual(user["role"], "tpo")

    def test_09_auth_me_unauthorized_cases(self):
        res_none = client.get("/api/auth/me")
        self.assertEqual(res_none.status_code, 401)

        res_malformed = client.get("/api/auth/me", headers={"Authorization": "InvalidTokenWithoutBearer"})
        self.assertEqual(res_malformed.status_code, 401)

        fake_token = jwt.encode({"sub": 1, "exp": int(time.time()) + 3600}, "wrong_secret", algorithm="HS256")
        res_invalid = client.get("/api/auth/me", headers={"Authorization": f"Bearer {fake_token}"})
        self.assertEqual(res_invalid.status_code, 401)

        expired_token = jwt.encode({"sub": 1, "exp": int(time.time()) - 3600}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        res_expired = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        self.assertEqual(res_expired.status_code, 401)

    def test_10_student_can_access_own_detail(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/students/ST_DEMO_001", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["student"]["student_id"], "ST_DEMO_001")

    def test_11_student_cannot_access_other_student_detail(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/students/ST_DEMO_002", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 403)
        self.assertIn("Access denied", res.json()["detail"])

    def test_12_tpo_can_access_any_student_detail(self):
        login_res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        token = login_res.json()["access_token"]

        res1 = client.get("/api/students/ST_DEMO_001", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res1.status_code, 200)

        res2 = client.get("/api/students/ST_DEMO_002", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res2.status_code, 200)

    def test_13_student_forbidden_from_student_directory(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/students", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 403)
        self.assertIn("TPO", res.json()["detail"])

    def test_14_tpo_can_access_student_directory(self):
        login_res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/students", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 610)

    def test_15_student_forbidden_from_tpo_overview(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/tpo/overview", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 403)

    def test_16_tpo_can_access_tpo_overview(self):
        login_res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        token = login_res.json()["access_token"]

        res = client.get("/api/tpo/overview", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_students"], 610)

    def test_17_student_forbidden_from_flight_simulator(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        res = client.post("/api/simulator/run", json={
            "target_role": "Software Development Engineer",
            "department": "ALL"
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 403)

    def test_18_tpo_can_access_flight_simulator(self):
        login_res = client.post("/api/auth/login", json={
            "email": "tpo@placementiq.demo",
            "password": "tpo123"
        })
        token = login_res.json()["access_token"]

        res = client.post("/api/simulator/run", json={
            "target_role": "Software Development Engineer",
            "department": "ALL"
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_cohort"], 610)

    def test_19_student_prediction_endpoints_ownership(self):
        login_res = client.post("/api/auth/login", json={
            "email": "student@placementiq.demo",
            "password": "student123"
        })
        token = login_res.json()["access_token"]

        # 1. Access own roadmap -> 200
        res_own = client.get("/api/roadmap/ST_DEMO_001", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_own.status_code, 200)

        # 2. Access other student roadmap -> 403
        res_other = client.get("/api/roadmap/ST_DEMO_002", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_other.status_code, 403)

        # 3. Access own opportunity-cost -> 200
        res_opp_own = client.get("/api/opportunity-cost/ST_DEMO_001", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_opp_own.status_code, 200)

        # 4. Access other student opportunity-cost -> 403
        res_opp_other = client.get("/api/opportunity-cost/ST_DEMO_002", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_opp_other.status_code, 403)

    def test_20_user_registration_lifecycle(self):
        reg_res = client.post("/api/auth/register", json={
            "email": "newstudent@example.com",
            "password": "securepassword123",
            "name": "New Student",
            "department": "CSE",
            "target_role": "Full Stack Developer"
        })
        self.assertEqual(reg_res.status_code, 201)
        reg_data = reg_res.json()
        self.assertIn("registered successfully", reg_data["message"])
        self.assertEqual(reg_data["user"]["email"], "newstudent@example.com")
        self.assertNotIn("password_hash", reg_data["user"])

        dup_res = client.post("/api/auth/register", json={
            "email": "newstudent@example.com",
            "password": "anotherpassword",
            "name": "Duplicate User"
        })
        self.assertEqual(dup_res.status_code, 409)
        self.assertIn("already exists", dup_res.json()["detail"])

        login_res = client.post("/api/auth/login", json={
            "email": "newstudent@example.com",
            "password": "securepassword123"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        self.assertIsNotNone(token)

        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["user"]["email"], "newstudent@example.com")
        self.assertEqual(me_res.json()["user"]["department"], "CSE")


if __name__ == "__main__":
    unittest.main(verbosity=2)

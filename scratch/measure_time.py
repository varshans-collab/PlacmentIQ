import time
import sys
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.config import DB_PATH
from app.database import init_db
from app.services.model_service import model_service
from app.routers.tpo import get_tpo_overview

init_db()
model_service.load_artifacts()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

start = time.time()
res = get_tpo_overview(dept="ALL", db=conn)
end = time.time()

print(f"Response Time for GET /api/tpo/overview: {end - start:.4f} seconds")
print(f"Total Students: {res.get('total_students')}, Overall Avg: {res.get('overall_readiness_avg')}%")
conn.close()

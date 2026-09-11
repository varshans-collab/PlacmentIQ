import sqlite3
from fastapi import APIRouter, Depends
from app.database import get_db
from app.schemas import SimulatorConfigRequest, InterventionCompareRequest
from app.services.simulator_engine import run_flight_simulator, compare_interventions, run_plus10_optimizer

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

def get_cohort(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

@router.post("/run")
def run_simulation(config: SimulatorConfigRequest, db: sqlite3.Connection = Depends(get_db)):
    cohort = get_cohort(db)
    res = run_flight_simulator(cohort, config.dict())
    return res

@router.get("/bottlenecks")
def get_bottlenecks(role: str = "Data Analyst", db: sqlite3.Connection = Depends(get_db)):
    cohort = get_cohort(db)
    config = {"target_role": role, "department": "ALL"}
    res = run_flight_simulator(cohort, config)
    return {
        "target_role": role,
        "primary_bottleneck": res["primary_bottleneck"],
        "pre_mortem": res["pre_mortem"],
        "stages": res["stages"],
        "data_provenance": "SIMULATED"
    }

@router.post("/interventions/compare")
def compare_intervention_scenarios(req: InterventionCompareRequest, db: sqlite3.Connection = Depends(get_db)):
    cohort = get_cohort(db)
    config = req.config.dict()
    interventions = compare_interventions(cohort, config, req.selected_interventions)
    optimizer = run_plus10_optimizer(cohort, config)

    return {
        "config": config,
        "interventions": interventions,
        "plus_10_optimizer": optimizer,
        "data_provenance": "SIMULATED"
    }

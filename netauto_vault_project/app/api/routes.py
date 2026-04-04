from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.models.schemas import RunRequest, RunResponse
from app.services.job_service import submit_run_job

router = APIRouter()


@router.post("/run", response_model=RunResponse)
def run_commands(request: RunRequest):
    task = submit_run_job(request)
    return RunResponse(job_id=task.id, status="queued", detail="Job submitted")


@router.get("/status/{job_id}")
def job_status(job_id: str):
    result = AsyncResult(job_id, app=celery_app)
    payload = {"job_id": job_id, "status": result.status}
    if result.status == "FAILURE":
        payload["error"] = str(result.result)
    return payload


@router.get("/result/{job_id}")
def job_result(job_id: str):
    result = AsyncResult(job_id, app=celery_app)
    if result.status == "PENDING":
        raise HTTPException(status_code=404, detail="Job not found or still pending")
    if result.status != "SUCCESS":
        return {"job_id": job_id, "status": result.status, "detail": str(result.result)}
    return {"job_id": job_id, "status": result.status, "result": result.result}


@router.get("/health")
def health():
    return {"status": "ok"}

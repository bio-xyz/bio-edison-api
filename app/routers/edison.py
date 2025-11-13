import asyncio
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from edison_client import EdisonClient, JobNames
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel

load_dotenv()

router = APIRouter(
    prefix="/edison",
    tags=["edison"],
)


# Pydantic models for request/response
class JobType(str, Enum):
    LITERATURE = "LITERATURE"
    ANALYSIS = "ANALYSIS"
    PRECEDENT = "PRECEDENT"
    MOLECULES = "MOLECULES"
    DUMMY = "DUMMY"


class TaskRequest(BaseModel):
    name: JobType
    query: str
    runtime_config: Optional[Dict[str, Any]] = None


class MultipleTasksRequest(BaseModel):
    tasks: List[TaskRequest]


class TaskResponse(BaseModel):
    task_id: Optional[str] = None
    answer: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    answer: Optional[str] = None
    error: Optional[str] = None


# Dependency to extract API key from Authorization header
def get_api_key(authorization: Optional[str] = Header(None)):
    """Extract Bearer token from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


# Initialize Edison client
def get_edison_client(api_key: str):
    """Create Edison client with the provided API key"""
    return EdisonClient(api_key=api_key)


def job_name_mapper(job_type: JobType):
    """Map our enum to edison JobNames"""
    mapping = {
        JobType.LITERATURE: JobNames.LITERATURE,
        JobType.ANALYSIS: JobNames.ANALYSIS,
        JobType.PRECEDENT: JobNames.PRECEDENT,
        JobType.MOLECULES: JobNames.MOLECULES,
        JobType.DUMMY: JobNames.DUMMY,
    }
    return mapping[job_type]


@router.get("/health")
async def edison_health(api_key: str = Depends(get_api_key)):
    """Check Edison service connectivity"""
    try:
        client = get_edison_client(api_key)
        return {"status": "connected", "service": "edison", "client_configured": True}
    except HTTPException as e:
        return {
            "status": "error",
            "service": "edison",
            "client_configured": False,
            "error": str(e.detail),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Edison service unavailable: {str(e)}"
        )


@router.post("/run/sync", response_model=TaskResponse)
async def run_task_sync(task: TaskRequest, api_key: str = Depends(get_api_key)):
    """Run a single Edison task synchronously and wait for completion"""
    try:
        client = get_edison_client(api_key)

        task_data = {
            "name": job_name_mapper(task.name),
            "query": task.query,
        }

        if task.runtime_config:
            task_data["runtime_config"] = task.runtime_config

        # Run task until completion
        task_response = await client.arun_tasks_until_done(task_data)

        return TaskResponse(answer=task_response.answer, status="completed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")


@router.post("/run/sync/multiple", response_model=List[TaskResponse])
async def run_multiple_tasks_sync(request: MultipleTasksRequest, api_key: str = Depends(get_api_key)):
    """Run multiple Edison tasks synchronously"""
    try:
        client = get_edison_client(api_key)

        tasks_data = []
        for task in request.tasks:
            task_data = {
                "name": job_name_mapper(task.name),
                "query": task.query,
            }
            if task.runtime_config:
                task_data["runtime_config"] = task.runtime_config
            tasks_data.append(task_data)

        # Run all tasks until completion
        task_responses = await client.arun_tasks_until_done(tasks_data)

        results = []
        for response in task_responses:
            results.append(TaskResponse(answer=response.answer, status="completed"))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks execution failed: {str(e)}")


@router.post("/run/async", response_model=TaskResponse)
async def run_task_async(task: TaskRequest, api_key: str = Depends(get_api_key)):
    """Start an Edison task asynchronously and return task ID"""
    try:
        client = get_edison_client(api_key)

        task_data = {
            "name": job_name_mapper(task.name),
            "query": task.query,
        }

        if task.runtime_config:
            task_data["runtime_config"] = task.runtime_config

        # Create task and return task ID
        task_id = await client.acreate_task(task_data)

        return TaskResponse(task_id=task_id, status="started")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")


@router.post("/run/async/multiple", response_model=List[TaskResponse])
async def run_multiple_tasks_async(request: MultipleTasksRequest, api_key: str = Depends(get_api_key)):
    """Start multiple Edison tasks asynchronously"""
    try:
        client = get_edison_client(api_key)

        results = []
        for task in request.tasks:
            task_data = {
                "name": job_name_mapper(task.name),
                "query": task.query,
            }
            if task.runtime_config:
                task_data["runtime_config"] = task.runtime_config

            task_id = await client.acreate_task(task_data)
            results.append(TaskResponse(task_id=task_id, status="started"))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks creation failed: {str(e)}")


@router.get("/task/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, api_key: str = Depends(get_api_key)):
    """Get the status of an asynchronous task"""
    try:
        client = get_edison_client(api_key)

        task_status = await client.aget_task(task_id)

        return TaskStatusResponse(
            task_id=task_id,
            status=task_status.status if hasattr(task_status, 'status') else "unknown",
            answer=task_status.answer if hasattr(task_status, 'answer') else None,
            error=task_status.error if hasattr(task_status, 'error') else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get task status: {str(e)}"
        )


@router.post("/run/continuation/sync", response_model=TaskResponse)
async def run_continuation_task_sync(task: TaskRequest, continued_job_id: str, api_key: str = Depends(get_api_key)):
    """Run a continuation task synchronously based on a previous task"""
    try:
        client = get_edison_client(api_key)

        task_data = {
            "name": job_name_mapper(task.name),
            "query": task.query,
            "runtime_config": {"continued_job_id": continued_job_id},
        }

        # Merge with any additional runtime_config from request
        if task.runtime_config:
            task_data["runtime_config"].update(task.runtime_config)

        task_response = await client.arun_tasks_until_done(task_data)

        return TaskResponse(answer=task_response.answer, status="completed")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Continuation task failed: {str(e)}"
        )


@router.post("/run/continuation/async", response_model=TaskResponse)
async def run_continuation_task_async(task: TaskRequest, continued_job_id: str, api_key: str = Depends(get_api_key)):
    """Start a continuation task asynchronously based on a previous task"""
    try:
        client = get_edison_client(api_key)

        task_data = {
            "name": job_name_mapper(task.name),
            "query": task.query,
            "runtime_config": {"continued_job_id": continued_job_id},
        }

        # Merge with any additional runtime_config from request
        if task.runtime_config:
            task_data["runtime_config"].update(task.runtime_config)

        # Create task and return task ID
        task_id = await client.acreate_task(task_data)

        return TaskResponse(task_id=task_id, status="started")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Continuation task creation failed: {str(e)}"
        )


@router.get("/jobs/available")
async def get_available_jobs():
    """Get list of available job types"""
    return {
        "jobs": [
            {
                "name": "LITERATURE",
                "description": "Literature Search - Ask a question of scientific data sources, and receive a high-accuracy, cited response. Built with PaperQA3.",
            },
            {
                "name": "ANALYSIS",
                "description": "Data Analysis - Turn biological datasets into detailed analyses answering your research questions.",
            },
            {
                "name": "PRECEDENT",
                "description": "Precedent Search - Formerly known as HasAnyone, query if anyone has ever done something in science.",
            },
            {
                "name": "MOLECULES",
                "description": "Chemistry Tasks - A new iteration of ChemCrow, Phoenix uses cheminformatics tools to do chemistry. Good for planning synthesis and designing new molecules.",
            },
            {
                "name": "DUMMY",
                "description": "Dummy Task - This is a dummy task. Mainly for testing purposes.",
            },
        ]
    }

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    """Task type enumeration."""
    SEQUENTIAL = "sequential"
    BACKGROUND = "background"
    THREADING = "threading"
    MULTIPROCESSING = "multiprocessing"
    BATCH_ASYNC = "batch_async"
    CONCURRENT_FUTURES = "concurrent_futures"

class TaskConfig(BaseModel):
    """Configuration for CPU-heavy tasks."""
    items_count: int = Field(default=50000, ge=1000, le=100000, description="Number of items to process")
    batch_size: int = Field(default=5000, ge=100, le=10000, description="Batch size for processing")
    workers: int = Field(default=4, ge=1, le=16, description="Number of workers/threads")
    simulate_db_delay: bool = Field(default=True, description="Simulate database delay")
    simulate_redis_delay: bool = Field(default=True, description="Simulate Redis delay")

class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    items_processed: int
    total_items: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    results: List[Dict[str, Any]] = []
    error_message: Optional[str] = None

class TaskResponse(BaseModel):
    """Response for task operations."""
    task_id: str
    status: TaskStatus
    message: str
    estimated_duration: Optional[int] = None  # in seconds

class PerformanceComparison(BaseModel):
    """Performance comparison between different approaches."""
    sequential_time: Optional[float] = None
    background_time: Optional[float] = None
    threading_time: Optional[float] = None
    multiprocessing_time: Optional[float] = None
    batch_async_time: Optional[float] = None
    concurrent_futures_time: Optional[float] = None
    best_approach: Optional[str] = None
    improvement_factor: Optional[float] = None 
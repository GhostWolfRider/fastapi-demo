from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import asyncio

from app.models import (
    TaskConfig, TaskResult, TaskResponse, TaskStatus, TaskType, PerformanceComparison
)
from app.utils.processors import (
    SequentialProcessor, ThreadingProcessor, MultiprocessingProcessor,
    AsyncBatchProcessor, ConcurrentFuturesProcessor, BackgroundTaskProcessor,
    get_task_result, get_all_task_results
)

router = APIRouter()

@router.get("/", summary="Get all available task processing methods")
async def get_task_methods():
    """
    Get information about all available task processing methods for CPU-heavy operations.
    """
    return {
        "message": "CPU-Heavy Task Processing Methods",
        "methods": {
            "sequential": {
                "description": "Baseline sequential processing - processes items one by one",
                "best_for": "Small datasets, debugging, baseline comparison",
                "endpoint": "/sequential"
            },
            "threading": {
                "description": "Uses ThreadPoolExecutor for I/O-bound operations",
                "best_for": "I/O-heavy operations (DB queries, API calls)",
                "endpoint": "/threading"
            },
            "multiprocessing": {
                "description": "Uses multiprocessing.Pool for CPU-bound operations",
                "best_for": "CPU-intensive computations, bypasses GIL",
                "endpoint": "/multiprocessing"
            },
            "async_batch": {
                "description": "Processes items in async batches",
                "best_for": "Mixed I/O and CPU operations with controlled concurrency",
                "endpoint": "/async-batch"
            },
            "concurrent_futures": {
                "description": "Uses concurrent.futures.ProcessPoolExecutor",
                "best_for": "CPU-bound operations with fine-grained control",
                "endpoint": "/concurrent-futures"
            },
            "background": {
                "description": "Non-blocking background task processing",
                "best_for": "Long-running tasks that shouldn't block API responses",
                "endpoint": "/background"
            }
        },
        "endpoints": {
            "compare": "/compare - Compare performance of different methods",
            "status": "/status/{task_id} - Get task status",
            "results": "/results - Get all task results"
        }
    }

@router.post("/sequential", response_model=TaskResult)
async def process_sequential(config: TaskConfig = TaskConfig()):
    """
    Process items sequentially (baseline approach).
    
    This is the slowest method but serves as a baseline for comparison.
    Each item is processed one after another in a single thread.
    """
    try:
        result = SequentialProcessor.process_items(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sequential processing failed: {str(e)}")

@router.post("/threading", response_model=TaskResult)
async def process_threading(config: TaskConfig = TaskConfig()):
    """
    Process items using ThreadPoolExecutor.
    
    Best for I/O-bound operations like database queries and API calls.
    Uses multiple threads to handle I/O concurrency but limited by GIL for CPU operations.
    """
    try:
        result = ThreadingProcessor.process_items(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threading processing failed: {str(e)}")

@router.post("/multiprocessing", response_model=TaskResult)
async def process_multiprocessing(config: TaskConfig = TaskConfig()):
    """
    Process items using multiprocessing.Pool.
    
    Best for CPU-bound operations as it bypasses Python's GIL.
    Creates separate processes for true parallel CPU computation.
    """
    try:
        result = MultiprocessingProcessor.process_items(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiprocessing failed: {str(e)}")

@router.post("/async-batch", response_model=TaskResult)
async def process_async_batch(config: TaskConfig = TaskConfig()):
    """
    Process items in async batches.
    
    Processes items in configurable batch sizes using asyncio.gather.
    Good for mixed I/O and CPU operations with controlled concurrency.
    """
    try:
        result = await AsyncBatchProcessor.process_items(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Async batch processing failed: {str(e)}")

@router.post("/concurrent-futures", response_model=TaskResult)
async def process_concurrent_futures(config: TaskConfig = TaskConfig()):
    """
    Process items using concurrent.futures.ProcessPoolExecutor.
    
    Similar to multiprocessing but with more control over execution.
    Uses as_completed() for handling results as they finish.
    """
    try:
        result = ConcurrentFuturesProcessor.process_items(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Concurrent futures processing failed: {str(e)}")

@router.post("/background", response_model=TaskResponse)
async def process_background(config: TaskConfig = TaskConfig()):
    """
    Start background task processing (non-blocking).
    
    Returns immediately with a task ID. Use /status/{task_id} to check progress.
    Best for long-running tasks that shouldn't block the API response.
    """
    try:
        task_id = BackgroundTaskProcessor.start_background_task(config)
        estimated_duration = config.items_count * 1.2  # Rough estimate
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            message="Background task started successfully",
            estimated_duration=int(estimated_duration)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background task failed to start: {str(e)}")

@router.get("/status/{task_id}", response_model=TaskResult)
async def get_task_status(task_id: str = Path(..., description="Task ID to check status")):
    """
    Get the status and progress of a specific task.
    
    Returns current status, progress, and results if completed.
    """
    result = get_task_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return result

@router.get("/results", response_model=List[TaskResult])
async def get_all_results():
    """
    Get all task results for comparison and analysis.
    
    Returns results from all previously executed tasks.
    """
    return get_all_task_results()

@router.post("/compare", response_model=PerformanceComparison)
async def compare_performance(
    items_count: int = Query(1000, ge=100, le=500000, description="Number of items to process for comparison"),
    workers: int = Query(4, ge=1, le=16, description="Number of workers to use")
):
    """
    Compare performance of different processing methods.
    
    Runs a smaller workload through different processors to compare performance.
    Note: This will take some time as it runs multiple processing methods.
    """
    config = TaskConfig(
        items_count=items_count,
        workers=workers,
        simulate_db_delay=True,
        simulate_redis_delay=True
    )
    
    comparison = PerformanceComparison()
    times = {}
    
    try:
        # Sequential (baseline)
        sequential_result = SequentialProcessor.process_items(config)
        comparison.sequential_time = sequential_result.duration_seconds
        times["sequential"] = sequential_result.duration_seconds
        
        # Threading
        threading_result = ThreadingProcessor.process_items(config)
        comparison.threading_time = threading_result.duration_seconds
        times["threading"] = threading_result.duration_seconds
        
        # Multiprocessing
        mp_result = MultiprocessingProcessor.process_items(config)
        comparison.multiprocessing_time = mp_result.duration_seconds
        times["multiprocessing"] = mp_result.duration_seconds
        
        # Async Batch
        async_result = await AsyncBatchProcessor.process_items(config)
        comparison.batch_async_time = async_result.duration_seconds
        times["batch_async"] = async_result.duration_seconds
        
        # Concurrent Futures
        cf_result = ConcurrentFuturesProcessor.process_items(config)
        comparison.concurrent_futures_time = cf_result.duration_seconds
        times["concurrent_futures"] = cf_result.duration_seconds
        
        # Find best approach
        best_method = min(times.items(), key=lambda x: x[1])
        comparison.best_approach = best_method[0]
        
        # Calculate improvement over sequential
        if comparison.sequential_time and comparison.sequential_time > 0:
            best_time = best_method[1]
            comparison.improvement_factor = comparison.sequential_time / best_time
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance comparison failed: {str(e)}")

@router.delete("/results")
async def clear_results():
    """
    Clear all stored task results.
    
    Useful for cleaning up before running new performance tests.
    """
    from app.utils.processors import task_results
    task_results.clear()
    return {"message": "All task results cleared successfully"}

@router.get("/recommendations")
async def get_recommendations():
    """
    Get recommendations for optimal CPU-heavy task processing.
    
    Provides guidelines for choosing the best approach based on workload characteristics.
    """
    return {
        "recommendations": {
            "for_io_heavy_workloads": {
                "primary": "Threading or Async Batch",
                "reason": "I/O operations benefit from concurrency, threading handles I/O well",
                "optimal_workers": "2-4x CPU cores for I/O bound tasks"
            },
            "for_cpu_heavy_workloads": {
                "primary": "Multiprocessing or Concurrent Futures",
                "reason": "Bypasses Python GIL, utilizes multiple CPU cores effectively",
                "optimal_workers": "Equal to number of CPU cores"
            },
            "for_mixed_workloads": {
                "primary": "Async Batch with moderate batch sizes",
                "reason": "Balances I/O concurrency with CPU utilization",
                "optimal_batch_size": "1000-5000 items per batch"
            },
            "for_long_running_tasks": {
                "primary": "Background processing",
                "reason": "Prevents API timeouts, allows progress monitoring",
                "consideration": "Implement proper task status tracking"
            }
        },
        "scaling_considerations": {
            "small_datasets": "< 1000 items: Threading or Sequential",
            "medium_datasets": "1000-10000 items: Multiprocessing or Async Batch",
            "large_datasets": "> 10000 items: Background + Multiprocessing",
            "memory_constraints": "Use batch processing to limit memory usage"
        },
        "monitoring": {
            "metrics_to_track": ["duration", "memory_usage", "cpu_utilization", "error_rate"],
            "optimization_targets": ["minimize_duration", "optimize_resource_usage", "maintain_stability"]
        }
    } 
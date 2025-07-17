import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count
import threading
from typing import List, Dict, Any, Callable
from datetime import datetime

from app.utils.task_simulator import process_single_item, async_process_single_item, generate_task_id
from app.models import TaskResult, TaskType, TaskStatus, TaskConfig

# Global task storage (in production, use Redis or a database)
task_results = {}

class SequentialProcessor:
    """Process items sequentially - baseline implementation."""
    
    @staticmethod
    def process_items(config: TaskConfig) -> TaskResult:
        task_id = generate_task_id()
        start_time = datetime.now()
        
        task_result = TaskResult(
            task_id=task_id,
            task_type=TaskType.SEQUENTIAL,
            status=TaskStatus.RUNNING,
            items_processed=0,
            total_items=config.items_count,
            start_time=start_time
        )
        
        try:
            results = []
            for i in range(config.items_count):
                item_result = process_single_item(
                    i, 
                    config.simulate_db_delay, 
                    config.simulate_redis_delay
                )
                results.append(item_result)
                task_result.items_processed = i + 1
            
            end_time = datetime.now()
            task_result.end_time = end_time
            task_result.duration_seconds = (end_time - start_time).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.results = results[:5]  # Store only first 5 for demo
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
        
        task_results[task_id] = task_result
        return task_result

class ThreadingProcessor:
    """Process items using threading for I/O-bound operations."""
    
    @staticmethod
    def process_items(config: TaskConfig) -> TaskResult:
        task_id = generate_task_id()
        start_time = datetime.now()
        
        task_result = TaskResult(
            task_id=task_id,
            task_type=TaskType.THREADING,
            status=TaskStatus.RUNNING,
            items_processed=0,
            total_items=config.items_count,
            start_time=start_time
        )
        workers = min(config.workers, cpu_count() - 1)

        try:
            results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                # Submit all tasks
                future_to_item = {
                    executor.submit(
                        process_single_item, 
                        i, 
                        config.simulate_db_delay, 
                        config.simulate_redis_delay
                    ): i for i in range(config.items_count)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_item):
                    item_result = future.result()
                    results.append(item_result)
                    task_result.items_processed = len(results)
            
            end_time = datetime.now()
            task_result.end_time = end_time
            task_result.duration_seconds = (end_time - start_time).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.results = results[:5]  # Store only first 5 for demo
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
        
        task_results[task_id] = task_result
        return task_result

class MultiprocessingProcessor:
    """Process items using multiprocessing for CPU-bound operations."""
    
    @staticmethod
    def process_items(config: TaskConfig) -> TaskResult:
        task_id = generate_task_id()
        start_time = datetime.now()
        
        task_result = TaskResult(
            task_id=task_id,
            task_type=TaskType.MULTIPROCESSING,
            status=TaskStatus.RUNNING,
            items_processed=0,
            total_items=config.items_count,
            start_time=start_time
        )
        
        try:
            # Prepare arguments for multiprocessing
            args = [
                (i, config.simulate_db_delay, config.simulate_redis_delay) 
                for i in range(config.items_count)
            ]
            
            results = []
            workers = min(config.workers, cpu_count()-1)
            
            with Pool(processes=workers) as pool:
                # Use starmap for multiple arguments
                pool_results = pool.starmap(process_single_item, args)
                results.extend(pool_results)
            
            task_result.items_processed = len(results)
            end_time = datetime.now()
            task_result.end_time = end_time
            task_result.duration_seconds = (end_time - start_time).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.results = results
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
        
        task_results[task_id] = task_result
        return task_result

class AsyncBatchProcessor:
    """Process items in async batches to optimize I/O operations."""
    
    @staticmethod
    async def process_items(config: TaskConfig) -> TaskResult:
        task_id = generate_task_id()
        start_time = datetime.now()
        
        task_result = TaskResult(
            task_id=task_id,
            task_type=TaskType.BATCH_ASYNC,
            status=TaskStatus.RUNNING,
            items_processed=0,
            total_items=config.items_count,
            start_time=start_time
        )
        
        try:
            results = []
            batch_size = config.batch_size
            
            # Process in batches
            for i in range(0, config.items_count, batch_size):
                batch_end = min(i + batch_size, config.items_count)
                batch_items = range(i, batch_end)
                
                # Process batch concurrently
                batch_tasks = [
                    async_process_single_item(
                        item_id, 
                        config.simulate_db_delay, 
                        config.simulate_redis_delay
                    ) for item_id in batch_items
                ]
                
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)
                task_result.items_processed = len(results)
            
            end_time = datetime.now()
            task_result.end_time = end_time
            task_result.duration_seconds = (end_time - start_time).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.results = results  # Store only first 5 for demo
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
        
        task_results[task_id] = task_result
        return task_result

class ConcurrentFuturesProcessor:
    """Process items using concurrent.futures for both CPU and I/O bound operations."""
    
    @staticmethod
    def process_items(config: TaskConfig) -> TaskResult:
        task_id = generate_task_id()
        start_time = datetime.now()
        
        task_result = TaskResult(
            task_id=task_id,
            task_type=TaskType.CONCURRENT_FUTURES,
            status=TaskStatus.RUNNING,
            items_processed=0,
            total_items=config.items_count,
            start_time=start_time
        )
        
        try:
            results = []
            workers = min(config.workers, cpu_count() - 1)

            # Use ProcessPoolExecutor for CPU-bound work
            with ProcessPoolExecutor(max_workers=workers) as executor:
                # Submit all tasks
                future_to_item = {
                    executor.submit(
                        process_single_item, 
                        i, 
                        config.simulate_db_delay, 
                        config.simulate_redis_delay
                    ): i for i in range(config.items_count)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_item):
                    item_result = future.result()
                    results.append(item_result)
                    task_result.items_processed = len(results)
            
            end_time = datetime.now()
            task_result.end_time = end_time
            task_result.duration_seconds = (end_time - start_time).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.results = results[:5]  # Store only first 5 for demo
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error_message = str(e)
        
        task_results[task_id] = task_result
        return task_result

class BackgroundTaskProcessor:
    """Process items as background tasks (non-blocking)."""
    
    @staticmethod
    def start_background_task(config: TaskConfig) -> str:
        task_id = generate_task_id()
        
        def background_worker():
            start_time = datetime.now()
            
            task_result = TaskResult(
                task_id=task_id,
                task_type=TaskType.BACKGROUND,
                status=TaskStatus.RUNNING,
                items_processed=0,
                total_items=config.items_count,
                start_time=start_time
            )
            task_results[task_id] = task_result
            
            try:
                results = []
                workers = min(config.workers, cpu_count() - 1)

                # Use threading for background processing
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    future_to_item = {
                        executor.submit(
                            process_single_item, 
                            i, 
                            config.simulate_db_delay, 
                            config.simulate_redis_delay
                        ): i for i in range(config.items_count)
                    }
                    
                    for future in as_completed(future_to_item):
                        item_result = future.result()
                        results.append(item_result)
                        task_result.items_processed = len(results)
                        task_results[task_id] = task_result  # Update progress
                
                end_time = datetime.now()
                task_result.end_time = end_time
                task_result.duration_seconds = (end_time - start_time).total_seconds()
                task_result.status = TaskStatus.COMPLETED
                task_result.results = results[:5]  # Store only first 5 for demo
                
            except Exception as e:
                task_result.status = TaskStatus.FAILED
                task_result.error_message = str(e)
            
            task_results[task_id] = task_result
        
        # Start background thread
        thread = threading.Thread(target=background_worker)
        thread.daemon = True
        thread.start()
        
        return task_id

def get_task_result(task_id: str) -> TaskResult:
    """Get task result by ID."""
    return task_results.get(task_id)

def get_all_task_results() -> List[TaskResult]:
    """Get all task results."""
    return list(task_results.values()) 
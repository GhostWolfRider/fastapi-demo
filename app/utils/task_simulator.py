import time
import asyncio
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime
import math

def simulate_pinot_query(duration: float = 1.0) -> Dict[str, Any]:
    """Simulate a Pinot database query with configurable duration."""
    start_time = time.time()
    # Simulate actual work with some computation
    time.sleep(duration)
    end_time = time.time()
    
    return {
        "query_type": "pinot",
        "duration": end_time - start_time,
        "result_count": random.randint(100, 1000),
        "timestamp": datetime.now().isoformat()
    }

def simulate_redis_query() -> Dict[str, Any]:
    """Simulate a Redis query - typically faster than DB queries."""
    start_time = time.time()
    # Simulate Redis lookup with minimal delay
    time.sleep(random.uniform(0.001, 0.01))  # 1-10ms
    end_time = time.time()
    
    return {
        "query_type": "redis",
        "duration": end_time - start_time,
        "cache_hit": random.choice([True, False]),
        "timestamp": datetime.now().isoformat()
    }


def cpu_intensive_loop_v3(iterations: int = 100000) -> Dict[str, Any]:
    """Version with prime number computation."""
    start_time = time.time()
    result = 0
    primes_found = 0

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    for i in range(2, iterations):
        if is_prime(i):
            primes_found += 1
            # Additional computation on prime numbers
            x = math.sqrt(i)
            y = math.sin(x) * math.cos(x) * math.log(i)
            result += y * math.pow(i, 0.25)

    end_time = time.time()
    return {
        "operation": "cpu_loop_v3_primes",
        "iterations": iterations,
        "primes_found": primes_found,
        "result": result,
        "duration": end_time - start_time,
        "timestamp": datetime.now().isoformat()
    }

def cpu_intensive_loop(iterations: int = 20000) -> Dict[str, Any]:
    """Simulate CPU-intensive work with a simple loop."""
    start_time = time.time()
    result = 0
    
    # Simple CPU-bound computation
    for i in range(iterations):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    
    end_time = time.time()
    return {
        "operation": "cpu_loop",
        "iterations": iterations,
        "result": result,
        "duration": end_time - start_time,
        "timestamp": datetime.now().isoformat()
    }

def nested_cpu_loop(outer_iterations: int = 100, inner_iterations: int = 200) -> Dict[str, Any]:
    """Simulate nested CPU-intensive loops."""
    start_time = time.time()
    result = 0
    
    # Nested loop computation
    for i in range(outer_iterations):
        for j in range(inner_iterations):
            result += (i * j) % 1000
    
    end_time = time.time()
    return {
        "operation": "nested_cpu_loop",
        "outer_iterations": outer_iterations,
        "inner_iterations": inner_iterations,
        "result": result,
        "duration": end_time - start_time,
        "timestamp": datetime.now().isoformat()
    }

def process_single_item(
    item_id: int, 
    simulate_db: bool = True, 
    simulate_redis: bool = True,
    cpu_iterations: int = 20000
) -> Dict[str, Any]:
    """
    Process a single item with all the heavy operations.
    This simulates the 1-second processing time per item.
    """
    start_time = time.time()
    results = {
        "item_id": item_id,
        "operations": []
    }
    
    # 1. Pinot DB query (1 second)
    # if simulate_db:
    #     pinot_result = simulate_pinot_query(1.0)
    #     results["operations"].append(pinot_result)
    
    # 2. Redis query
    # if simulate_redis:
    #     redis_result = simulate_redis_query()
    #     results["operations"].append(redis_result)
    
    # 3. CPU-intensive loop
    cpu_result = cpu_intensive_loop_v3(cpu_iterations)
    results["operations"].append(cpu_result)
    
    # 4. Nested CPU loop
    # nested_result = nested_cpu_loop()
    # results["operations"].append(nested_result)
    
    end_time = time.time()
    results["total_duration"] = end_time - start_time
    results["processed_at"] = datetime.now().isoformat()
    
    return results

async def async_process_single_item(
    item_id: int, 
    simulate_db: bool = True, 
    simulate_redis: bool = True,
    cpu_iterations: int = 20000
) -> Dict[str, Any]:
    """
    Async version of process_single_item.
    Note: CPU-bound operations will still block, but I/O can be async.
    """
    start_time = time.time()
    results = {
        "item_id": item_id,
        "operations": []
    }
    
    # 1. Simulate async Pinot DB query
    # if simulate_db:
    #     await asyncio.sleep(1.0)  # Simulate async DB call
    #     results["operations"].append({
    #         "query_type": "pinot_async",
    #         "duration": 1.0,
    #         "result_count": random.randint(100, 1000),
    #         "timestamp": datetime.now().isoformat()
    #     })
    #
    # # 2. Simulate async Redis query
    # if simulate_redis:
    #     await asyncio.sleep(random.uniform(0.001, 0.01))
    #     results["operations"].append({
    #         "query_type": "redis_async",
    #         "duration": 0.005,
    #         "cache_hit": random.choice([True, False]),
    #         "timestamp": datetime.now().isoformat()
    #     })
    #
    # 3. CPU operations (these will still block)
    cpu_result = cpu_intensive_loop_v3(cpu_iterations)
    results["operations"].append(cpu_result)
    
    # nested_result = nested_cpu_loop()
    # results["operations"].append(nested_result)
    #
    end_time = time.time()
    results["total_duration"] = end_time - start_time
    results["processed_at"] = datetime.now().isoformat()
    
    return results

def generate_task_id() -> str:
    """Generate a unique task ID."""
    return f"task_{uuid.uuid4().hex[:8]}_{int(time.time())}" 
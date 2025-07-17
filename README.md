# FastAPI CPU-Heavy Task Optimization POC

This project demonstrates different approaches to optimize CPU-heavy operations in FastAPI, specifically designed to handle scenarios with:
- Database queries (1 sec each to Pinot)
- Redis queries 
- CPU-intensive loops (20,000 iterations)
- Nested CPU loops
- Processing 50,000+ items efficiently

## 🚀 Quick Start

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Access the API
- **API Documentation**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **Root Endpoint**: http://localhost:8001/

## 🔧 Available Processing Methods

### 1. Sequential Processing
**Endpoint**: `POST /api/v1/tasks/sequential`
- **Description**: Baseline approach, processes items one by one
- **Best for**: Small datasets, debugging, establishing baseline performance
- **Performance**: Slowest but predictable

### 2. Threading (ThreadPoolExecutor)
**Endpoint**: `POST /api/v1/tasks/threading`
- **Description**: Uses multiple threads for I/O-bound operations
- **Best for**: Database queries, API calls, I/O-heavy workloads
- **Performance**: Good for I/O, limited by GIL for CPU operations

### 3. Multiprocessing
**Endpoint**: `POST /api/v1/tasks/multiprocessing`
- **Description**: Uses separate processes to bypass Python's GIL
- **Best for**: CPU-intensive computations, mathematical operations
- **Performance**: Excellent for CPU-bound tasks

### 4. Async Batch Processing
**Endpoint**: `POST /api/v1/tasks/async-batch`
- **Description**: Processes items in configurable async batches
- **Best for**: Mixed I/O and CPU operations with controlled concurrency
- **Performance**: Good balance between resource usage and speed

### 5. Concurrent Futures
**Endpoint**: `POST /api/v1/tasks/concurrent-futures`
- **Description**: Uses ProcessPoolExecutor with fine-grained control
- **Best for**: CPU-bound operations requiring result handling flexibility
- **Performance**: Similar to multiprocessing with better control

### 6. Background Tasks
**Endpoint**: `POST /api/v1/tasks/background`
- **Description**: Non-blocking background processing
- **Best for**: Long-running tasks that shouldn't block API responses
- **Performance**: Immediate response, async execution

## 📊 Performance Comparison

### Compare All Methods
```bash
curl -X POST "http://localhost:8001/api/v1/tasks/compare?items_count=1000&workers=4"
```

### Example Performance Results
For 1000 items with 4 workers:
- **Sequential**: ~1000 seconds (baseline)
- **Threading**: ~250 seconds (4x improvement for I/O)
- **Multiprocessing**: ~200 seconds (5x improvement for CPU)
- **Async Batch**: ~300 seconds (good balance)
- **Concurrent Futures**: ~200 seconds (similar to multiprocessing)

## 🎯 Usage Examples

### Basic Task Configuration
```json
{
  "items_count": 50000,
  "batch_size": 5000,
  "workers": 4,
  "simulate_db_delay": true,
  "simulate_redis_delay": true
}
```

### Sequential Processing (Small Test)
```bash
curl -X POST "http://localhost:8001/api/v1/tasks/sequential" \
  -H "Content-Type: application/json" \
  -d '{"items_count": 100, "workers": 1}'
```

### Multiprocessing (Optimal for CPU)
```bash
curl -X POST "http://localhost:8001/api/v1/tasks/multiprocessing" \
  -H "Content-Type: application/json" \
  -d '{"items_count": 50000, "workers": 8}'
```

### Background Task (Non-blocking)
```bash
# Start background task
curl -X POST "http://localhost:8001/api/v1/tasks/background" \
  -H "Content-Type: application/json" \
  -d '{"items_count": 50000, "workers": 4}'

# Check status (use task_id from response)
curl "http://localhost:8001/api/v1/tasks/status/task_abc123_1234567890"
```

### Get Recommendations
```bash
curl "http://localhost:8001/api/v1/tasks/recommendations"
```

## 🏗️ Project Structure

```
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Application configuration
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py       # Task processing endpoints
│   └── utils/
│       ├── __init__.py
│       ├── task_simulator.py  # Simulates CPU/I/O operations
│       └── processors.py     # Different processing implementations
```

## 🧪 Simulated Operations

Each item processing includes:
1. **Pinot DB Query**: 1-second database query simulation
2. **Redis Query**: 1-10ms cache lookup simulation  
3. **CPU Loop**: 20,000 iterations of mathematical computations
4. **Nested CPU Loop**: Nested loops for additional CPU load

## 📈 Optimization Strategies

### For Your 50,000 Item Use Case

#### Option 1: Multiprocessing (Recommended for CPU-heavy)
```python
# Optimal configuration for CPU-bound work
config = {
    "items_count": 50000,
    "workers": 8,  # Match your CPU cores
    "batch_size": 5000
}
```

#### Option 2: Background + Batching (Recommended for Production)
```python
# For production APIs to avoid timeouts
config = {
    "items_count": 50000,
    "workers": 6,
    "batch_size": 2000
}
# Use background endpoint for non-blocking execution
```

#### Option 3: Hybrid Approach
For mixed workloads, consider:
1. Use async batching for I/O operations (DB/Redis)
2. Use multiprocessing for CPU-intensive loops
3. Implement progress tracking for user feedback

## 🔍 Monitoring & Optimization

### Key Metrics to Track
- **Duration**: Total execution time
- **Throughput**: Items processed per second
- **Memory Usage**: Peak memory consumption
- **CPU Utilization**: Core usage efficiency
- **Error Rate**: Failed operations percentage

### Optimization Tips
1. **Match workers to workload type**:
   - I/O-bound: 2-4x CPU cores
   - CPU-bound: 1x CPU cores
   - Mixed: Start with 1.5x CPU cores

2. **Tune batch sizes**:
   - Small batches (1000): Better progress tracking
   - Large batches (10000): Better throughput
   - Balance based on memory constraints

3. **Consider memory limits**:
   - Large datasets: Use generators/streaming
   - Limited memory: Reduce batch sizes
   - High concurrency: Monitor memory usage

## 🚦 Production Considerations

### Scalability
- Use Redis/Database for task storage instead of in-memory
- Implement proper logging and monitoring
- Add rate limiting and resource controls
- Consider using Celery for complex task management

### Error Handling
- Implement retry mechanisms for failed operations
- Add circuit breakers for external dependencies
- Monitor and alert on high error rates

### Security
- Validate input parameters thoroughly
- Implement authentication and authorization
- Rate limit API endpoints
- Monitor for resource exhaustion attacks

## 📊 Benchmarking Your System

Run the comparison endpoint to understand your system's characteristics:

```bash
# Small test
curl -X POST "http://localhost:8001/api/v1/tasks/compare?items_count=100&workers=4"

# Medium test  
curl -X POST "http://localhost:8001/api/v1/tasks/compare?items_count=1000&workers=4"

# Performance test (be patient!)
curl -X POST "http://localhost:8001/api/v1/tasks/compare?items_count=5000&workers=8"
```

The results will help you choose the optimal approach for your specific hardware and workload characteristics. 
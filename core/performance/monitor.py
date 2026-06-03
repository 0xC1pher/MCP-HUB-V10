import psutil
import time
import structlog

logger = structlog.get_logger()

class PerformanceMonitor:
    def __init__(self):
        self.last_log = time.time()
    
    def collect_metrics(self):
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "memory_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "disk_reads": psutil.disk_io_counters().read_bytes,
            "disk_writes": psutil.disk_io_counters().write_bytes
        }
        
        if time.time() - self.last_log > 60:  # Log every minute
            logger.info(f"Performance metrics: {metrics}")
            self.last_log = time.time()
            return metrics
        return None

# Initialize monitor instance
performance_monitor = PerformanceMonitor()

# Example usage (called from Vision Hub or Orchestrator)
def start_monitoring():
    while True:
        performance_monitor.collect_metrics()
        time.sleep(60)  # Check every minute

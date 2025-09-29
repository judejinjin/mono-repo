"""
Health check endpoints for Docker containers and Kubernetes probes.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import sys
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import asyncio

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from libs.monitoring import get_health_checker
    from config import get_config
except ImportError:
    # Fallback if libs not available
    get_health_checker = None
    get_config = None


class HealthCheckManager:
    """Manages health checks for the application."""
    
    def __init__(self, app_name: str = "service"):
        self.app_name = app_name
        self.start_time = datetime.utcnow()
        self.config = get_config() if get_config else {}
        self.health_checker = get_health_checker() if get_health_checker else None
    
    def get_basic_health(self) -> Dict[str, Any]:
        """Get basic health information."""
        uptime = datetime.utcnow() - self.start_time
        
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            "service": self.app_name,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime": str(uptime),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024)
            },
            "environment": {
                "python_version": sys.version,
                "environment": os.getenv('ENVIRONMENT', 'unknown'),
                "hostname": os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            }
        }
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health check with dependencies."""
        basic_health = self.get_basic_health()
        
        # Add dependency checks if health checker available
        if self.health_checker:
            try:
                dependency_status = await self.health_checker.check_all_dependencies()
                basic_health["dependencies"] = dependency_status
                
                # Update overall status based on dependencies
                failed_deps = [name for name, status in dependency_status.items() 
                              if status.get("status") == "unhealthy"]
                
                if failed_deps:
                    basic_health["status"] = "degraded"
                    basic_health["failed_dependencies"] = failed_deps
                    
            except Exception as e:
                basic_health["status"] = "degraded"
                basic_health["health_check_error"] = str(e)
        
        return basic_health
    
    def get_liveness_probe(self) -> Dict[str, Any]:
        """Kubernetes liveness probe - basic alive check."""
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "service": self.app_name
        }
    
    async def get_readiness_probe(self) -> Dict[str, Any]:
        """Kubernetes readiness probe - ready to serve traffic."""
        try:
            # Check if service is ready to handle requests
            health = await self.get_detailed_health()
            
            # Determine readiness based on health status
            is_ready = health["status"] in ["healthy", "degraded"]
            
            return {
                "status": "ready" if is_ready else "not_ready",
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "service": self.app_name,
                "details": health if not is_ready else None
            }
        except Exception as e:
            return {
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "service": self.app_name,
                "error": str(e)
            }


def add_health_endpoints(app: FastAPI, service_name: str):
    """Add health check endpoints to FastAPI app."""
    health_manager = HealthCheckManager(service_name)
    
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        try:
            health = health_manager.get_basic_health()
            return JSONResponse(content=health, status_code=200)
        except Exception as e:
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                },
                status_code=503
            )
    
    @app.get("/health/detailed")
    async def detailed_health_check():
        """Detailed health check with dependencies."""
        try:
            health = await health_manager.get_detailed_health()
            status_code = 200 if health["status"] == "healthy" else 503
            return JSONResponse(content=health, status_code=status_code)
        except Exception as e:
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                },
                status_code=503
            )
    
    @app.get("/health/liveness")
    async def liveness_probe():
        """Kubernetes liveness probe."""
        try:
            health = health_manager.get_liveness_probe()
            return JSONResponse(content=health, status_code=200)
        except Exception as e:
            return JSONResponse(
                content={
                    "status": "dead",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                },
                status_code=503
            )
    
    @app.get("/health/readiness")
    async def readiness_probe():
        """Kubernetes readiness probe."""
        try:
            health = await health_manager.get_readiness_probe()
            status_code = 200 if health["status"] == "ready" else 503
            return JSONResponse(content=health, status_code=status_code)
        except Exception as e:
            return JSONResponse(
                content={
                    "status": "not_ready",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                },
                status_code=503
            )
    
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        try:
            if health_manager.health_checker:
                metrics = health_manager.health_checker.get_prometheus_metrics()
                return JSONResponse(content=metrics, status_code=200)
            else:
                # Basic metrics without monitoring library
                basic_health = health_manager.get_basic_health()
                metrics = {
                    "service_up": 1,
                    "cpu_percent": basic_health["system"]["cpu_percent"],
                    "memory_percent": basic_health["system"]["memory_percent"],
                    "disk_percent": basic_health["system"]["disk_percent"],
                    "uptime_seconds": basic_health["uptime_seconds"]
                }
                return JSONResponse(content=metrics, status_code=200)
        except Exception as e:
            return JSONResponse(
                content={"error": str(e)},
                status_code=500
            )


def create_standalone_health_app(service_name: str) -> FastAPI:
    """Create a standalone health check FastAPI app."""
    app = FastAPI(
        title=f"{service_name} Health Checks",
        description="Health check and monitoring endpoints",
        version="1.0.0"
    )
    
    add_health_endpoints(app, service_name)
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": service_name,
            "message": "Health check service is running",
            "endpoints": {
                "health": "/health",
                "detailed_health": "/health/detailed", 
                "liveness": "/health/liveness",
                "readiness": "/health/readiness",
                "metrics": "/metrics"
            }
        }
    
    return app


# For use in other services
__all__ = ['HealthCheckManager', 'add_health_endpoints', 'create_standalone_health_app']
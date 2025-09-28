"""
JupyterHub Service for Risk Platform
Provides notebook environment for business users and data scientists
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import logging
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="JupyterHub Management Service",
    description="Service for managing JupyterHub users, notebooks, and integration with Risk Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
JUPYTERHUB_API_URL = os.getenv("JUPYTERHUB_API_URL", "http://jupyterhub-service.default.svc.cluster.local:8081")
JUPYTERHUB_API_TOKEN = os.getenv("JUPYTERHUB_API_TOKEN", "your-jupyterhub-api-token")
RISK_API_URL = os.getenv("RISK_API_URL", "http://fastapi-service.default.svc.cluster.local")

# Pydantic models
class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str  # business_user, data_scientist, admin
    groups: List[str] = []
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    password: Optional[str] = None
    groups: List[str] = []

class NotebookSession(BaseModel):
    user: str
    notebook_path: str
    server_name: str
    status: str
    started_at: datetime
    last_activity: datetime

class NotebookTemplate(BaseModel):
    name: str
    description: str
    path: str
    category: str  # business, data_science, template
    tags: List[str] = []

class UserActivity(BaseModel):
    username: str
    action: str
    resource: str
    timestamp: datetime
    details: Dict[str, Any] = {}

# Global state (in production, use proper database)
users_db: Dict[str, User] = {}
sessions_db: Dict[str, NotebookSession] = {}
activity_log: List[UserActivity] = []

# Utility functions
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    # In production, implement proper JWT token validation
    token = credentials.credentials
    if not token or token != "valid-admin-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

async def jupyterhub_api_request(method: str, endpoint: str, data: Dict = None):
    """Make authenticated request to JupyterHub API"""
    url = f"{JUPYTERHUB_API_URL}{endpoint}"
    headers = {
        "Authorization": f"token {JUPYTERHUB_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            else:
                raise HTTPException(status_code=400, detail="Unsupported HTTP method")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        
        except httpx.HTTPError as e:
            logger.error(f"JupyterHub API request failed: {e}")
            raise HTTPException(status_code=500, detail="JupyterHub API unavailable")

def log_activity(username: str, action: str, resource: str, details: Dict = None):
    """Log user activity"""
    activity = UserActivity(
        username=username,
        action=action,
        resource=resource,
        timestamp=datetime.now(),
        details=details or {}
    )
    activity_log.append(activity)
    logger.info(f"Activity logged: {username} {action} {resource}")

# Health and info endpoints
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "JupyterHub Management Service",
        "version": "1.0.0",
        "description": "Risk Platform notebook environment management",
        "endpoints": {
            "health": "/health",
            "users": "/api/v1/users",
            "sessions": "/api/v1/sessions",
            "notebooks": "/api/v1/notebooks",
            "admin": "/api/v1/admin"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check JupyterHub connectivity
        await jupyterhub_api_request("GET", "/hub/api/")
        jupyterhub_healthy = True
    except:
        jupyterhub_healthy = False
    
    return {
        "status": "healthy" if jupyterhub_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "jupyterhub": "healthy" if jupyterhub_healthy else "unhealthy",
            "risk_api": "healthy"  # In production, check actual connectivity
        },
        "version": "1.0.0"
    }

# User management endpoints
@app.get("/api/v1/users", response_model=List[User])
async def get_users(token: str = Depends(verify_token)):
    """Get all JupyterHub users"""
    try:
        # Get users from JupyterHub API
        hub_users = await jupyterhub_api_request("GET", "/hub/api/users")
        
        # Merge with local user data
        users = []
        for hub_user in hub_users:
            username = hub_user["name"]
            local_user = users_db.get(username)
            
            if local_user:
                users.append(local_user)
            else:
                # Create default user profile
                user = User(
                    username=username,
                    email=f"{username}@company.com",
                    full_name=username.replace("_", " ").title(),
                    role="business_user",
                    is_active=hub_user.get("active", True)
                )
                users.append(user)
        
        return users
    
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@app.post("/api/v1/users", response_model=User)
async def create_user(user_data: UserCreate, token: str = Depends(verify_token)):
    """Create new JupyterHub user"""
    try:
        # Create user in JupyterHub
        hub_user_data = {
            "name": user_data.username,
            "admin": user_data.role == "admin"
        }
        
        await jupyterhub_api_request("POST", f"/hub/api/users/{user_data.username}", hub_user_data)
        
        # Store user profile locally
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            groups=user_data.groups
        )
        users_db[user_data.username] = user
        
        log_activity("admin", "create_user", user_data.username, {"role": user_data.role})
        
        return user
    
    except Exception as e:
        logger.error(f"Failed to create user {user_data.username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/v1/users/{username}", response_model=User)
async def get_user(username: str, token: str = Depends(verify_token)):
    """Get specific user details"""
    if username in users_db:
        return users_db[username]
    
    # Try to get from JupyterHub API
    try:
        hub_user = await jupyterhub_api_request("GET", f"/hub/api/users/{username}")
        user = User(
            username=username,
            email=f"{username}@company.com",
            full_name=username.replace("_", " ").title(),
            role="business_user",
            is_active=hub_user.get("active", True)
        )
        return user
    
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/api/v1/users/{username}")
async def delete_user(username: str, token: str = Depends(verify_token)):
    """Delete user from JupyterHub"""
    try:
        # Delete from JupyterHub
        await jupyterhub_api_request("DELETE", f"/hub/api/users/{username}")
        
        # Remove from local storage
        if username in users_db:
            del users_db[username]
        
        log_activity("admin", "delete_user", username)
        
        return {"message": f"User {username} deleted successfully"}
    
    except Exception as e:
        logger.error(f"Failed to delete user {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Session management endpoints
@app.get("/api/v1/sessions", response_model=List[NotebookSession])
async def get_active_sessions(token: str = Depends(verify_token)):
    """Get all active notebook sessions"""
    try:
        # Get servers from JupyterHub API
        users_data = await jupyterhub_api_request("GET", "/hub/api/users")
        
        sessions = []
        for user_data in users_data:
            username = user_data["name"]
            servers = user_data.get("servers", {})
            
            for server_name, server_info in servers.items():
                if server_info.get("ready"):
                    session = NotebookSession(
                        user=username,
                        notebook_path="",  # Would need to query notebook server API
                        server_name=server_name,
                        status="running",
                        started_at=datetime.fromisoformat(server_info["started"]) if server_info.get("started") else datetime.now(),
                        last_activity=datetime.fromisoformat(server_info["last_activity"]) if server_info.get("last_activity") else datetime.now()
                    )
                    sessions.append(session)
        
        return sessions
    
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")

@app.post("/api/v1/sessions/{username}/start")
async def start_user_server(username: str, token: str = Depends(verify_token)):
    """Start notebook server for user"""
    try:
        await jupyterhub_api_request("POST", f"/hub/api/users/{username}/server")
        
        log_activity(username, "start_server", f"notebook_server")
        
        return {"message": f"Server started for user {username}"}
    
    except Exception as e:
        logger.error(f"Failed to start server for {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start server")

@app.delete("/api/v1/sessions/{username}/stop")
async def stop_user_server(username: str, token: str = Depends(verify_token)):
    """Stop notebook server for user"""
    try:
        await jupyterhub_api_request("DELETE", f"/hub/api/users/{username}/server")
        
        log_activity(username, "stop_server", "notebook_server")
        
        return {"message": f"Server stopped for user {username}"}
    
    except Exception as e:
        logger.error(f"Failed to stop server for {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop server")

# Notebook management endpoints
@app.get("/api/v1/notebooks/templates", response_model=List[NotebookTemplate])
async def get_notebook_templates():
    """Get available notebook templates"""
    templates = [
        NotebookTemplate(
            name="Risk Analysis for Business Users",
            description="Complete risk analysis workflow for business users",
            path="/notebooks/examples/risk_analysis_business_user.ipynb",
            category="business",
            tags=["risk", "portfolio", "analysis"]
        ),
        NotebookTemplate(
            name="Data Science Template",
            description="Framework for data scientists and model developers",
            path="/notebooks/templates/data_science_template.ipynb",
            category="data_science",
            tags=["modeling", "development", "framework"]
        )
    ]
    return templates

@app.post("/api/v1/notebooks/create")
async def create_notebook_from_template(
    username: str,
    template_name: str,
    notebook_name: str,
    token: str = Depends(verify_token)
):
    """Create new notebook from template for user"""
    # In production, this would copy template to user's directory
    log_activity(username, "create_notebook", notebook_name, {"template": template_name})
    
    return {
        "message": f"Notebook {notebook_name} created for {username}",
        "template": template_name,
        "path": f"/home/{username}/{notebook_name}.ipynb"
    }

# Integration endpoints
@app.get("/api/v1/integration/risk-api/status")
async def check_risk_api_integration():
    """Check Risk API connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RISK_API_URL}/health", timeout=5.0)
            response.raise_for_status()
            return {
                "status": "connected",
                "risk_api_url": RISK_API_URL,
                "response": response.json()
            }
    
    except Exception as e:
        return {
            "status": "disconnected",
            "risk_api_url": RISK_API_URL,
            "error": str(e)
        }

@app.get("/api/v1/integration/shared-storage")
async def check_shared_storage():
    """Check shared storage access"""
    storage_paths = [
        "/home/jovyan/shared/data",
        "/home/jovyan/shared/models",
        "/home/jovyan/shared/notebooks"
    ]
    
    status = {}
    for path in storage_paths:
        status[path] = {
            "exists": os.path.exists(path),
            "writable": os.access(path, os.W_OK) if os.path.exists(path) else False
        }
    
    return {"shared_storage": status}

# Admin endpoints
@app.get("/api/v1/admin/stats")
async def get_admin_stats(token: str = Depends(verify_token)):
    """Get administrative statistics"""
    try:
        hub_users = await jupyterhub_api_request("GET", "/hub/api/users")
        
        active_users = sum(1 for user in hub_users if user.get("active", False))
        running_servers = sum(1 for user in hub_users if user.get("servers"))
        
        return {
            "total_users": len(hub_users),
            "active_users": active_users,
            "running_servers": running_servers,
            "recent_activity": len([a for a in activity_log if (datetime.now() - a.timestamp).days < 7])
        }
    
    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.get("/api/v1/admin/activity", response_model=List[UserActivity])
async def get_user_activity(
    limit: int = 100,
    username: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Get user activity log"""
    filtered_activity = activity_log
    
    if username:
        filtered_activity = [a for a in activity_log if a.username == username]
    
    # Sort by timestamp descending and limit
    filtered_activity.sort(key=lambda x: x.timestamp, reverse=True)
    return filtered_activity[:limit]

@app.post("/api/v1/admin/cleanup")
async def cleanup_inactive_sessions(token: str = Depends(verify_token)):
    """Cleanup inactive notebook sessions"""
    try:
        # Get all users and their servers
        users_data = await jupyterhub_api_request("GET", "/hub/api/users")
        
        cleanup_count = 0
        for user_data in users_data:
            username = user_data["name"]
            servers = user_data.get("servers", {})
            
            for server_name, server_info in servers.items():
                # Check if server is inactive (more than 2 hours)
                if server_info.get("last_activity"):
                    last_activity = datetime.fromisoformat(server_info["last_activity"])
                    if (datetime.now() - last_activity).total_seconds() > 7200:  # 2 hours
                        await jupyterhub_api_request("DELETE", f"/hub/api/users/{username}/server/{server_name}")
                        cleanup_count += 1
                        log_activity("system", "cleanup_session", f"{username}/{server_name}")
        
        return {"message": f"Cleaned up {cleanup_count} inactive sessions"}
    
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
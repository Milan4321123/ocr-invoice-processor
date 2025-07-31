"""
Folder Watcher API routes for managing directory monitoring and automatic uploads.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from services.folder_watcher import folder_watcher_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class AddWatchFolderRequest(BaseModel):
    folder_path: str
    pattern: str = "*.pdf"
    recursive: bool = False
    enabled: bool = True

class UpdateWatchFolderRequest(BaseModel):
    pattern: Optional[str] = None
    recursive: Optional[bool] = None
    enabled: Optional[bool] = None

class WatchFolderResponse(BaseModel):
    id: str
    folder_path: str
    pattern: str
    enabled: bool
    recursive: bool
    files_processed: int
    last_scan: Optional[str]
    created_at: str
    is_watching: bool

class WatcherStatusResponse(BaseModel):
    status: str
    uptime_seconds: int
    folders_watched: int
    total_folders_configured: int
    statistics: Dict[str, Any]

# Folder Watcher Management Endpoints

@router.get("/status", response_model=WatcherStatusResponse)
async def get_watcher_status():
    """Get current folder watcher status and statistics"""
    try:
        status_data = folder_watcher_service.get_status()
        return WatcherStatusResponse(
            status=status_data["status"],
            uptime_seconds=status_data["uptime_seconds"],
            folders_watched=status_data["folders_watched"],
            total_folders_configured=status_data["total_folders_configured"],
            statistics=status_data["statistics"]
        )
    except Exception as e:
        logger.error(f"Error getting watcher status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get watcher status: {str(e)}")

@router.post("/start")
async def start_watcher():
    """Start the folder watcher service"""
    try:
        success, error = await folder_watcher_service.start_watcher()
        
        if not success:
            raise HTTPException(status_code=400, detail=error or "Failed to start watcher")
        
        return {
            "success": True,
            "message": "Folder watcher started successfully",
            "status": folder_watcher_service.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting watcher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start watcher: {str(e)}")

@router.post("/stop")
async def stop_watcher():
    """Stop the folder watcher service"""
    try:
        success, error = await folder_watcher_service.stop_watcher()
        
        if not success:
            raise HTTPException(status_code=400, detail=error or "Failed to stop watcher")
        
        return {
            "success": True,
            "message": "Folder watcher stopped successfully",
            "status": folder_watcher_service.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping watcher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop watcher: {str(e)}")

@router.get("/folders", response_model=List[WatchFolderResponse])
async def get_watch_folders():
    """Get list of all configured watch folders"""
    try:
        folders = folder_watcher_service.get_watch_folders()
        return [
            WatchFolderResponse(
                id=folder["id"],
                folder_path=folder["folder_path"],
                pattern=folder["pattern"],
                enabled=folder["enabled"],
                recursive=folder["recursive"],
                files_processed=folder["files_processed"],
                last_scan=folder["last_scan"],
                created_at=folder["created_at"],
                is_watching=folder["is_watching"]
            )
            for folder in folders
        ]
    except Exception as e:
        logger.error(f"Error getting watch folders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get watch folders: {str(e)}")

@router.post("/folders", response_model=Dict[str, Any])
async def add_watch_folder(request: AddWatchFolderRequest):
    """Add a new folder to watch for invoice files"""
    try:
        # Normalize the path to handle any path resolution issues
        from pathlib import Path
        import os
        
        normalized_path = os.path.abspath(os.path.expanduser(request.folder_path))
        folder_path_to_use = normalized_path
        
        success, config_id, error = await folder_watcher_service.add_watch_folder(
            folder_path=folder_path_to_use,
            pattern=request.pattern,
            recursive=request.recursive,
            enabled=request.enabled
        )
        

        
        if not success:
            raise HTTPException(status_code=400, detail=error or "Failed to add watch folder")
        
        return {
            "success": True,
            "message": f"Successfully added watch folder: {request.folder_path}",
            "config_id": config_id,
            "folder_path": request.folder_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding watch folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add watch folder: {str(e)}")

@router.delete("/folders/{config_id}")
async def remove_watch_folder(config_id: str):
    """Remove a watch folder configuration"""
    try:
        success, error = await folder_watcher_service.remove_watch_folder(config_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=error or "Watch folder not found")
        
        return {
            "success": True,
            "message": f"Successfully removed watch folder: {config_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing watch folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove watch folder: {str(e)}")

@router.post("/folders/{config_id}/enable")
async def enable_watch_folder(config_id: str):
    """Enable watching for a specific folder"""
    try:
        success, error = await folder_watcher_service.enable_watch_folder(config_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=error or "Watch folder not found")
        
        return {
            "success": True,
            "message": f"Successfully enabled watch folder: {config_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling watch folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to enable watch folder: {str(e)}")

@router.post("/folders/{config_id}/disable")
async def disable_watch_folder(config_id: str):
    """Disable watching for a specific folder"""
    try:
        success, error = await folder_watcher_service.disable_watch_folder(config_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=error or "Watch folder not found")
        
        return {
            "success": True,
            "message": f"Successfully disabled watch folder: {config_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling watch folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to disable watch folder: {str(e)}")

# Statistics and Information Endpoints

@router.get("/statistics")
async def get_watcher_statistics():
    """Get detailed folder watcher statistics"""
    try:
        status_data = folder_watcher_service.get_status()
        
        return {
            "status": status_data["status"],
            "uptime_seconds": status_data["uptime_seconds"],
            "uptime_formatted": _format_uptime(status_data["uptime_seconds"]),
            "folders": {
                "watched": status_data["folders_watched"],
                "total_configured": status_data["total_folders_configured"],
                "active": len([c for c in status_data["watch_configs"] if c["is_watching"]])
            },
            "processing": status_data["statistics"],
            "watch_configs": status_data["watch_configs"]
        }
    except Exception as e:
        logger.error(f"Error getting watcher statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get watcher statistics: {str(e)}")

@router.get("/health")
async def get_watcher_health():
    """Health check endpoint for folder watcher service"""
    try:
        status_data = folder_watcher_service.get_status()
        
        # Determine health status
        watcher_status = status_data["status"]
        is_healthy = watcher_status in ["running", "stopped"]  # Both are healthy states
        
        health_status = "healthy" if is_healthy else "unhealthy"
        
        return {
            "status": health_status,
            "watcher_status": watcher_status,
            "folders_watching": status_data["folders_watched"],
            "uptime_seconds": status_data["uptime_seconds"],
            "last_activity": status_data["statistics"].get("last_activity"),
            "errors": [] if is_healthy else [f"Watcher in {watcher_status} state"]
        }
    except Exception as e:
        logger.error(f"Error checking watcher health: {str(e)}")
        return {
            "status": "unhealthy",
            "watcher_status": "error",
            "folders_watching": 0,
            "uptime_seconds": 0,
            "last_activity": None,
            "errors": [str(e)]
        }

@router.post("/process-pending")
async def process_pending_files():
    """Manually process any pending files that couldn't be processed automatically"""
    try:
        processed_count = await folder_watcher_service.process_pending_files()
        
        return {
            "success": True,
            "message": f"Processed {processed_count} pending files",
            "files_processed": processed_count
        }
    except Exception as e:
        logger.error(f"Error processing pending files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process pending files: {str(e)}")

@router.get("/notifications")
async def get_notifications(limit: int = Query(20, description="Number of recent notifications to return")):
    """Get recent file processing notifications"""
    try:
        notifications = folder_watcher_service.get_notifications(limit=limit)
        return {
            "success": True,
            "notifications": notifications,
            "total": len(notifications)
        }
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.delete("/notifications")
async def clear_notifications():
    """Clear all file processing notifications"""
    try:
        folder_watcher_service.clear_notifications()
        return {
            "success": True,
            "message": "All notifications cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear notifications: {str(e)}")

# Utility Functions

def _format_uptime(seconds: int) -> str:
    """Format uptime seconds into human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

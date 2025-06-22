"""
Folder Watcher Service for automatic invoice processing.
Monitors specified directories for new PDF files and automatically uploads them.
"""
import os
import asyncio
import logging
import uuid
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from services.upload_service import upload_service, FileData, UploadSource

logger = logging.getLogger(__name__)

class WatcherStatus(Enum):
    """Status of the folder watcher"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class WatchConfig:
    """Configuration for a watched folder"""
    id: str
    folder_path: str
    pattern: str = "*.pdf"
    enabled: bool = True
    recursive: bool = False
    cooldown_seconds: int = 5  # Prevent duplicate processing
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    last_scan: Optional[str] = None
    files_processed: int = 0

@dataclass
class WatcherStats:
    """Statistics for folder watcher"""
    total_files_processed: int = 0
    successful_uploads: int = 0
    failed_uploads: int = 0
    folders_watched: int = 0
    uptime_seconds: int = 0
    last_activity: Optional[str] = None

class InvoiceFileHandler(FileSystemEventHandler):
    """Handles file system events for invoice processing"""
    
    def __init__(self, folder_watcher_service, watch_config: WatchConfig):
        super().__init__()
        self.folder_watcher = folder_watcher_service
        self.watch_config = watch_config
        self.processed_files: Set[str] = set()
        self.processing_queue: Dict[str, float] = {}  # file_path -> timestamp
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "created")
    
    def on_modified(self, event):
        """Handle file modification events (sometimes files are written in chunks)"""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "modified")
    
    def _handle_file_event(self, file_path: str, event_type: str):
        """Process file system events"""
        try:
            # Convert to Path object for easier handling
            path = Path(file_path)
            
            # Check if it's a PDF file
            if not path.suffix.lower() == '.pdf':
                return
            
            # Check if file exists (might be deleted quickly)
            if not path.exists():
                return
            
            # Prevent duplicate processing with cooldown
            current_time = time.time()
            if file_path in self.processing_queue:
                last_processed = self.processing_queue[file_path]
                if current_time - last_processed < self.watch_config.cooldown_seconds:
                    logger.debug(f"Skipping {file_path} - still in cooldown period")
                    return
            
            # Add to processing queue
            self.processing_queue[file_path] = current_time
            
            # Clean up old entries from processing queue
            cutoff_time = current_time - (self.watch_config.cooldown_seconds * 2)
            self.processing_queue = {
                k: v for k, v in self.processing_queue.items() 
                if v > cutoff_time
            }
            
            logger.info(f"Detected {event_type} event for PDF: {file_path}")
            
            # Schedule async processing using thread-safe approach
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule coroutine to run soon in the existing loop
                    asyncio.run_coroutine_threadsafe(
                        self._process_file_async(file_path), loop
                    )
                else:
                    # No running loop, create task normally
                    asyncio.create_task(self._process_file_async(file_path))
            except RuntimeError:
                # No event loop in current thread, schedule for later processing
                logger.warning(f"No event loop available, queuing file for later processing: {file_path}")
                # Add to a processing queue that can be handled by the main service
                if hasattr(self.folder_watcher, '_pending_files'):
                    self.folder_watcher._pending_files.add(file_path)
                else:
                    self.folder_watcher._pending_files = {file_path}
            
        except Exception as e:
            logger.error(f"Error handling file event for {file_path}: {str(e)}")
    
    async def _process_file_async(self, file_path: str):
        """Asynchronously process detected file"""
        try:
            # Wait a bit to ensure file is fully written
            await asyncio.sleep(2)
            
            # Check if file still exists and is readable
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File no longer exists: {file_path}")
                return
            
            # Read file content
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
            except (IOError, PermissionError) as e:
                logger.error(f"Cannot read file {file_path}: {str(e)}")
                return
            
            if len(content) == 0:
                logger.warning(f"File is empty: {file_path}")
                return
            
            # Create FileData for upload service
            file_data = FileData(
                content=content,
                filename=path.name,
                content_type="application/pdf",
                file_size=len(content),
                source=UploadSource.FOLDER_WATCHER,
                source_metadata={
                    "folder_path": str(path.parent),
                    "original_path": file_path,
                    "detected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "watch_config_id": self.watch_config.id
                }
            )
            
            # Upload using common upload service
            result = await upload_service.upload_file(file_data)
            
            if result.success:
                logger.info(f"Successfully uploaded {path.name} from folder watcher")
                logger.info(f"  Invoice ID: {result.invoice_id}")
                logger.info(f"  Storage URL: {result.url}")
                
                # Update statistics
                self.folder_watcher.stats.successful_uploads += 1
                self.folder_watcher.stats.total_files_processed += 1
                self.folder_watcher.stats.last_activity = time.strftime("%Y-%m-%d %H:%M:%S")
                self.watch_config.files_processed += 1
                
                # Mark as processed
                self.processed_files.add(file_path)
                
            else:
                logger.error(f"Failed to upload {path.name}: {result.error}")
                self.folder_watcher.stats.failed_uploads += 1
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            self.folder_watcher.stats.failed_uploads += 1

class FolderWatcherService:
    """Main folder watcher service"""
    
    def __init__(self):
        self.status = WatcherStatus.STOPPED
        self.watch_configs: Dict[str, WatchConfig] = {}
        self.observers: Dict[str, Observer] = {}
        self.handlers: Dict[str, InvoiceFileHandler] = {}
        self.stats = WatcherStats()
        self.start_time: Optional[float] = None
        self._lock = asyncio.Lock()
        self._pending_files: Set[str] = set()  # Files queued for processing
    
    async def add_watch_folder(self, folder_path: str, pattern: str = "*.pdf", 
                             recursive: bool = False, enabled: bool = True) -> Tuple[bool, str, Optional[str]]:
        """
        Add a folder to watch for new files
        Returns (success, config_id, error_message)
        """
        try:
            # Validate folder path
            path = Path(folder_path)
            if not path.exists():
                return False, "", f"Folder does not exist: {folder_path}"
            
            if not path.is_dir():
                return False, "", f"Path is not a directory: {folder_path}"
            
            # Check if folder is already being watched
            for config in self.watch_configs.values():
                if config.folder_path == str(path.resolve()):
                    return False, "", f"Folder is already being watched: {folder_path}"
            
            # Create watch configuration
            config_id = str(uuid.uuid4())
            watch_config = WatchConfig(
                id=config_id,
                folder_path=str(path.resolve()),
                pattern=pattern,
                enabled=enabled,
                recursive=recursive
            )
            
            self.watch_configs[config_id] = watch_config
            
            # If watcher is running, start watching this folder immediately
            if self.status == WatcherStatus.RUNNING and enabled:
                await self._start_watching_folder(config_id)
            
            logger.info(f"Added watch folder: {folder_path} (ID: {config_id})")
            return True, config_id, None
            
        except Exception as e:
            logger.error(f"Error adding watch folder {folder_path}: {str(e)}")
            return False, "", str(e)
    
    async def remove_watch_folder(self, config_id: str) -> Tuple[bool, Optional[str]]:
        """
        Remove a folder from watching
        Returns (success, error_message)
        """
        try:
            if config_id not in self.watch_configs:
                return False, f"Watch configuration not found: {config_id}"
            
            # Stop watching this folder if currently active
            if config_id in self.observers:
                await self._stop_watching_folder(config_id)
            
            # Remove configuration
            config = self.watch_configs.pop(config_id)
            logger.info(f"Removed watch folder: {config.folder_path}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error removing watch folder {config_id}: {str(e)}")
            return False, str(e)
    
    async def start_watcher(self) -> Tuple[bool, Optional[str]]:
        """
        Start the folder watcher service
        Returns (success, error_message)
        """
        async with self._lock:
            try:
                if self.status == WatcherStatus.RUNNING:
                    return True, None  # Already running
                
                if self.status == WatcherStatus.STARTING:
                    return False, "Watcher is already starting"
                
                self.status = WatcherStatus.STARTING
                self.start_time = time.time()
                
                logger.info("Starting folder watcher service...")
                
                # Start watching all enabled folders
                for config_id, config in self.watch_configs.items():
                    if config.enabled:
                        await self._start_watching_folder(config_id)
                
                self.status = WatcherStatus.RUNNING
                self.stats.folders_watched = len([c for c in self.watch_configs.values() if c.enabled])
                
                logger.info(f"Folder watcher started successfully - watching {self.stats.folders_watched} folders")
                return True, None
                
            except Exception as e:
                self.status = WatcherStatus.ERROR
                logger.error(f"Error starting folder watcher: {str(e)}")
                return False, str(e)
    
    async def stop_watcher(self) -> Tuple[bool, Optional[str]]:
        """
        Stop the folder watcher service
        Returns (success, error_message)
        """
        async with self._lock:
            try:
                if self.status == WatcherStatus.STOPPED:
                    return True, None  # Already stopped
                
                if self.status == WatcherStatus.STOPPING:
                    return False, "Watcher is already stopping"
                
                self.status = WatcherStatus.STOPPING
                
                logger.info("Stopping folder watcher service...")
                
                # Stop all observers
                for config_id in list(self.observers.keys()):
                    await self._stop_watching_folder(config_id)
                
                self.status = WatcherStatus.STOPPED
                self.start_time = None
                
                logger.info("Folder watcher stopped successfully")
                return True, None
                
            except Exception as e:
                self.status = WatcherStatus.ERROR
                logger.error(f"Error stopping folder watcher: {str(e)}")
                return False, str(e)
    
    async def _start_watching_folder(self, config_id: str):
        """Start watching a specific folder"""
        try:
            config = self.watch_configs[config_id]
            
            # Create file handler
            handler = InvoiceFileHandler(self, config)
            self.handlers[config_id] = handler
            
            # Create and start observer
            observer = Observer()
            observer.schedule(handler, config.folder_path, recursive=config.recursive)
            observer.start()
            
            self.observers[config_id] = observer
            config.last_scan = time.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"Started watching folder: {config.folder_path}")
            
        except Exception as e:
            logger.error(f"Error starting watch for folder {config_id}: {str(e)}")
            # Clean up on error
            if config_id in self.observers:
                self.observers[config_id].stop()
                del self.observers[config_id]
            if config_id in self.handlers:
                del self.handlers[config_id]
    
    async def _stop_watching_folder(self, config_id: str):
        """Stop watching a specific folder"""
        try:
            if config_id in self.observers:
                observer = self.observers[config_id]
                observer.stop()
                observer.join(timeout=5)  # Wait up to 5 seconds
                del self.observers[config_id]
            
            if config_id in self.handlers:
                del self.handlers[config_id]
            
            if config_id in self.watch_configs:
                config = self.watch_configs[config_id]
                logger.info(f"Stopped watching folder: {config.folder_path}")
                
        except Exception as e:
            logger.error(f"Error stopping watch for folder {config_id}: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current watcher status and statistics"""
        # Update uptime
        if self.start_time and self.status == WatcherStatus.RUNNING:
            self.stats.uptime_seconds = int(time.time() - self.start_time)
        
        return {
            "status": self.status.value,
            "uptime_seconds": self.stats.uptime_seconds,
            "folders_watched": len([c for c in self.watch_configs.values() if c.enabled]),
            "total_folders_configured": len(self.watch_configs),
            "statistics": {
                "total_files_processed": self.stats.total_files_processed,
                "successful_uploads": self.stats.successful_uploads,
                "failed_uploads": self.stats.failed_uploads,
                "last_activity": self.stats.last_activity
            },
            "watch_configs": [
                {
                    "id": config.id,
                    "folder_path": config.folder_path,
                    "pattern": config.pattern,
                    "enabled": config.enabled,
                    "recursive": config.recursive,
                    "files_processed": config.files_processed,
                    "last_scan": config.last_scan,
                    "created_at": config.created_at,
                    "is_watching": config.id in self.observers
                }
                for config in self.watch_configs.values()
            ]
        }
    
    def get_watch_folders(self) -> List[Dict[str, Any]]:
        """Get list of configured watch folders"""
        return [
            {
                "id": config.id,
                "folder_path": config.folder_path,
                "pattern": config.pattern,
                "enabled": config.enabled,
                "recursive": config.recursive,
                "files_processed": config.files_processed,
                "last_scan": config.last_scan,
                "created_at": config.created_at,
                "is_watching": config.id in self.observers
            }
            for config in self.watch_configs.values()
        ]
    
    async def enable_watch_folder(self, config_id: str) -> Tuple[bool, Optional[str]]:
        """Enable watching for a specific folder"""
        try:
            if config_id not in self.watch_configs:
                return False, f"Watch configuration not found: {config_id}"
            
            config = self.watch_configs[config_id]
            config.enabled = True
            
            # If watcher is running, start watching this folder
            if self.status == WatcherStatus.RUNNING and config_id not in self.observers:
                await self._start_watching_folder(config_id)
            
            logger.info(f"Enabled watch folder: {config.folder_path}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error enabling watch folder {config_id}: {str(e)}")
            return False, str(e)
    
    async def disable_watch_folder(self, config_id: str) -> Tuple[bool, Optional[str]]:
        """Disable watching for a specific folder"""
        try:
            if config_id not in self.watch_configs:
                return False, f"Watch configuration not found: {config_id}"
            
            config = self.watch_configs[config_id]
            config.enabled = False
            
            # Stop watching this folder if currently active
            if config_id in self.observers:
                await self._stop_watching_folder(config_id)
            
            logger.info(f"Disabled watch folder: {config.folder_path}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error disabling watch folder {config_id}: {str(e)}")
            return False, str(e)

# Global instance
folder_watcher_service = FolderWatcherService()

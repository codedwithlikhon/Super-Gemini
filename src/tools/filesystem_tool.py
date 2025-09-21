"""
File system operations tool.
"""
from pathlib import Path
import aiofiles
import json
from typing import Dict, Any, Optional, Union
import os
import shutil

class FileSystemTool:
    """Tool for safe file system operations."""
    
    def __init__(self, root_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the file system tool.
        
        Args:
            root_dir: Optional root directory to restrict operations
        """
        self.root_dir = Path(root_dir) if root_dir else None
        
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate and normalize a file path.
        
        Args:
            path: Path to validate
            
        Returns:
            Path: Normalized path object
            
        Raises:
            ValueError: If path is outside root_dir (if set)
        """
        path = Path(path).resolve()
        
        if self.root_dir:
            try:
                path.relative_to(self.root_dir)
            except ValueError:
                raise ValueError(f"Path '{path}' is outside root directory")
                
        return path
        
    async def read_file(self, path: Union[str, Path], 
                       encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read a file safely.
        
        Args:
            path: Path to file
            encoding: File encoding
            
        Returns:
            Dict containing file content
        """
        try:
            path = self._validate_path(path)
            
            if not path.is_file():
                return {
                    "status": "error",
                    "error": f"File '{path}' does not exist",
                    "path": str(path)
                }
                
            async with aiofiles.open(path, mode='r', encoding=encoding) as f:
                content = await f.read()
                
            return {
                "status": "success",
                "content": content,
                "path": str(path),
                "size": path.stat().st_size
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(path)
            }
            
    async def write_file(self, path: Union[str, Path], content: str,
                        encoding: str = 'utf-8', mode: str = 'w') -> Dict[str, Any]:
        """
        Write content to a file safely.
        
        Args:
            path: Path to file
            content: Content to write
            encoding: File encoding
            mode: File open mode ('w' or 'a')
            
        Returns:
            Dict containing operation result
        """
        try:
            path = self._validate_path(path)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, mode=mode, encoding=encoding) as f:
                await f.write(content)
                
            return {
                "status": "success",
                "path": str(path),
                "size": path.stat().st_size,
                "mode": mode
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(path)
            }
            
    def list_directory(self, path: Union[str, Path], 
                      pattern: str = "*") -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path
            pattern: Optional glob pattern
            
        Returns:
            Dict containing directory listing
        """
        try:
            path = self._validate_path(path)
            
            if not path.is_dir():
                return {
                    "status": "error",
                    "error": f"'{path}' is not a directory",
                    "path": str(path)
                }
                
            items = []
            for item in path.glob(pattern):
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
                
            return {
                "status": "success",
                "path": str(path),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(path)
            }
            
    def remove(self, path: Union[str, Path], recursive: bool = False) -> Dict[str, Any]:
        """
        Remove a file or directory.
        
        Args:
            path: Path to remove
            recursive: Allow recursive directory removal
            
        Returns:
            Dict containing operation result
        """
        try:
            path = self._validate_path(path)
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"Path '{path}' does not exist",
                    "path": str(path)
                }
                
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                if recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()
                    
            return {
                "status": "success",
                "path": str(path),
                "type": "directory" if path.is_dir() else "file"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": str(path)
            }
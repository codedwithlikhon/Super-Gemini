"""
Time and timezone handling tool.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional
import re

class TimeTool:
    """Tool for time operations and timezone conversions."""
    
    def __init__(self):
        """Initialize the time tool."""
        pass
        
    def get_current_time(self, tz: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current time, optionally in specific timezone.
        
        Args:
            tz: Optional timezone name (e.g. 'America/New_York')
            
        Returns:
            Dict containing time information
        """
        try:
            now = datetime.now(timezone.utc)
            
            if tz:
                # Convert to requested timezone
                now = now.astimezone(ZoneInfo(tz))
                
            return {
                "status": "success",
                "timestamp": now.timestamp(),
                "iso": now.isoformat(),
                "timezone": str(now.tzinfo),
                "components": {
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                    "hour": now.hour,
                    "minute": now.minute,
                    "second": now.second,
                    "microsecond": now.microsecond
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def convert_timezone(self, dt: str, from_tz: str, 
                        to_tz: str) -> Dict[str, Any]:
        """
        Convert time between timezones.
        
        Args:
            dt: Datetime string (ISO format)
            from_tz: Source timezone
            to_tz: Target timezone
            
        Returns:
            Dict containing converted time
        """
        try:
            # Parse input datetime
            dt_obj = datetime.fromisoformat(dt)
            
            # Add source timezone if not present
            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=ZoneInfo(from_tz))
            
            # Convert to target timezone
            converted = dt_obj.astimezone(ZoneInfo(to_tz))
            
            return {
                "status": "success",
                "original": {
                    "datetime": dt,
                    "timezone": from_tz
                },
                "converted": {
                    "datetime": converted.isoformat(),
                    "timezone": to_tz,
                    "components": {
                        "year": converted.year,
                        "month": converted.month,
                        "day": converted.day,
                        "hour": converted.hour,
                        "minute": converted.minute,
                        "second": converted.second,
                        "microsecond": converted.microsecond
                    }
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def parse_datetime(self, text: str) -> Dict[str, Any]:
        """
        Extract datetime from natural language text.
        
        Args:
            text: Text containing datetime information
            
        Returns:
            Dict containing extracted datetime
        """
        try:
            # Simple pattern matching for common formats
            patterns = [
                # ISO format
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
                # Date only
                r'(\d{4}-\d{2}-\d{2})',
                # Time only
                r'(\d{2}:\d{2}(?::\d{2})?)',
                # American format
                r'(\d{1,2}/\d{1,2}/\d{4})',
                # European format
                r'(\d{1,2}\.\d{1,2}\.\d{4})'
            ]
            
            results = []
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    try:
                        dt = datetime.fromisoformat(match.group(1))
                        results.append({
                            "text": match.group(1),
                            "parsed": dt.isoformat(),
                            "pattern": pattern
                        })
                    except:
                        continue
                        
            return {
                "status": "success",
                "matches": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
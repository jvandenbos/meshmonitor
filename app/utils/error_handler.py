"""Centralized error handling utilities."""

import logging
import traceback
from typing import Any, Optional, Dict
from datetime import datetime


class MeshtasticError(Exception):
    """Base exception for Meshtastic server errors."""
    pass


class DeviceConnectionError(MeshtasticError):
    """Raised when device connection fails."""
    pass


class MessageProcessingError(MeshtasticError):
    """Raised when message processing fails."""
    pass


class DataValidationError(MeshtasticError):
    """Raised when data validation fails."""
    pass


class ErrorHandler:
    """Centralized error handler with logging and recovery strategies."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, Dict[str, Any]] = {}
    
    def handle_error(
        self,
        error: Exception,
        context: str,
        data: Optional[Dict[str, Any]] = None,
        critical: bool = False
    ) -> None:
        """Handle an error with appropriate logging and tracking."""
        error_type = type(error).__name__
        
        # Track error frequency
        error_key = f"{context}:{error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Store error details
        self.last_errors[error_key] = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "traceback": traceback.format_exc(),
            "data": data,
            "count": self.error_counts[error_key]
        }
        
        # Log appropriately
        if critical:
            self.logger.critical(
                f"CRITICAL ERROR in {context}: {error_type} - {error}",
                extra={"data": data, "traceback": traceback.format_exc()}
            )
        elif self.error_counts[error_key] > 10:
            self.logger.error(
                f"Recurring error in {context} (count: {self.error_counts[error_key]}): {error_type} - {error}",
                extra={"data": data}
            )
        else:
            self.logger.warning(
                f"Error in {context}: {error_type} - {error}",
                extra={"data": data}
            )
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "error_counts": self.error_counts,
            "recent_errors": list(self.last_errors.values())[-10:],  # Last 10 errors
            "total_errors": sum(self.error_counts.values())
        }
    
    def reset_error_counts(self) -> None:
        """Reset error counters (useful for periodic cleanup)."""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
error_handler = ErrorHandler()
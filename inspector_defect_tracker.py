"""
Inspector Defect Tracker Module
Task 3.2.2: Inspector Defect Tracker

This module provides comprehensive defect tracking capabilities for the Inspector system,
including defect categorization, tracking, and management.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import uuid
from collections import defaultdict

from inspector_config_manager import InspectorConfigManager


class DefectSeverity(Enum):
    """Defect severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINOR = "minor"


class DefectStatus(Enum):
    """Defect status values."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    WONT_FIX = "wont_fix"


class DefectCategory(Enum):
    """Defect categories."""
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPATIBILITY = "compatibility"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class DefectPriority(Enum):
    """Defect priority levels."""
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FUTURE = "future"


@dataclass
class Defect:
    """Defect data structure."""
    id: str
    title: str
    description: str
    severity: DefectSeverity
    priority: DefectPriority
    category: DefectCategory
    status: DefectStatus
    created_at: datetime
    updated_at: datetime
    reported_by: str
    assigned_to: Optional[str] = None
    component: Optional[str] = None
    version: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment: Optional[str] = None
    tags: List[str] = None
    attachments: List[str] = None
    comments: List[Dict[str, Any]] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    estimated_effort: Optional[str] = None
    actual_effort: Optional[str] = None
    related_defects: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tags is None:
            self.tags = []
        if self.attachments is None:
            self.attachments = []
        if self.comments is None:
            self.comments = []
        if self.related_defects is None:
            self.related_defects = []


@dataclass
class DefectStatistics:
    """Defect statistics."""
    total_defects: int
    open_defects: int
    resolved_defects: int
    closed_defects: int
    critical_defects: int
    high_priority_defects: int
    defects_by_category: Dict[DefectCategory, int]
    defects_by_severity: Dict[DefectSeverity, int]
    defects_by_status: Dict[DefectStatus, int]
    average_resolution_time: Optional[float] = None
    resolution_rate: Optional[float] = None


class InspectorDefectTracker:
    """
    Comprehensive defect tracking system for the Inspector.
    
    Provides defect tracking, categorization, and management capabilities.
    """
    
    def __init__(self, config_manager: InspectorConfigManager):
        """Initialize the defect tracker."""
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Defect storage
        self.defects: Dict[str, Defect] = {}
        
        # Ensure data directory exists
        self.data_dir = Path("results/inspector/defects")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing defects
        self._load_defects()
    
    def create_defect(self, title: str, description: str, severity: DefectSeverity,
                     priority: DefectPriority, category: DefectCategory,
                     reported_by: str, **kwargs) -> str:
        """Create a new defect."""
        defect_id = str(uuid.uuid4())
        now = datetime.now()
        
        defect = Defect(
            id=defect_id,
            title=title,
            description=description,
            severity=severity,
            priority=priority,
            category=category,
            status=DefectStatus.OPEN,
            created_at=now,
            updated_at=now,
            reported_by=reported_by,
            **kwargs
        )
        
        self.defects[defect_id] = defect
        self.logger.info(f"Created defect {defect_id}: {title}")
        
        # Save defects
        self._save_defects()
        
        return defect_id
    
    def get_defect(self, defect_id: str) -> Optional[Defect]:
        """Get a defect by ID."""
        return self.defects.get(defect_id)
    
    def update_defect(self, defect_id: str, **kwargs) -> bool:
        """Update a defect."""
        if defect_id not in self.defects:
            return False
        
        defect = self.defects[defect_id]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(defect, key):
                setattr(defect, key, value)
        
        # Update timestamp
        defect.updated_at = datetime.now()
        
        # Handle status changes
        if 'status' in kwargs:
            new_status = kwargs['status']
            if new_status == DefectStatus.RESOLVED:
                defect.resolved_at = datetime.now()
                defect.resolved_by = kwargs.get('resolved_by', defect.assigned_to)
            elif new_status == DefectStatus.REOPENED:
                defect.resolved_at = None
                defect.resolved_by = None
        
        self.logger.info(f"Updated defect {defect_id}")
        
        # Save defects
        self._save_defects()
        
        return True
    
    def add_comment(self, defect_id: str, comment: str, author: str) -> bool:
        """Add a comment to a defect."""
        if defect_id not in self.defects:
            return False
        
        defect = self.defects[defect_id]
        
        comment_data = {
            "id": str(uuid.uuid4()),
            "comment": comment,
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
        
        defect.comments.append(comment_data)
        defect.updated_at = datetime.now()
        
        self.logger.info(f"Added comment to defect {defect_id}")
        
        # Save defects
        self._save_defects()
        
        return True
    
    def search_defects(self, **filters) -> List[Defect]:
        """Search defects based on filters."""
        results = []
        
        for defect in self.defects.values():
            match = True
            
            for key, value in filters.items():
                if hasattr(defect, key):
                    defect_value = getattr(defect, key)
                    if isinstance(value, list):
                        if defect_value not in value:
                            match = False
                            break
                    else:
                        if defect_value != value:
                            match = False
                            break
                else:
                    match = False
                    break
            
            if match:
                results.append(defect)
        
        return results
    
    def get_defects_by_status(self, status: DefectStatus) -> List[Defect]:
        """Get defects by status."""
        return self.search_defects(status=status)
    
    def get_defects_by_severity(self, severity: DefectSeverity) -> List[Defect]:
        """Get defects by severity."""
        return self.search_defects(severity=severity)
    
    def get_defects_by_category(self, category: DefectCategory) -> List[Defect]:
        """Get defects by category."""
        return self.search_defects(category=category)
    
    def get_critical_defects(self) -> List[Defect]:
        """Get critical defects."""
        return self.search_defects(severity=DefectSeverity.CRITICAL)
    
    def get_high_priority_defects(self) -> List[Defect]:
        """Get high priority defects."""
        return self.search_defects(priority=DefectPriority.HIGH)
    
    def get_open_defects(self) -> List[Defect]:
        """Get open defects."""
        return self.search_defects(status=DefectStatus.OPEN)
    
    def get_defect_statistics(self) -> DefectStatistics:
        """Get defect statistics."""
        total_defects = len(self.defects)
        open_defects = len(self.get_open_defects())
        resolved_defects = len(self.search_defects(status=DefectStatus.RESOLVED))
        closed_defects = len(self.search_defects(status=DefectStatus.CLOSED))
        critical_defects = len(self.get_critical_defects())
        high_priority_defects = len(self.get_high_priority_defects())
        
        # Count by category
        defects_by_category = defaultdict(int)
        for defect in self.defects.values():
            defects_by_category[defect.category] += 1
        
        # Count by severity
        defects_by_severity = defaultdict(int)
        for defect in self.defects.values():
            defects_by_severity[defect.severity] += 1
        
        # Count by status
        defects_by_status = defaultdict(int)
        for defect in self.defects.values():
            defects_by_status[defect.status] += 1
        
        # Calculate average resolution time
        resolved_defects_with_time = [
            defect for defect in self.defects.values()
            if defect.status == DefectStatus.RESOLVED and defect.resolved_at
        ]
        
        if resolved_defects_with_time:
            total_resolution_time = sum(
                (defect.resolved_at - defect.created_at).total_seconds()
                for defect in resolved_defects_with_time
            )
            average_resolution_time = total_resolution_time / len(resolved_defects_with_time)
        else:
            average_resolution_time = None
        
        # Calculate resolution rate
        if total_defects > 0:
            resolution_rate = (resolved_defects + closed_defects) / total_defects
        else:
            resolution_rate = None
        
        return DefectStatistics(
            total_defects=total_defects,
            open_defects=open_defects,
            resolved_defects=resolved_defects,
            closed_defects=closed_defects,
            critical_defects=critical_defects,
            high_priority_defects=high_priority_defects,
            defects_by_category=dict(defects_by_category),
            defects_by_severity=dict(defects_by_severity),
            defects_by_status=dict(defects_by_status),
            average_resolution_time=average_resolution_time,
            resolution_rate=resolution_rate
        )
    
    def export_defects(self, format: str = "json", **filters) -> str:
        """Export defects in specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter defects
        defects_to_export = self.search_defects(**filters) if filters else list(self.defects.values())
        
        if format.lower() == "json":
            filename = f"defects_export_{timestamp}.json"
            filepath = self.data_dir / filename
            
            # Convert defects to serializable format
            defects_data = []
            for defect in defects_to_export:
                defect_dict = asdict(defect)
                # Convert datetime objects to ISO format
                defect_dict["created_at"] = defect.created_at.isoformat()
                defect_dict["updated_at"] = defect.updated_at.isoformat()
                if defect.resolved_at:
                    defect_dict["resolved_at"] = defect.resolved_at.isoformat()
                
                # Convert enum values to strings
                defect_dict["severity"] = defect.severity.value
                defect_dict["priority"] = defect.priority.value
                defect_dict["category"] = defect.category.value
                defect_dict["status"] = defect.status.value
                
                defects_data.append(defect_dict)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(defects_data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            filename = f"defects_export_{timestamp}.csv"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                # Write header
                f.write("ID,Title,Description,Severity,Priority,Category,Status,Created,Updated,Reported By,Assigned To,Component,Version,Resolution\n")
                
                # Write data
                for defect in defects_to_export:
                    resolution = defect.resolution.replace('"', '""') if defect.resolution else ""
                    f.write(f'"{defect.id}","{defect.title}","{defect.description}","{defect.severity.value}","{defect.priority.value}","{defect.category.value}","{defect.status.value}","{defect.created_at.isoformat()}","{defect.updated_at.isoformat()}","{defect.reported_by}","{defect.assigned_to or ""}","{defect.component or ""}","{defect.version or ""}","{resolution}"\n')
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Exported {len(defects_to_export)} defects to {filepath}")
        return str(filepath)
    
    def generate_defect_report(self, period: str = "current") -> Dict[str, Any]:
        """Generate a comprehensive defect report."""
        stats = self.get_defect_statistics()
        
        # Get recent defects
        cutoff_time = datetime.now() - timedelta(days=30)
        recent_defects = [
            defect for defect in self.defects.values()
            if defect.created_at >= cutoff_time
        ]
        
        # Get defect trends
        daily_defects = defaultdict(int)
        for defect in recent_defects:
            day = defect.created_at.date()
            daily_defects[day] += 1
        
        # Get top categories
        top_categories = sorted(
            stats.defects_by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get top components
        component_defects = defaultdict(int)
        for defect in self.defects.values():
            if defect.component:
                component_defects[defect.component] += 1
        
        top_components = sorted(
            component_defects.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        report = {
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_defects": stats.total_defects,
                "open_defects": stats.open_defects,
                "resolved_defects": stats.resolved_defects,
                "closed_defects": stats.closed_defects,
                "critical_defects": stats.critical_defects,
                "high_priority_defects": stats.high_priority_defects,
                "resolution_rate": stats.resolution_rate,
                "average_resolution_time": stats.average_resolution_time
            },
            "defects_by_category": dict(stats.defects_by_category),
            "defects_by_severity": dict(stats.defects_by_severity),
            "defects_by_status": dict(stats.defects_by_status),
            "top_categories": top_categories,
            "top_components": top_components,
            "daily_trends": dict(daily_defects),
            "recent_defects": [
                {
                    "id": defect.id,
                    "title": defect.title,
                    "severity": defect.severity.value,
                    "priority": defect.priority.value,
                    "status": defect.status.value,
                    "created_at": defect.created_at.isoformat()
                }
                for defect in sorted(recent_defects, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }
        
        return report
    
    def _save_defects(self) -> None:
        """Save defects to file."""
        filepath = self.data_dir / "defects.json"
        
        # Convert defects to serializable format
        defects_data = []
        for defect in self.defects.values():
            defect_dict = asdict(defect)
            # Convert datetime objects to ISO format
            defect_dict["created_at"] = defect.created_at.isoformat()
            defect_dict["updated_at"] = defect.updated_at.isoformat()
            if defect.resolved_at:
                defect_dict["resolved_at"] = defect.resolved_at.isoformat()
            
            # Convert enum values to strings
            defect_dict["severity"] = defect.severity.value
            defect_dict["priority"] = defect.priority.value
            defect_dict["category"] = defect.category.value
            defect_dict["status"] = defect.status.value
            
            defects_data.append(defect_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(defects_data, f, indent=2, ensure_ascii=False)
        
        self.logger.debug(f"Saved {len(self.defects)} defects to {filepath}")
    
    def _load_defects(self) -> None:
        """Load defects from file."""
        filepath = self.data_dir / "defects.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                defects_data = json.load(f)
            
            for defect_data in defects_data:
                # Convert ISO format back to datetime
                defect_data["created_at"] = datetime.fromisoformat(defect_data["created_at"])
                defect_data["updated_at"] = datetime.fromisoformat(defect_data["updated_at"])
                if defect_data.get("resolved_at"):
                    defect_data["resolved_at"] = datetime.fromisoformat(defect_data["resolved_at"])
                
                # Convert enum values
                defect_data["severity"] = DefectSeverity(defect_data["severity"])
                defect_data["priority"] = DefectPriority(defect_data["priority"])
                defect_data["category"] = DefectCategory(defect_data["category"])
                defect_data["status"] = DefectStatus(defect_data["status"])
                
                defect = Defect(**defect_data)
                self.defects[defect.id] = defect
            
            self.logger.info(f"Loaded {len(self.defects)} defects from {filepath}")
        
        except Exception as e:
            self.logger.error(f"Error loading defects: {e}")


def main():
    """Main function for testing the defect tracker module."""
    # Initialize configuration manager
    config_manager = InspectorConfigManager()
    
    # Initialize defect tracker
    tracker = InspectorDefectTracker(config_manager)
    
    # Create sample defects
    defect1_id = tracker.create_defect(
        title="MCP Server Performance Issues",
        description="Server response times are consistently above 20 seconds",
        severity=DefectSeverity.CRITICAL,
        priority=DefectPriority.IMMEDIATE,
        category=DefectCategory.PERFORMANCE,
        reported_by="test_performance.py",
        component="mcp_server",
        version="1.0.0",
        steps_to_reproduce="Run concurrent tool execution tests",
        expected_behavior="Response times under 1 second",
        actual_behavior="Response times 20-27 seconds",
        environment="Windows 10, Python 3.9"
    )
    
    defect2_id = tracker.create_defect(
        title="Tool Registration Inconsistencies",
        description="Some tools fail to register properly",
        severity=DefectSeverity.HIGH,
        priority=DefectPriority.HIGH,
        category=DefectCategory.FUNCTIONALITY,
        reported_by="test_tool_registration.py",
        component="tool_manager",
        version="1.0.0"
    )
    
    defect3_id = tracker.create_defect(
        title="Documentation Missing",
        description="Several modules lack proper documentation",
        severity=DefectSeverity.MEDIUM,
        priority=DefectPriority.MEDIUM,
        category=DefectCategory.DOCUMENTATION,
        reported_by="code_review",
        component="inspector_modules"
    )
    
    # Add comments
    tracker.add_comment(defect1_id, "Investigating root cause", "developer1")
    tracker.add_comment(defect1_id, "Found memory leak in async operations", "developer1")
    
    # Update defect status
    tracker.update_defect(defect1_id, status=DefectStatus.IN_PROGRESS, assigned_to="developer1")
    
    # Get statistics
    stats = tracker.get_defect_statistics()
    
    # Print report
    print("=== Defect Tracker Report ===")
    print(f"Total Defects: {stats.total_defects}")
    print(f"Open Defects: {stats.open_defects}")
    print(f"Critical Defects: {stats.critical_defects}")
    print(f"High Priority Defects: {stats.high_priority_defects}")
    print(f"Resolution Rate: {stats.resolution_rate:.1%}" if stats.resolution_rate else "N/A")
    
    print("\nDefects by Category:")
    for category, count in stats.defects_by_category.items():
        print(f"  {category.value}: {count}")
    
    print("\nDefects by Severity:")
    for severity, count in stats.defects_by_severity.items():
        print(f"  {severity.value}: {count}")
    
    # Export defects
    tracker.export_defects(format="json")
    
    print(f"\nDefect data saved to results/inspector/defects/")


if __name__ == "__main__":
    main() 
"""
Data Visualizer for Module 4: LangflowConnector

This module handles data visualization and chart generation for Langflow.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum

import aiofiles


class ChartType(Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"


class DataFormat(Enum):
    """Data formats for visualization"""
    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    XML = "xml"
    YAML = "yaml"


@dataclass
class ChartConfig:
    """Chart configuration"""
    id: str
    title: str
    chart_type: ChartType
    data_source: str
    x_axis: str
    y_axis: str
    color_field: Optional[str] = None
    size_field: Optional[str] = None
    filters: Dict[str, Any] = None
    options: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
        if self.filters is None:
            self.filters = {}
        if self.options is None:
            self.options = {}


@dataclass
class VisualizationData:
    """Visualization data structure"""
    chart_id: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime
    format: DataFormat = DataFormat.JSON


@dataclass
class Dashboard:
    """Dashboard configuration"""
    id: str
    name: str
    description: str
    charts: List[str]  # Chart IDs
    layout: Dict[str, Any]
    refresh_interval: int = 300  # seconds
    is_public: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


class DataVisualizer:
    """
    Handles data visualization and chart generation for Langflow.
    """
    
    def __init__(self, data_dir: str = "data/visualizations"):
        self.data_dir = data_dir
        self.charts: Dict[str, ChartConfig] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.visualization_data: Dict[str, VisualizationData] = {}
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        
        # Default chart templates
        self.default_charts = {
            "cost_trends": {
                "title": "Cost Trends Over Time",
                "chart_type": ChartType.LINE,
                "x_axis": "date",
                "y_axis": "cost",
                "color_field": "category"
            },
            "budget_usage": {
                "title": "Budget Usage by Category",
                "chart_type": ChartType.PIE,
                "x_axis": "category",
                "y_axis": "amount",
                "color_field": "category"
            },
            "performance_metrics": {
                "title": "System Performance Metrics",
                "chart_type": ChartType.BAR,
                "x_axis": "metric",
                "y_axis": "value",
                "color_field": "status"
            },
            "optimization_impact": {
                "title": "Optimization Impact Analysis",
                "chart_type": ChartType.AREA,
                "x_axis": "date",
                "y_axis": "savings",
                "color_field": "strategy"
            }
        }
    
    async def initialize(self) -> None:
        """Initialize the data visualizer"""
        self.logger.info("Initializing data visualizer...")
        
        try:
            await self._ensure_data_dir()
            await self._load_charts()
            await self._load_dashboards()
            await self._load_visualization_data()
            
            # Create default charts if none exist
            if not self.charts:
                await self._create_default_charts()
            
            self.logger.info("Data visualizer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize data visualizer: {e}")
            raise
    
    async def create_chart(
        self,
        title: str,
        chart_type: ChartType,
        data_source: str,
        x_axis: str,
        y_axis: str,
        color_field: Optional[str] = None,
        size_field: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new chart configuration"""
        async with self._lock:
            try:
                chart_id = f"chart_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{title.lower().replace(' ', '_')}"
                
                chart = ChartConfig(
                    id=chart_id,
                    title=title,
                    chart_type=chart_type,
                    data_source=data_source,
                    x_axis=x_axis,
                    y_axis=y_axis,
                    color_field=color_field,
                    size_field=size_field,
                    filters=filters or {},
                    options=options or {}
                )
                
                self.charts[chart_id] = chart
                await self._save_charts()
                
                self.logger.info(f"Created chart: {chart_id} - {title}")
                return chart_id
                
            except Exception as e:
                self.logger.error(f"Failed to create chart: {e}")
                raise
    
    async def get_chart(self, chart_id: str) -> Optional[ChartConfig]:
        """Get chart by ID"""
        return self.charts.get(chart_id)
    
    async def list_charts(self) -> List[ChartConfig]:
        """List all charts"""
        return list(self.charts.values())
    
    async def update_chart(
        self,
        chart_id: str,
        title: Optional[str] = None,
        chart_type: Optional[ChartType] = None,
        data_source: Optional[str] = None,
        x_axis: Optional[str] = None,
        y_axis: Optional[str] = None,
        color_field: Optional[str] = None,
        size_field: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update chart configuration"""
        async with self._lock:
            try:
                if chart_id not in self.charts:
                    return False
                
                chart = self.charts[chart_id]
                
                if title is not None:
                    chart.title = title
                if chart_type is not None:
                    chart.chart_type = chart_type
                if data_source is not None:
                    chart.data_source = data_source
                if x_axis is not None:
                    chart.x_axis = x_axis
                if y_axis is not None:
                    chart.y_axis = y_axis
                if color_field is not None:
                    chart.color_field = color_field
                if size_field is not None:
                    chart.size_field = size_field
                if filters is not None:
                    chart.filters = filters
                if options is not None:
                    chart.options = options
                
                chart.updated_at = datetime.now(timezone.utc)
                await self._save_charts()
                
                self.logger.info(f"Updated chart: {chart_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update chart: {e}")
                return False
    
    async def delete_chart(self, chart_id: str) -> bool:
        """Delete chart"""
        async with self._lock:
            try:
                if chart_id not in self.charts:
                    return False
                
                del self.charts[chart_id]
                await self._save_charts()
                
                self.logger.info(f"Deleted chart: {chart_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete chart: {e}")
                return False
    
    async def generate_visualization(
        self,
        chart_id: str,
        data: List[Dict[str, Any]],
        format: DataFormat = DataFormat.JSON
    ) -> str:
        """Generate visualization data for a chart"""
        async with self._lock:
            try:
                if chart_id not in self.charts:
                    raise ValueError(f"Chart {chart_id} not found")
                
                chart = self.charts[chart_id]
                
                # Process data according to chart configuration
                processed_data = await self._process_data_for_chart(chart, data)
                
                # Create visualization data
                viz_data = VisualizationData(
                    chart_id=chart_id,
                    data=processed_data,
                    metadata={
                        "chart_type": chart.chart_type.value,
                        "x_axis": chart.x_axis,
                        "y_axis": chart.y_axis,
                        "color_field": chart.color_field,
                        "size_field": chart.size_field,
                        "filters": chart.filters,
                        "options": chart.options
                    },
                    timestamp=datetime.now(timezone.utc),
                    format=format
                )
                
                viz_id = f"viz_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{chart_id}"
                self.visualization_data[viz_id] = viz_data
                await self._save_visualization_data()
                
                self.logger.info(f"Generated visualization: {viz_id} for chart {chart_id}")
                return viz_id
                
            except Exception as e:
                self.logger.error(f"Failed to generate visualization: {e}")
                raise
    
    async def get_visualization(self, viz_id: str) -> Optional[VisualizationData]:
        """Get visualization by ID"""
        return self.visualization_data.get(viz_id)
    
    async def create_dashboard(
        self,
        name: str,
        description: str,
        charts: List[str],
        layout: Optional[Dict[str, Any]] = None,
        refresh_interval: int = 300,
        is_public: bool = False
    ) -> str:
        """Create a new dashboard"""
        async with self._lock:
            try:
                dashboard_id = f"dashboard_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
                
                if layout is None:
                    layout = self._generate_default_layout(charts)
                
                dashboard = Dashboard(
                    id=dashboard_id,
                    name=name,
                    description=description,
                    charts=charts,
                    layout=layout,
                    refresh_interval=refresh_interval,
                    is_public=is_public
                )
                
                self.dashboards[dashboard_id] = dashboard
                await self._save_dashboards()
                
                self.logger.info(f"Created dashboard: {dashboard_id} - {name}")
                return dashboard_id
                
            except Exception as e:
                self.logger.error(f"Failed to create dashboard: {e}")
                raise
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)
    
    async def list_dashboards(self, public_only: bool = False) -> List[Dashboard]:
        """List dashboards"""
        dashboards = list(self.dashboards.values())
        if public_only:
            dashboards = [d for d in dashboards if d.is_public]
        return dashboards
    
    async def update_dashboard(
        self,
        dashboard_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        charts: Optional[List[str]] = None,
        layout: Optional[Dict[str, Any]] = None,
        refresh_interval: Optional[int] = None,
        is_public: Optional[bool] = None
    ) -> bool:
        """Update dashboard"""
        async with self._lock:
            try:
                if dashboard_id not in self.dashboards:
                    return False
                
                dashboard = self.dashboards[dashboard_id]
                
                if name is not None:
                    dashboard.name = name
                if description is not None:
                    dashboard.description = description
                if charts is not None:
                    dashboard.charts = charts
                if layout is not None:
                    dashboard.layout = layout
                if refresh_interval is not None:
                    dashboard.refresh_interval = refresh_interval
                if is_public is not None:
                    dashboard.is_public = is_public
                
                dashboard.updated_at = datetime.now(timezone.utc)
                await self._save_dashboards()
                
                self.logger.info(f"Updated dashboard: {dashboard_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update dashboard: {e}")
                return False
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""
        async with self._lock:
            try:
                if dashboard_id not in self.dashboards:
                    return False
                
                del self.dashboards[dashboard_id]
                await self._save_dashboards()
                
                self.logger.info(f"Deleted dashboard: {dashboard_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete dashboard: {e}")
                return False
    
    async def export_visualization(
        self,
        viz_id: str,
        format: DataFormat = DataFormat.JSON
    ) -> str:
        """Export visualization data in specified format"""
        try:
            viz_data = self.visualization_data.get(viz_id)
            if not viz_data:
                raise ValueError(f"Visualization {viz_id} not found")
            
            if format == DataFormat.JSON:
                return json.dumps({
                    "chart_id": viz_data.chart_id,
                    "data": viz_data.data,
                    "metadata": viz_data.metadata,
                    "timestamp": viz_data.timestamp.isoformat(),
                    "format": viz_data.format.value
                }, indent=2)
            
            elif format == DataFormat.CSV:
                if not viz_data.data:
                    return ""
                
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=viz_data.data[0].keys())
                writer.writeheader()
                writer.writerows(viz_data.data)
                
                return output.getvalue()
            
            elif format == DataFormat.TSV:
                if not viz_data.data:
                    return ""
                
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=viz_data.data[0].keys(), delimiter='\t')
                writer.writeheader()
                writer.writerows(viz_data.data)
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Failed to export visualization: {e}")
            raise
    
    async def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create default JSON files if they don't exist
        default_files = {
            'charts.json': [],
            'dashboards.json': [],
            'visualizations.json': []
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(default_data, indent=2, default=str))

    async def _load_charts(self) -> None:
        """Load charts from file"""
        filepath = os.path.join(self.data_dir, 'charts.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    charts_data = json.loads(data)
                    
                    for chart_data in charts_data:
                        chart = ChartConfig(
                            id=chart_data['id'],
                            title=chart_data['title'],
                            chart_type=ChartType(chart_data['chart_type']),
                            data_source=chart_data['data_source'],
                            x_axis=chart_data['x_axis'],
                            y_axis=chart_data['y_axis'],
                            color_field=chart_data.get('color_field'),
                            size_field=chart_data.get('size_field'),
                            filters=chart_data.get('filters', {}),
                            options=chart_data.get('options', {}),
                            created_at=datetime.fromisoformat(chart_data['created_at']),
                            updated_at=datetime.fromisoformat(chart_data['updated_at'])
                        )
                        self.charts[chart.id] = chart
            else:
                # Create default file
                await self._save_charts()
        except Exception as e:
            self.logger.error(f"Failed to load charts: {e}")
            # Create default file on error
            await self._save_charts()

    async def _save_charts(self) -> None:
        """Save charts to file"""
        try:
            charts_file = f"{self.data_dir}/charts.json"
            charts_data = []
            for chart in self.charts.values():
                chart_dict = asdict(chart)
                chart_dict['chart_type'] = chart_dict['chart_type'].value
                chart_dict['created_at'] = chart_dict['created_at'].isoformat()
                chart_dict['updated_at'] = chart_dict['updated_at'].isoformat()
                charts_data.append(chart_dict)
            
            async with aiofiles.open(charts_file, 'w') as f:
                await f.write(json.dumps(charts_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save charts: {e}")
    
    async def _load_dashboards(self) -> None:
        """Load dashboards from file"""
        filepath = os.path.join(self.data_dir, 'dashboards.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    dashboards_data = json.loads(data)
                    
                    for dashboard_data in dashboards_data:
                        dashboard = Dashboard(
                            id=dashboard_data['id'],
                            name=dashboard_data['name'],
                            description=dashboard_data['description'],
                            charts=dashboard_data['charts'],
                            layout=dashboard_data.get('layout', {}),
                            refresh_interval=dashboard_data.get('refresh_interval', 300),
                            is_public=dashboard_data.get('is_public', False),
                            created_at=datetime.fromisoformat(dashboard_data['created_at']),
                            updated_at=datetime.fromisoformat(dashboard_data['updated_at'])
                        )
                        self.dashboards[dashboard.id] = dashboard
            else:
                # Create default file
                await self._save_dashboards()
        except Exception as e:
            self.logger.error(f"Failed to load dashboards: {e}")
            # Create default file on error
            await self._save_dashboards()

    async def _save_dashboards(self) -> None:
        """Save dashboards to file"""
        try:
            dashboards_file = f"{self.data_dir}/dashboards.json"
            dashboards_data = []
            for dashboard in self.dashboards.values():
                dashboard_dict = asdict(dashboard)
                dashboard_dict['created_at'] = dashboard_dict['created_at'].isoformat()
                dashboard_dict['updated_at'] = dashboard_dict['updated_at'].isoformat()
                dashboards_data.append(dashboard_dict)
            
            async with aiofiles.open(dashboards_file, 'w') as f:
                await f.write(json.dumps(dashboards_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save dashboards: {e}")
    
    async def _load_visualization_data(self) -> None:
        """Load visualization data from file"""
        filepath = os.path.join(self.data_dir, 'visualizations.json')
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    data = await f.read()
                    viz_data = json.loads(data)
                    
                    for viz_item in viz_data:
                        visualization = VisualizationData(
                            chart_id=viz_item['chart_id'],
                            data=viz_item['data'],
                            metadata=viz_item['metadata'],
                            timestamp=datetime.fromisoformat(viz_item['timestamp']),
                            format=DataFormat(viz_item['format'])
                        )
                        self.visualization_data[viz_item['chart_id']] = visualization
            else:
                # Create default file
                await self._save_visualization_data()
        except Exception as e:
            self.logger.error(f"Failed to load visualization data: {e}")
            # Create default file on error
            await self._save_visualization_data()

    async def _save_visualization_data(self) -> None:
        """Save visualization data to file"""
        try:
            viz_file = f"{self.data_dir}/visualizations.json"
            viz_data = []
            for viz in self.visualization_data.values():
                viz_dict = asdict(viz)
                viz_dict['timestamp'] = viz_dict['timestamp'].isoformat()
                viz_dict['format'] = viz_dict['format'].value
                viz_data.append(viz_dict)
            
            async with aiofiles.open(viz_file, 'w') as f:
                await f.write(json.dumps(viz_data, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save visualization data: {e}")
    
    async def _create_default_charts(self) -> None:
        """Create default chart configurations"""
        for chart_name, chart_config in self.default_charts.items():
            await self.create_chart(
                title=chart_config["title"],
                chart_type=chart_config["chart_type"],
                data_source=f"module_data_{chart_name}",
                x_axis=chart_config["x_axis"],
                y_axis=chart_config["y_axis"],
                color_field=chart_config.get("color_field")
            )
    
    async def _process_data_for_chart(self, chart: ChartConfig, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data according to chart configuration"""
        processed_data = []
        
        for item in data:
            # Apply filters
            if chart.filters:
                if not self._apply_filters(item, chart.filters):
                    continue
            
            # Extract relevant fields
            processed_item = {
                chart.x_axis: item.get(chart.x_axis),
                chart.y_axis: item.get(chart.y_axis)
            }
            
            if chart.color_field and chart.color_field in item:
                processed_item[chart.color_field] = item[chart.color_field]
            
            if chart.size_field and chart.size_field in item:
                processed_item[chart.size_field] = item[chart.size_field]
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def _apply_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to data item"""
        for field, filter_value in filters.items():
            if field not in item:
                return False
            
            item_value = item[field]
            
            if isinstance(filter_value, dict):
                # Complex filter (range, regex, etc.)
                if "min" in filter_value and item_value < filter_value["min"]:
                    return False
                if "max" in filter_value and item_value > filter_value["max"]:
                    return False
                if "regex" in filter_value:
                    import re
                    if not re.search(filter_value["regex"], str(item_value)):
                        return False
            else:
                # Simple equality filter
                if item_value != filter_value:
                    return False
        
        return True
    
    def _generate_default_layout(self, charts: List[str]) -> Dict[str, Any]:
        """Generate default dashboard layout"""
        layout = {
            "type": "grid",
            "columns": 2,
            "rows": (len(charts) + 1) // 2,
            "items": []
        }
        
        for i, chart_id in enumerate(charts):
            row = i // 2
            col = i % 2
            
            layout["items"].append({
                "id": chart_id,
                "x": col,
                "y": row,
                "w": 1,
                "h": 1
            })
        
        return layout 
"""
Fast dashboard generation for capacity utilization visualization.

Generates historical charts, forecasts, bottleneck alerts, and recommendations
with <5s load time.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import numpy as np
from dataclasses import asdict


class DashboardGenerator:
    """
    Generates capacity utilization dashboards efficiently.
    
    Supports historical trends, forecasts, bottleneck alerts,
    and provisioning recommendations with optimized rendering.
    """
    
    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._cache = {}
    
    def _generate_historical_chart_data(
        self,
        metric_name: str,
        historical_data: np.ndarray,
        days_back: int = 90,
    ) -> Dict:
        """Generate data for 90-day historical chart"""
        # Downsample to every 3rd point for fast rendering
        downsample_rate = max(1, len(historical_data) // 100)
        downsampled = historical_data[::downsample_rate]
        
        dates = [
            (datetime.now() - timedelta(days=days_back))
            + timedelta(days=i * downsample_rate / (len(downsampled) - 1) * days_back)
            for i in range(len(downsampled))
        ]
        
        return {
            'metric': metric_name,
            'type': 'line_chart',
            'dates': [d.isoformat() for d in dates],
            'values': downsampled.tolist(),
            'min': float(np.min(downsampled)),
            'max': float(np.max(downsampled)),
            'avg': float(np.mean(downsampled)),
        }
    
    def _generate_forecast_chart_data(
        self,
        metric_name: str,
        current_value: float,
        forecast_7day: np.ndarray,
        forecast_30day: np.ndarray,
        confidence_upper: np.ndarray,
        confidence_lower: np.ndarray,
    ) -> Dict:
        """Generate data for forecast chart"""
        # Combine current + forecast for 30-day view
        full_forecast = np.concatenate([
            [current_value],
            forecast_30day[:30],
        ])
        
        dates = [
            datetime.now() + timedelta(days=i)
            for i in range(len(full_forecast))
        ]
        
        return {
            'metric': metric_name,
            'type': 'forecast_chart',
            'dates': [d.isoformat() for d in dates],
            'forecast': full_forecast.tolist(),
            'confidence_upper': confidence_upper[:30].tolist(),
            'confidence_lower': confidence_lower[:30].tolist(),
            'current': current_value,
        }
    
    def _generate_bottleneck_alert_panel(
        self,
        alerts: List,
    ) -> Dict:
        """Generate bottleneck alert panel"""
        alert_items = []
        
        for alert in alerts[:5]:  # Show top 5 alerts
            severity_color = {
                'critical': '#FF0000',
                'high': '#FF6600',
                'medium': '#FFAA00',
                'low': '#00AA00',
            }
            
            alert_items.append({
                'resource': alert.resource,
                'current_util': f"{alert.current_utilization_percent:.1f}%",
                'saturation_date': alert.predicted_saturation_date.isoformat(),
                'days_until': alert.days_until_saturation,
                'severity': alert.severity,
                'severity_color': severity_color.get(alert.severity, '#CCCCCC'),
                'confidence': f"{alert.confidence * 100:.0f}%",
            })
        
        return {
            'panel_type': 'bottleneck_alerts',
            'alerts': alert_items,
            'total_alerts': len(alerts),
        }
    
    def _generate_recommendation_panel(
        self,
        recommendations: List,
    ) -> Dict:
        """Generate provisioning recommendation panel"""
        rec_items = []
        
        for rec in recommendations[:10]:  # Show top 10 recommendations
            roi_status = 'High ROI' if rec.roi_months < 12 else 'Medium ROI'
            
            rec_items.append({
                'type': rec.recommendation_type,
                'resource': rec.resource,
                'current': rec.current_capacity,
                'recommended': rec.recommended_capacity,
                'timing': rec.timing,
                'monthly_cost': f"${rec.estimated_cost_monthly:.2f}",
                'monthly_savings': f"${rec.estimated_savings_monthly:.2f}",
                'roi_months': rec.roi_months,
                'roi_status': roi_status,
                'confidence': f"{rec.confidence * 100:.0f}%",
            })
        
        total_savings = sum(r.estimated_savings_monthly for r in recommendations)
        
        return {
            'panel_type': 'recommendations',
            'recommendations': rec_items,
            'total_recommendations': len(recommendations),
            'total_monthly_savings': f"${total_savings:.2f}",
        }
    
    def generate_dashboard(
        self,
        metrics_data: Dict,  # {metric_name: {...}}
        alerts: List,
        recommendations: List,
        include_cache: bool = True,
    ) -> Dict:
        """
        Generate complete dashboard with all panels.
        
        Optimized for <5s load time.
        """
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0',
            'panels': [],
        }
        
        # Generate metric panels
        for metric_name, metric_data in metrics_data.items():
            try:
                historical = self._generate_historical_chart_data(
                    metric_name,
                    metric_data['historical'],
                )
                dashboard['panels'].append(historical)
                
                if 'forecast_30day' in metric_data:
                    forecast = self._generate_forecast_chart_data(
                        metric_name,
                        metric_data.get('current', 0),
                        metric_data.get('forecast_7day', np.array([])),
                        metric_data['forecast_30day'],
                        metric_data.get('confidence_upper', np.array([])),
                        metric_data.get('confidence_lower', np.array([])),
                    )
                    dashboard['panels'].append(forecast)
            except Exception as e:
                # Skip problematic metrics
                continue
        
        # Add alert panel
        if alerts:
            dashboard['panels'].append(
                self._generate_bottleneck_alert_panel(alerts)
            )
        
        # Add recommendation panel
        if recommendations:
            dashboard['panels'].append(
                self._generate_recommendation_panel(recommendations)
            )
        
        return dashboard
    
    def generate_dashboard_json(
        self,
        metrics_data: Dict,
        alerts: List,
        recommendations: List,
    ) -> str:
        """Generate dashboard as JSON string for fast transmission"""
        dashboard = self.generate_dashboard(
            metrics_data,
            alerts,
            recommendations,
        )
        
        return json.dumps(dashboard, indent=2)
    
    def generate_dashboard_html(
        self,
        dashboard_json: str,
        title: str = "Capacity Utilization Dashboard",
    ) -> str:
        """Generate lightweight HTML dashboard"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; background: #f5f5f5; }}
        .dashboard {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 28px; color: #333; }}
        .panels {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr)); gap: 20px; }}
        .panel {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .panel h3 {{ margin-bottom: 15px; color: #333; font-size: 16px; }}
        .chart {{ height: 300px; background: #fafafa; border-radius: 4px; padding: 10px; }}
        .alert {{ padding: 12px; margin: 8px 0; border-left: 4px solid #ccc; border-radius: 2px; }}
        .alert.critical {{ border-color: #FF0000; background: #FFE5E5; }}
        .alert.high {{ border-color: #FF6600; background: #FFE5CC; }}
        .metric-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .metric-row:last-child {{ border-bottom: none; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>{title}</h1>
            <p>Real-time capacity utilization and forecast dashboard</p>
        </div>
        <div class="panels">
            <div class="panel">
                <h3>Dashboard Data</h3>
                <pre style="font-size: 11px; overflow-y: auto; max-height: 400px;">{dashboard_json}</pre>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html

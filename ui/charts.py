import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict
from src.hooks import LifecycleHooks
import streamlit as st

def generate_progress_charts(biofeedback_data: List[Dict]):
    """Generate progress charts from biofeedback data"""
    try:
        if not biofeedback_data:
            st.warning("No biofeedback data available yet")
            return
        
        # Prepare data
        timestamps = [entry['timestamp'] for entry in biofeedback_data]
        heart_rates = [entry['heart_rate'] for entry in biofeedback_data]
        steps = [entry['steps'] for entry in biofeedback_data]
        hydration_alerts = sum(1 for entry in biofeedback_data if entry.get('hydration_alert', False))
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "xy"}, {"type": "domain"}],
                [{"type": "xy"}, {"type": "indicator"}]
            ],
            subplot_titles=(
                "Heart Rate Trend",
                "Hydration Alerts",
                "Step Count Trend",
                "Current Status"
            )
        )
        
        # Heart rate chart
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=heart_rates,
                name="Heart Rate",
                line=dict(color='#4FD1C5')
            ),
            row=1, col=1
        )
        
        # Hydration pie chart
        fig.add_trace(
            go.Pie(
                labels=['Hydration OK', 'Hydration Alert'],
                values=[len(biofeedback_data) - hydration_alerts, hydration_alerts],
                marker=dict(colors=['#68D391', '#E53E3E']),
                hole=0.4
            ),
            row=1, col=2
        )
        
        # Steps chart
        fig.add_trace(
            go.Bar(
                x=timestamps,
                y=steps,
                name="Steps",
                marker_color='#63B3ED'
            ),
            row=2, col=1
        )
        
        # Current status indicator
        last_hr = heart_rates[-1]
        hr_status = "Excellent" if last_hr < 70 else "Good" if last_hr < 90 else "Elevated"
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=last_hr,
                title="Current Heart Rate",
                gauge=dict(
                    axis=dict(range=[50, 120]),
                    bar=dict(color='#F687B3'),
                    steps=[
                        dict(range=[50, 70], color="#38A169"),
                        dict(range=[70, 90], color="#68D391"),
                        dict(range=[90, 120], color="#E53E3E")
                    ]
                )
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=700,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2D3748')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        LifecycleHooks.on_error('ChartGenerator', e)
        st.error("Error generating charts")
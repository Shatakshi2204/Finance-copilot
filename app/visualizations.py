"""
Visualizations
==============
Plotly charts for macroeconomic data visualization.
Optimized for performance.
"""

import plotly.graph_objects as go
from data_fetcher import TriangulatedData, get_data
from config import app_config


def create_source_comparison_chart(data: TriangulatedData) -> go.Figure:
    """Create a bar chart comparing values from different sources."""
    sources = []
    values = []
    colors = []
    
    color_map = {
        "FRED": "#1f77b4",
        "World Bank": "#2ca02c",
        "OECD": "#ff7f0e",
        "Consensus": "#d62728"
    }
    
    if data.fred_value is not None:
        sources.append("FRED")
        values.append(data.fred_value)
        colors.append(color_map["FRED"])
    
    if data.worldbank_value is not None:
        sources.append("World Bank")
        values.append(data.worldbank_value)
        colors.append(color_map["World Bank"])
    
    if data.oecd_value is not None:
        sources.append("OECD")
        values.append(data.oecd_value)
        colors.append(color_map["OECD"])
    
    if data.consensus_value is not None:
        sources.append("Consensus")
        values.append(data.consensus_value)
        colors.append(color_map["Consensus"])
    
    fig = go.Figure(data=[
        go.Bar(
            x=sources,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}%" for v in values],
            textposition="outside"
        )
    ])
    
    metric_name = app_config.metrics.get(data.metric, data.metric)
    
    fig.update_layout(
        title=f"{metric_name} - {data.country}",
        xaxis_title="Source",
        yaxis_title="Value (%)",
        showlegend=False,
        height=350,
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


def create_confidence_gauge(confidence: str) -> go.Figure:
    """Create a gauge chart showing confidence level."""
    confidence_values = {
        "high": 90,
        "medium": 60,
        "low": 30,
        "single_source": 40,
        "no_data": 0
    }
    
    confidence_colors = {
        "high": "green",
        "medium": "orange",
        "low": "red",
        "single_source": "yellow",
        "no_data": "gray"
    }
    
    value = confidence_values.get(confidence, 0)
    color = confidence_colors.get(confidence, "gray")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": "Confidence"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 30], "color": "#ffebee"},
                {"range": [30, 60], "color": "#fff8e1"},
                {"range": [60, 100], "color": "#e8f5e9"}
            ],
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_country_comparison_chart(metric: str) -> go.Figure:
    """Create a chart comparing a metric across all countries."""
    countries = []
    values = []
    confidences = []
    
    for country_code in app_config.countries.keys():
        try:
            data = get_data(metric, country_code)
            if data.consensus_value is not None:
                countries.append(data.country)
                values.append(data.consensus_value)
                confidences.append(data.confidence)
        except:
            continue
    
    # Color by confidence
    color_map = {
        "high": "#2ca02c",
        "medium": "#ff7f0e",
        "low": "#d62728",
        "single_source": "#ffcc00"
    }
    colors = [color_map.get(c, "#999999") for c in confidences]
    
    fig = go.Figure(data=[
        go.Bar(
            x=countries,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}%" for v in values],
            textposition="outside"
        )
    ])
    
    metric_name = app_config.metrics.get(metric, metric)
    
    fig.update_layout(
        title=f"{metric_name} - All Countries",
        xaxis_title="Country",
        yaxis_title="Value (%)",
        showlegend=False,
        height=350,
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig


def create_metrics_overview_chart(country_code: str) -> go.Figure:
    """Create a radar chart showing all metrics for a country."""
    metrics = []
    values = []
    
    for metric_key, metric_name in app_config.metrics.items():
        try:
            data = get_data(metric_key, country_code)
            if data.consensus_value is not None:
                metrics.append(metric_name)
                values.append(abs(data.consensus_value))
        except:
            continue
    
    if not values:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    # Normalize values for radar chart
    max_val = max(values) if values else 1
    normalized = [v / max_val * 100 for v in values]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=normalized + [normalized[0]],
        theta=metrics + [metrics[0]],
        fill='toself',
        name=app_config.countries.get(country_code, country_code),
        line_color="#1f77b4"
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=f"Economic Overview - {app_config.countries.get(country_code, country_code)}",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_risk_heatmap() -> go.Figure:
    """Create a heatmap showing risk levels across countries and metrics."""
    risk_thresholds = {
        "gdp_growth": {"low": 3, "moderate": 1, "high": 0},
        "inflation": {"low": 2, "moderate": 4, "high": 6},
        "unemployment": {"low": 4, "moderate": 6, "high": 8},
        "interest_rate": {"low": 2, "moderate": 4, "high": 6}
    }
    
    countries = list(app_config.countries.keys())
    metrics = list(app_config.metrics.keys())
    
    risk_matrix = []
    hover_text = []
    
    for metric in metrics:
        row = []
        hover_row = []
        thresholds = risk_thresholds.get(metric, {})
        
        for country in countries:
            try:
                data = get_data(metric, country)
                
                if data.consensus_value is None:
                    risk = 0
                    hover = "No data"
                else:
                    value = data.consensus_value
                    
                    if metric == "gdp_growth":
                        if value >= thresholds.get("low", 3):
                            risk = 20
                        elif value >= thresholds.get("moderate", 1):
                            risk = 50
                        else:
                            risk = 80
                    else:
                        if value <= thresholds.get("low", 2):
                            risk = 20
                        elif value <= thresholds.get("moderate", 4):
                            risk = 50
                        else:
                            risk = 80
                    
                    hover = f"{value:.2f}%"
                
                row.append(risk)
                hover_row.append(hover)
            except:
                row.append(0)
                hover_row.append("Error")
        
        risk_matrix.append(row)
        hover_text.append(hover_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=risk_matrix,
        x=[app_config.countries[c] for c in countries],
        y=[app_config.metrics[m] for m in metrics],
        text=hover_text,
        texttemplate="%{text}",
        colorscale=[[0, "#e8f5e9"], [0.5, "#fff8e1"], [1, "#ffebee"]],
        showscale=True,
        colorbar=dict(title="Risk")
    ))
    
    fig.update_layout(
        title="Risk Assessment Heatmap",
        xaxis_title="Country",
        yaxis_title="Metric",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

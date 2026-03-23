"""
Visualization utilities for Aviation Fuel Analytics dashboard.
Provides consistent, professional charts using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any


# Color palette for consistent branding
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ffbb33',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

SEQUENTIAL_PALETTE = px.colors.sequential.Blues
CATEGORICAL_PALETTE = px.colors.qualitative.Set2


def format_currency(value: float, prefix: str = '$', suffix: str = '') -> str:
    """Format value as currency."""
    if abs(value) >= 1e9:
        return f"{prefix}{value/1e9:.2f}B{suffix}"
    elif abs(value) >= 1e6:
        return f"{prefix}{value/1e6:.2f}M{suffix}"
    elif abs(value) >= 1e3:
        return f"{prefix}{value/1e3:.2f}K{suffix}"
    return f"{prefix}{value:.2f}{suffix}"


def create_kpi_card_figure(
    value: float,
    title: str,
    delta: Optional[float] = None,
    prefix: str = '',
    suffix: str = '',
    color: str = COLORS['primary']
) -> go.Figure:
    """Create a KPI indicator figure."""
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta" if delta else "number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        delta={"reference": value - delta, "relative": True} if delta else None,
        number={"prefix": prefix, "suffix": suffix, "font": {"size": 28}},
    ))

    fig.update_layout(
        height=120,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def create_timeseries_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str,
    y_axis_title: str = '',
    secondary_y_col: Optional[str] = None,
    secondary_y_title: str = ''
) -> go.Figure:
    """Create time series line chart with optional secondary y-axis."""

    if secondary_y_col:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        for i, col in enumerate(y_cols):
            if col != secondary_y_col:
                fig.add_trace(
                    go.Scatter(
                        x=df[x_col],
                        y=df[col],
                        name=col.replace('_', ' ').title(),
                        line=dict(color=CATEGORICAL_PALETTE[i % len(CATEGORICAL_PALETTE)])
                    ),
                    secondary_y=False
                )

        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[secondary_y_col],
                name=secondary_y_col.replace('_', ' ').title(),
                line=dict(color=COLORS['danger'], dash='dash')
            ),
            secondary_y=True
        )

        fig.update_yaxes(title_text=y_axis_title, secondary_y=False)
        fig.update_yaxes(title_text=secondary_y_title, secondary_y=True)
    else:
        fig = go.Figure()
        for i, col in enumerate(y_cols):
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    name=col.replace('_', ' ').title(),
                    line=dict(color=CATEGORICAL_PALETTE[i % len(CATEGORICAL_PALETTE)])
                )
            )
        fig.update_yaxes(title_text=y_axis_title)

    fig.update_layout(
        title=title,
        xaxis_title='',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=60, r=40, t=60, b=40),
        height=400
    )

    return fig


def create_correlation_heatmap(
    df: pd.DataFrame,
    columns: List[str],
    title: str = 'Correlation Matrix'
) -> go.Figure:
    """Create correlation heatmap."""
    corr_matrix = df[columns].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
        y=[c.replace('_', ' ').title() for c in corr_matrix.index],
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))

    fig.update_layout(
        title=title,
        height=500,
        margin=dict(l=100, r=40, t=60, b=100)
    )

    return fig


def create_scatter_with_regression(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: str = '',
    show_regression: bool = True
) -> go.Figure:
    """Create scatter plot with optional regression line."""

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={
            x_col: x_col.replace('_', ' ').title(),
            y_col: y_col.replace('_', ' ').title()
        },
        color_discrete_sequence=CATEGORICAL_PALETTE,
        trendline='ols' if show_regression else None
    )

    fig.update_layout(
        height=450,
        margin=dict(l=60, r=40, t=60, b=40)
    )

    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: str = '',
    orientation: str = 'v',
    show_values: bool = True
) -> go.Figure:
    """Create bar chart."""

    fig = px.bar(
        df,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        color=color_col,
        title=title,
        orientation=orientation,
        color_discrete_sequence=CATEGORICAL_PALETTE,
        text=y_col if show_values and orientation == 'v' else (x_col if show_values else None)
    )

    if show_values:
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=60, b=40),
        showlegend=color_col is not None
    )

    return fig


def create_event_timeline(
    df: pd.DataFrame,
    date_col: str,
    event_col: str,
    severity_col: str,
    impact_col: str,
    title: str = 'Event Timeline'
) -> go.Figure:
    """Create interactive event timeline."""

    severity_colors = {
        'Low': COLORS['success'],
        'Medium': COLORS['warning'],
        'High': COLORS['secondary'],
        'Very High': COLORS['danger']
    }

    fig = go.Figure()

    for severity in df[severity_col].unique():
        mask = df[severity_col] == severity
        subset = df[mask]

        fig.add_trace(go.Scatter(
            x=subset[date_col],
            y=subset[impact_col],
            mode='markers+text',
            name=severity,
            marker=dict(
                size=subset[impact_col].abs() * 3 + 10,
                color=severity_colors.get(severity, COLORS['info']),
                line=dict(width=2, color='white')
            ),
            text=subset[event_col],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Impact: %{y:.1f}%<extra></extra>'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Oil Price Impact (%)',
        height=500,
        hovermode='closest',
        legend=dict(title='Severity'),
        margin=dict(l=60, r=40, t=60, b=40)
    )

    return fig


def create_box_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = '',
    color_col: Optional[str] = None
) -> go.Figure:
    """Create box plot for distribution analysis."""

    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        color_discrete_sequence=CATEGORICAL_PALETTE
    )

    fig.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=60, b=40)
    )

    return fig


def create_treemap(
    df: pd.DataFrame,
    path: List[str],
    values_col: str,
    color_col: str,
    title: str = ''
) -> go.Figure:
    """Create treemap visualization."""

    fig = px.treemap(
        df,
        path=path,
        values=values_col,
        color=color_col,
        color_continuous_scale='RdYlGn',
        title=title
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str,
    min_val: float = 0,
    max_val: float = 100,
    thresholds: List[float] = None
) -> go.Figure:
    """Create gauge chart for single metrics."""

    if thresholds is None:
        thresholds = [max_val * 0.3, max_val * 0.7, max_val]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': COLORS['primary']},
            'steps': [
                {'range': [min_val, thresholds[0]], 'color': '#ffebee'},
                {'range': [thresholds[0], thresholds[1]], 'color': '#fff3e0'},
                {'range': [thresholds[1], max_val], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def create_sunburst(
    df: pd.DataFrame,
    path: List[str],
    values_col: str,
    title: str = ''
) -> go.Figure:
    """Create sunburst chart for hierarchical data."""

    fig = px.sunburst(
        df,
        path=path,
        values=values_col,
        title=title,
        color_discrete_sequence=CATEGORICAL_PALETTE
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig

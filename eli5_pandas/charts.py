"""Chart generation for data analysis results."""

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .models import FieldAnalysis, FieldType


class ChartGenerator:
    """Generates appropriate charts for different field types."""
    
    def __init__(self) -> None:
        """Initialize the chart generator."""
        pass
    
    def generate_field_chart(self, field: FieldAnalysis, data: pd.Series) -> Optional[str]:
        """
        Generate an appropriate chart for a field based on its type.
        
        Args:
            field: FieldAnalysis object
            data: Pandas Series containing the data
            
        Returns:
            HTML string containing the chart or None if no chart can be generated
        """
        if field.field_type == FieldType.CATEGORICAL:
            return self._generate_categorical_chart(field, data)
        elif field.field_type in [FieldType.INTEGER, FieldType.FLOAT]:
            return self._generate_numerical_chart(field, data)
        elif field.field_type == FieldType.DATETIME:
            return self._generate_datetime_chart(field, data)
        elif field.field_type == FieldType.BOOLEAN:
            return self._generate_boolean_chart(field, data)
        else:
            return None
    
    def _generate_categorical_chart(self, field: FieldAnalysis, data: pd.Series) -> str:
        """Generate a bar chart for categorical data."""
        # Get value counts for top 15 values
        value_counts = data.value_counts().head(15)
        
        # Convert to lists explicitly
        categories = value_counts.index.tolist()
        counts = value_counts.values.tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=counts,
            y=categories,
            orientation='h',
            marker_color='#667eea',
            text=counts,
            textposition='auto',
        ))
        
        fig.update_layout(
            title=f"Distribution of {field.name}",
            xaxis_title="Count",
            yaxis_title=field.name,
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig.to_html(include_plotlyjs=False, full_html=False)
    
    def _generate_numerical_chart(self, field: FieldAnalysis, data: pd.Series) -> str:
        """Generate a histogram for numerical data."""
        # Remove NaN values and convert to list
        clean_data = data.dropna().tolist()
        
        if len(clean_data) == 0:
            return "<p>No data available for chart</p>"
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=clean_data,
            nbinsx=30,
            marker_color='#667eea',
            opacity=0.7,
        ))
        
        fig.update_layout(
            title=f"Distribution of {field.name}",
            xaxis_title=field.name,
            yaxis_title="Frequency",
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig.to_html(include_plotlyjs=False, full_html=False)
    
    def _generate_datetime_chart(self, field: FieldAnalysis, data: pd.Series) -> str:
        """Generate a histogram for datetime data with intelligent binning."""
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(data):
            datetime_data = pd.to_datetime(data, errors='coerce')
        else:
            datetime_data = data
        
        # Remove NaN values
        clean_data = datetime_data.dropna()
        
        if len(clean_data) == 0:
            return "<p>No data available for chart</p>"
        
        # Determine appropriate binning based on data range
        min_date = clean_data.min()
        max_date = clean_data.max()
        date_range = max_date - min_date
        
        # Convert to list for Plotly
        dates_list = clean_data.tolist()
        
        fig = go.Figure()
        
        # Determine binning strategy
        if date_range.days <= 31:
            # Less than a month - bin by day
            fig.add_trace(go.Histogram(
                x=dates_list,
                nbinsx=min(30, len(clean_data.unique())),
                marker_color='#667eea',
                opacity=0.7,
            ))
            bin_type = "day"
        elif date_range.days <= 365:
            # Less than a year - bin by month
            fig.add_trace(go.Histogram(
                x=dates_list,
                nbinsx=min(12, len(clean_data.dt.to_period('M').unique())),
                marker_color='#667eea',
                opacity=0.7,
            ))
            bin_type = "month"
        else:
            # More than a year - bin by year
            fig.add_trace(go.Histogram(
                x=dates_list,
                nbinsx=min(10, len(clean_data.dt.to_period('Y').unique())),
                marker_color='#667eea',
                opacity=0.7,
            ))
            bin_type = "year"
        
        fig.update_layout(
            title=f"Distribution of {field.name} (binned by {bin_type})",
            xaxis_title=field.name,
            yaxis_title="Frequency",
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig.to_html(include_plotlyjs=False, full_html=False)
    
    def _generate_boolean_chart(self, field: FieldAnalysis, data: pd.Series) -> str:
        """Generate a pie chart for boolean data."""
        # Get value counts
        value_counts = data.value_counts()
        
        # Convert to lists explicitly
        labels = value_counts.index.tolist()
        values = value_counts.values.tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            marker_colors=['#28a745', '#dc3545'],
        ))
        
        fig.update_layout(
            title=f"Distribution of {field.name}",
            height=400,
            showlegend=True,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig.to_html(include_plotlyjs=False, full_html=False)
    
    def generate_summary_charts(self, fields: List[FieldAnalysis], data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate summary charts for the dataset.
        
        Args:
            fields: List of FieldAnalysis objects
            data: Pandas DataFrame containing the data
            
        Returns:
            Dictionary mapping chart names to HTML strings
        """
        charts = {}
        
        # Field type distribution
        field_types = [field.field_type.value for field in fields]
        type_counts = pd.Series(field_types).value_counts()
        
        # Convert to lists explicitly
        type_labels = type_counts.index.tolist()
        type_values = type_counts.values.tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=type_labels,
            values=type_values,
            marker_colors=px.colors.qualitative.Set3,
        ))
        
        fig.update_layout(
            title="Field Type Distribution",
            height=400,
            showlegend=True,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        charts['field_types'] = fig.to_html(include_plotlyjs=False, full_html=False)
        
        # Missing data heatmap
        missing_data = data.isnull().sum()
        if missing_data.sum() > 0:
            # Convert to lists explicitly
            field_names = missing_data.index.tolist()
            missing_counts = missing_data.values.tolist()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=field_names,
                y=missing_counts,
                marker_color='#ffc107',
                text=missing_counts,
                textposition='auto',
            ))
            
            fig.update_layout(
                title="Missing Data by Field",
                xaxis_title="Fields",
                yaxis_title="Missing Count",
                height=400,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            
            charts['missing_data'] = fig.to_html(include_plotlyjs=False, full_html=False)
        
        return charts 
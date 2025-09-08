import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import requests
import json

# Page configuration
st.set_page_config(
    page_title="DIPICA Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding: 1rem 2rem;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0px;
        border-left: 4px solid #4ECDC4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stMetric > div {
        text-align: center;
    }
    
    .stMetric label {
        text-align: center !important;
        justify-content: center !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        text-align: center;
    }
    
    .stMetric [data-testid="metric-container"] div[data-testid="metric-label"] {
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .stMetric [data-testid="metric-container"] > div > div {
        text-align: center !important;
    }
    
    .stMetric div[data-testid="metric-label"] {
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    .stMetric div[data-testid="metric-label"] > div {
        text-align: center !important;
        width: 100% !important;
    }
    
    .stMetric:nth-child(2n) {
        border-left-color: #FF6B6B;
    }
    
    .stMetric:nth-child(3n) {
        border-left-color: #95E1D3;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f4;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
    }
    
    h1 {
        color: #2C5F7F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2C5F7F;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #34495E;
    }
    
    .stSidebar {
        background-color: #f8f9fa;
    }
    
    .css-1d391kg {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for view selection
st.sidebar.header("🏥 DIPICA Dashboard")
st.sidebar.markdown("---")

view_selection = st.sidebar.radio(
    "Select View:",
    ["🗺️ Variable View", "🏛️ State View"],
    index=0,
    help="Choose between Variable-focused analysis or State-focused analysis"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Variable View**: Analyze healthcare accessibility by selecting specific variables and viewing national patterns with state-wise maps and rural-urban comparisons.

**State View**: Compare states by selecting multiple variables and viewing national benchmarks, radar comparisons, and rural-urban gaps.
""")

# Title with DIPICA logo - Side by side centered layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Single container approach with flexbox for precise control
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 20px 0;
    ">
        <img src="data:image/png;base64,{}" width="120" style="margin: 0;">
        <h1 style="
            color: #1f4e79; 
            margin: 0; 
            font-size: 2.5rem; 
            font-weight: bold;
            letter-spacing: 2px;
        ">DIPICA Dashboard</h1>
    </div>
    """.format(
        __import__('base64').b64encode(open('DIPICA.png', 'rb').read()).decode()
    ), unsafe_allow_html=True)

st.markdown("---")

# Load data with caching
@st.cache_data
def load_data():
    """Load the healthcare accessibility dataset"""
    try:
        df = pd.read_csv("healthcare_accessibility_data.csv")
        return df
    except FileNotFoundError:
        st.error("Dataset file 'healthcare_accessibility_data.csv' not found!")
        return None

# Load the dataset
df = load_data()

if df is None:
    st.error("❌ Unable to load the dataset. Please ensure 'healthcare_accessibility_data.csv' is in the same directory.")
    st.info("💡 You can create the dataset by running the data generation script first.")
    st.stop()

# Conditional rendering based on view selection
if view_selection == "🗺️ Variable View":
    # VARIABLE VIEW - Original dashboard.py content
    st.info("📊 **Healthcare Accessibility Analysis**: Select a healthcare accessibility variable to explore national patterns, state-wise distribution maps, and rural-urban comparisons across India.")
    
    st.markdown("---")
    
    # Dashboard Controls in main area
    st.header("🎛️ Variable Selection")
    filter_col1, filter_col2 = st.columns(2)
    
    # Main area filters
    with filter_col1:
        # Variable selection
        variable_options = {
            "HAC-M": "hac_m",
            "HAC-W": "hac_w"
        }

        selected_variable = st.selectbox(
            "Select Variable to Visualize:",
            options=list(variable_options.keys()),
            index=0
        )

        variable_type = variable_options[selected_variable]

    with filter_col2:
        # Time threshold selection (only for HAC variables)
        if variable_type in ["hac_m", "hac_w"]:
            if variable_type == "hac_m":
                time_options = {"30 minutes": "30", "60 minutes": "60", "90 minutes": "90", "120 minutes": "120"}
            else:  # hac_w
                time_options = {"60 minutes": "60", "120 minutes": "120", "240 minutes": "240"}

            selected_time = st.selectbox(
                f"Select Time Threshold:",
                options=list(time_options.keys()),
                index=0
            )

            time_value = time_options[selected_time]

            # Build column names
            if variable_type == "hac_m":
                total_col = f"HAC_M_{time_value}_Total"
                rural_col = f"HAC_M_{time_value}_Rural"
                urban_col = f"HAC_M_{time_value}_Urban"
            else:
                total_col = f"HAC_W_{time_value}_Total"
                rural_col = f"HAC_W_{time_value}_Rural"
                urban_col = f"HAC_W_{time_value}_Urban"

    # Initialize variables if not set (for cases where time selection is skipped)
    if 'total_col' not in locals():
        # Default to HAC-M 30min if not selected
        total_col = "HAC_M_30_Total"
        rural_col = "HAC_M_30_Rural"
        urban_col = "HAC_M_30_Urban"
        variable_type = "hac_m"
        selected_time = "30 minutes"

    # === TOP SECTION: KEY METRICS TILES ===
    st.header("📊 National Overview")

    # Calculate key metrics using India row
    india_row = df[df['State'] == 'India']
    if not india_row.empty:
        india_data = india_row.iloc[0]
        national_avg = india_data[total_col]
    else:
        # Fallback to mean if India row not found
        national_avg = df[total_col].mean()
        st.warning("India row not found in dataset, using calculated average instead.")

    # Determine variable abbreviation for tiles
    if variable_type == "hac_m":
        var_abbrev = f"HAC-M {selected_time.split()[0]}"
    else:
        var_abbrev = f"HAC-W {selected_time.split()[0]}"

    # Single centered tile for HAC percentage using metric component
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # st.markdown(f"""
        # <div style="
        #     background: linear-gradient(90deg, #4ECDC4 0%, #44A08D 100%);
        #     padding: 20px;
        #     border-radius: 8px;
        #     text-align: center;
        #     color: white;
        #     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        #     margin-bottom: 8px;
        #     height: 120px;
        #     display: flex;
        #     flex-direction: column;
        #     justify-content: center;
        # ">
        #     <h3 style="margin: 0; font-size: 16px; font-weight: 500;">{var_abbrev}</h3>
        #     <h1 style="margin: 8px 0 0 0; font-size: 32px; font-weight: bold;">{national_avg:.1f}%</h1>
        # </div>
        # """, unsafe_allow_html=True)
        st.metric(
        label=var_abbrev,
        value=f"{national_avg:.1f}%"
    )
    st.markdown("---")
    
    # === BOTTOM SECTION: VISUALIZATIONS SIDE BY SIDE ===
    viz_col1, viz_col2 = st.columns([1, 1])
    
    with viz_col1:
        if variable_type == "hac_m":
            viz_title = f"🗺️ Statewise distribution of: HAC-M {selected_time.split()[0]}"
        else:
            viz_title = f"🗺️ Statewise distribution of: HAC-W {selected_time.split()[0]}"
        st.subheader(viz_title)
        
        # Create enhanced choropleth map using shapefile
        color_label = "% Population"
        color_scale = 'Viridis'
        
        # Create choropleth map using the proven approach
        df_viz = df.copy()
        
        # Create the figure
        fig_map = go.Figure(data=go.Choropleth(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locationmode='geojson-id',
            locations=df_viz['State'],
            z=df_viz[total_col],
            zmin=0,
            zmax=100,
            autocolorscale=False,
            colorscale=color_scale,
            marker_line_color='white',
            marker_line_width=0.5,
            hovertemplate='<b>%{location}</b><br>' + color_label + ': %{z:.1f}<extra></extra>',
            colorbar=dict(
                title={'text': color_label},
                thickness=15,
                len=0.6,
                bgcolor='rgba(255,255,255,0.8)',
                xanchor='left',
                x=0.01,
                yanchor='bottom',
                y=0.1,
                tick0=0,
                dtick=20
            )
        ))
        
        # Update geos
        fig_map.update_geos(
            visible=False,
            projection=dict(
                type='conic conformal',
                parallels=[12.472944444, 35.172805555556],
                rotation={'lat': 24, 'lon': 80}
            ),
            lonaxis={'range': [68, 98]},
            lataxis={'range': [6, 38]}
        )
        
        # Update layout
        fig_map.update_layout(
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
            height=800,
            width=None
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Add dynamic description below the map
        transport_type = "motorized transport" if variable_type == "hac_m" else "walking"
        time_threshold = selected_time.split()[0]

        st.markdown(f"""
        <div style="text-align: center; margin-top: -50px; margin-bottom: 40px; color: #666; font-size: 14px; font-weight: 500;">
            % population within {time_threshold} min to nearest health center via {transport_type}
        </div>
        """, unsafe_allow_html=True)
    
    with viz_col2:
        if variable_type == "hac_m":
            range_title = f"📊 Rural vs Urban: HAC-M {selected_time.split()[0]}"
        else:
            range_title = f"📊 Rural vs Urban: HAC-W {selected_time.split()[0]}"
        st.subheader(range_title)
        
        # Rural vs Urban Comparison (Range Plot)
        if rural_col and urban_col:
            # Use the original loaded data
            df_range = load_data()
            
            # Ensure we have all original states including J&K
            if df_range is not None:
                df_sorted = df_range.sort_values(total_col, ascending=True)
            else:
                df_sorted = df.sort_values(total_col, ascending=True)
            
            fig_range = go.Figure()
            
            # Add rural values
            fig_range.add_trace(go.Scatter(
                x=df_sorted[rural_col],
                y=df_sorted['State'],
                mode='markers',
                name='Rural',
                marker=dict(color='#FF6B6B', size=10, symbol='circle'),
                hovertemplate='<b>%{y}</b><br>Rural: %{x:.1f}%<extra></extra>'
            ))
            
            # Add urban values  
            fig_range.add_trace(go.Scatter(
                x=df_sorted[urban_col],
                y=df_sorted['State'],
                mode='markers',
                name='Urban',
                marker=dict(color='#4ECDC4', size=10, symbol='diamond'),
                hovertemplate='<b>%{y}</b><br>Urban: %{x:.1f}%<extra></extra>'
            ))
            
            # Add range lines
            for idx, row in df_sorted.iterrows():
                fig_range.add_trace(go.Scatter(
                    x=[row[rural_col], row[urban_col]],
                    y=[row['State'], row['State']],
                    mode='lines',
                    line=dict(color='#A8DADC', width=3),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            fig_range.update_layout(
                xaxis_title=f"% population within {time_threshold} min to nearest center via {transport_type}",
                yaxis_title="",
                height=800,
                hovermode='closest',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='rgba(0,0,0,0.2)',
                    borderwidth=1
                )
            )
            
            fig_range.update_xaxes(gridcolor='lightgray', gridwidth=0.5)
            fig_range.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
            
            st.plotly_chart(fig_range, use_container_width=True)

else:  # State View
    # STATE VIEW - Original state_view.py content
    st.info("📊 **Healthcare Accessibility Analysis**: Select a healthcare accessibility variable to explore national patterns, state-wise distribution maps, and rural-urban comparisons across India.")
    
    st.markdown("---")
    # Dashboard Controls in main area
    st.header("🎛️ State and Variable Selection")
    filter_col1, filter_col2 = st.columns(2)
    
    # Get list of states (excluding India which is the total row)
    states = [state for state in df['State'].unique() if state != 'India']
    states.sort()  # Sort alphabetically
    
    # Get all variable columns (excluding State and population columns)
    population_cols = ['Total_Population', 'Rural_Population', 'Urban_Population']
    all_variable_columns = [col for col in df.columns if col not in ['State'] + population_cols]
    
    # Filter to only include "Total" variables (exclude Rural and Urban variants)
    total_variable_columns = [col for col in all_variable_columns if col.endswith('_Total')]
    
    # Create user-friendly variable names for Total variables only
    variable_display_names = {}
    for col in total_variable_columns:
        if col.startswith('HAC_M_'):
            # HAC Motorized transport
            parts = col.split('_')
            time = parts[2]
            display_name = f"HAC-M {time}min"
        elif col.startswith('HAC_W_'):
            # HAC Walking
            parts = col.split('_')
            time = parts[2]
            display_name = f"HAC-W {time}min"
        else:
            display_name = col
        variable_display_names[display_name] = col
    
    with filter_col1:
        # State selection (single choice)
        selected_state = st.selectbox(
            "🏛️ Select State:",
            options=states,
            index=0,
            help="Choose a state to analyze its healthcare accessibility metrics"
        )
    
    with filter_col2:
        # Variable selection (multiple choice - up to 5)
        selected_variables = st.multiselect(
            "📊 Select Variables (max 5):",
            options=list(variable_display_names.keys()),
            default=list(variable_display_names.keys())[:5],  # Default to first 5
            max_selections=5,
            help="Choose up to 5 healthcare accessibility variables to compare"
        )
    
    # Convert selected variable display names back to column names
    selected_variable_columns = [variable_display_names[var] for var in selected_variables]
    
    # Display national values and radar chart side by side
    if selected_variables:
        # Create three columns: tiles on left, radar chart in middle, range plot on right
        tiles_col, radar_col, range_col = st.columns([1, 2, 1.5])
        
        # Get India row for national values
        india_row = df[df['State'] == 'India']
        state_row = df[df['State'] == selected_state]
        
        if not india_row.empty and not state_row.empty:
            india_data = india_row.iloc[0]
            state_data = state_row.iloc[0]
            
            # Left column: National tiles
            with tiles_col:
                st.markdown("<h3 style='text-align: center;'>National Overview</h3>", unsafe_allow_html=True)
                for i, (display_name, col_name) in enumerate(zip(selected_variables[:5], selected_variable_columns[:5])):
                    national_value = india_data[col_name]
                    st.metric(
                        label=display_name,
                        value=f"{national_value:.1f}%"
                    )
            
            # Middle column: Radar chart
            with radar_col:
                st.markdown("<h3 style='text-align: center;'>State Comparison</h3>", unsafe_allow_html=True)
                
                # Prepare data for radar chart
                categories = selected_variables[:5]  # Limit to 5 for better visualization
                national_values = [india_data[col] for col in selected_variable_columns[:5]]
                state_values = [state_data[col] for col in selected_variable_columns[:5]]
                
                # Create radar chart
                fig = go.Figure()
                
                # Add national values (first web)
                fig.add_trace(go.Scatterpolar(
                    r=national_values,
                    theta=categories,
                    fill='toself',
                    name='India',
                    line=dict(color='#4ECDC4', width=2),
                    fillcolor='rgba(78, 205, 196, 0.2)'
                ))
                
                # Add state values (second web)
                fig.add_trace(go.Scatterpolar(
                    r=state_values,
                    theta=categories,
                    fill='toself',
                    name=selected_state,
                    line=dict(color='#FF6B6B', width=2),
                    fillcolor='rgba(255, 107, 107, 0.2)'
                ))
                
                # Update layout with proper configuration
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            ticksuffix='%'
                        )
                    ),
                    showlegend=True,
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    # Enable proper plotly controls
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                # Display chart with config for zoom/pan/reset
                st.plotly_chart(
                    fig, 
                    use_container_width=True,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': ['pan2d', 'select2d'],
                        'modeBarButtonsToRemove': ['lasso2d']
                    }
                )
                
                # Add centered subtitle below the chart
                st.markdown(
                    f"""<div style='text-align: center; margin-top: 10px; color: #666; font-size: 16px; font-weight: 500;'>
                    Healthcare Accessibility: India vs {selected_state}
                    </div>""", 
                    unsafe_allow_html=True
                )
            
            # Third column: Rural-Urban Range Plot
            with range_col:
                st.markdown("<h3 style='text-align: center;'>Rural-Urban Gap</h3>", unsafe_allow_html=True)
                
                # Get variables that have rural and urban data
                rural_urban_variables = []
                for display_name, col_name in zip(selected_variables[:5], selected_variable_columns[:5]):
                    # Check if rural and urban columns exist for this variable
                    rural_col = col_name.replace('_Total', '_Rural')
                    urban_col = col_name.replace('_Total', '_Urban')
                    
                    if rural_col in df.columns and urban_col in df.columns:
                        rural_urban_variables.append({
                            'display_name': display_name,
                            'rural_col': rural_col,
                            'urban_col': urban_col,
                            'rural_value': state_data[rural_col],
                            'urban_value': state_data[urban_col]
                        })
                
                if rural_urban_variables:
                    # Create range plot
                    fig_range = go.Figure()
                    
                    # Prepare data for the plot
                    variable_names = [var['display_name'] for var in rural_urban_variables]
                    rural_values = [var['rural_value'] for var in rural_urban_variables]
                    urban_values = [var['urban_value'] for var in rural_urban_variables]
                    
                    # Add rural values
                    fig_range.add_trace(go.Scatter(
                        x=rural_values,
                        y=variable_names,
                        mode='markers',
                        name='Rural',
                        marker=dict(color='#FF6B6B', size=10, symbol='circle'),
                        hovertemplate='<b>%{y}</b><br>Rural: %{x:.1f}%<extra></extra>'
                    ))
                    
                    # Add urban values
                    fig_range.add_trace(go.Scatter(
                        x=urban_values,
                        y=variable_names,
                        mode='markers',
                        name='Urban',
                        marker=dict(color='#4ECDC4', size=10, symbol='diamond'),
                        hovertemplate='<b>%{y}</b><br>Urban: %{x:.1f}%<extra></extra>'
                    ))
                    
                    # Add range lines connecting rural and urban values
                    for i, var in enumerate(rural_urban_variables):
                        fig_range.add_trace(go.Scatter(
                            x=[var['rural_value'], var['urban_value']],
                            y=[var['display_name'], var['display_name']],
                            mode='lines',
                            line=dict(color='#A8DADC', width=3),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    
                    # Update layout
                    fig_range.update_layout(
                        xaxis_title="Percentage (%)",
                        yaxis_title="",
                        height=400,
                        hovermode='closest',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=0, r=0, t=0, b=0),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            bgcolor='rgba(255,255,255,0.8)',
                            bordercolor='rgba(0,0,0,0.2)',
                            borderwidth=1
                        ),
                        yaxis=dict(side='left'),  # Only show left y-axis
                        showlegend=True
                    )
                    
                    # Remove axis lines, keep only horizontal grid
                    fig_range.update_xaxes(
                        showline=False,
                        showgrid=False,
                        zeroline=False,
                        range=[0, None],  # Start x-axis from 0
                        tick0=0,  # Start ticks from 0
                        dtick=20  # Tick interval
                    )
                    fig_range.update_yaxes(
                        showline=False,
                        showgrid=True,
                        gridcolor='lightgray',
                        gridwidth=0.5
                    )
                    
                    st.plotly_chart(fig_range, use_container_width=True)
                    
                    # Add centered subtitle below the chart
                    st.markdown(
                        f"""<div style='text-align: center; margin-top: 10px; color: #666; font-size: 14px; font-weight: 500;'>
                        Rural vs Urban Access - {selected_state}
                        </div>""", 
                        unsafe_allow_html=True
                    )
                else:
                    st.info("📍 No rural-urban data available for selected variables")
                
        else:
            if india_row.empty:
                st.error("❌ National data (India row) not found in dataset")
            if state_row.empty:
                st.error(f"❌ Data for {selected_state} not found in dataset")

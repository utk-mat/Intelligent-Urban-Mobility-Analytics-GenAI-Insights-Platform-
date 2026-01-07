"""
Intelligent Urban Mobility Analytics & GenAI Insights Platform
Comprehensive Streamlit Frontend
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import importlib.util

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import GenAI assistant
try:
    spec = importlib.util.spec_from_file_location(
        "genai_assistant", 
        Path(__file__).parent.parent / "5_genai_assistant.py"
    )
    genai_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(genai_module)
    MobilityGenAIAssistant = genai_module.MobilityGenAIAssistant
    GENAI_AVAILABLE = True
except Exception as e:
    st.warning(f"GenAI Assistant not available: {e}")
    GENAI_AVAILABLE = False
    MobilityGenAIAssistant = None

# -----------------------------
# CONFIGURATION
# -----------------------------
DATA_PATH = Path(__file__).parent.parent / "data" / "cleaned" / "cleaned_taxi_data.csv"
OUTPUTS = Path(__file__).parent.parent / "outputs"
VIS_DIR = OUTPUTS / "visualizations"
SQL_DIR = OUTPUTS / "sql_results"
SPARK_DIR = Path(__file__).parent.parent / "data" / "processed"
KPI_REPORT = OUTPUTS / "kpi_report.txt"

# Page config
st.set_page_config(
    page_title="Urban Mobility Analytics Platform",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stChatMessage {
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("🚕 Navigation")
page = st.sidebar.radio(
    "Select Page",
    [
        "📊 Dashboard Overview",
        "📈 Visual Analytics",
        "🧮 SQL Insights",
        "⚡ Spark Analytics",
        "🤖 GenAI Chatbot"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 About")
st.sidebar.info(
    """
    **Intelligent Urban Mobility Analytics Platform**
    
    This platform provides comprehensive analytics on urban transportation data including:
    - KPI computation and visualization
    - SQL-based analytics
    - PySpark ETL processing
    - GenAI-powered insights
    """
)

# -----------------------------
# DATA LOADING FUNCTIONS
# -----------------------------
@st.cache_data
def load_data():
    """Load cleaned taxi data"""
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def load_kpi_report():
    """Load KPI report"""
    try:
        if KPI_REPORT.exists():
            with open(KPI_REPORT, 'r') as f:
                return f.read()
        return None
    except Exception as e:
        st.error(f"Error loading KPI report: {e}")
        return None

@st.cache_data
def load_sql_results():
    """Load all SQL results"""
    results = {}
    if SQL_DIR.exists():
        for file in SQL_DIR.glob("*.csv"):
            try:
                results[file.stem] = pd.read_csv(file)
            except Exception as e:
                st.warning(f"Error loading {file.name}: {e}")
    return results

@st.cache_data
def load_spark_results():
    """Load Spark Parquet results"""
    results = {}
    if SPARK_DIR.exists():
        try:
            import pyarrow.parquet as pq
            for parquet_dir in SPARK_DIR.glob("*.parquet"):
                if parquet_dir.is_dir():
                    try:
                        df = pd.read_parquet(parquet_dir)
                        results[parquet_dir.name] = df
                    except Exception as e:
                        st.warning(f"Error loading {parquet_dir.name}: {e}")
        except ImportError:
            st.warning("PyArrow not available. Cannot load Parquet files.")
    return results

# Load data
df = load_data()
kpi_report = load_kpi_report()
sql_results = load_sql_results()
spark_results = load_spark_results()

# =============================
# PAGE 1 — DASHBOARD OVERVIEW
# =============================
if page == "📊 Dashboard Overview":
    st.markdown('<h1 class="main-header">🚕 Intelligent Urban Mobility Analytics</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    if df is not None:
        # Key Metrics
        st.subheader("📊 Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Trips",
                value=f"{len(df):,}",
                delta=None
            )
        
        with col2:
            total_revenue = df['total_amount'].sum()
            st.metric(
                label="Total Revenue",
                value=f"${total_revenue:,.0f}",
                delta=None
            )
        
        with col3:
            avg_distance = df['trip_distance'].mean()
            st.metric(
                label="Avg Distance",
                value=f"{avg_distance:.2f} mi",
                delta=None
            )
        
        with col4:
            avg_fare = df['fare_amount'].mean()
            st.metric(
                label="Avg Fare",
                value=f"${avg_fare:.2f}",
                delta=None
            )
        
        with col5:
            tip_pct = df['tip_percentage'].mean()
            st.metric(
                label="Avg Tip %",
                value=f"{tip_pct:.2f}%",
                delta=None
            )
        
        st.markdown("---")
        
        # Additional Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue_per_mile = df['revenue_per_mile'].mean()
            st.metric("Revenue per Mile", f"${revenue_per_mile:.2f}")
        
        with col2:
            avg_duration = df['trip_duration_minutes'].mean()
            st.metric("Avg Trip Duration", f"{avg_duration:.1f} min")
        
        with col3:
            peak_util = (df['is_peak_hour'].sum() / len(df)) * 100
            st.metric("Peak Hour Utilization", f"{peak_util:.1f}%")
        
        with col4:
            total_tips = df['tip_amount'].sum()
            st.metric("Total Tips", f"${total_tips:,.0f}")
        
        st.markdown("---")
        
        # Quick Charts
        st.subheader("📈 Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by Hour
            hourly_revenue = df.groupby('pickup_hour')['total_amount'].sum().reset_index()
            fig_hourly = px.bar(
                hourly_revenue,
                x='pickup_hour',
                y='total_amount',
                title='Revenue by Hour of Day',
                labels={'pickup_hour': 'Hour', 'total_amount': 'Revenue ($)'},
                color='total_amount',
                color_continuous_scale='Blues'
            )
            fig_hourly.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            # Trips by Day of Week
            trips_by_day = df.groupby('pickup_day_name')['total_amount'].count().reset_index()
            trips_by_day.columns = ['day', 'count']
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            trips_by_day['day'] = pd.Categorical(trips_by_day['day'], categories=day_order, ordered=True)
            trips_by_day = trips_by_day.sort_values('day')
            
            fig_days = px.bar(
                trips_by_day,
                x='day',
                y='count',
                title='Trips by Day of Week',
                labels={'day': 'Day', 'count': 'Number of Trips'},
                color='count',
                color_continuous_scale='Greens'
            )
            fig_days.update_layout(showlegend=False, height=300, xaxis_tickangle=-45)
            st.plotly_chart(fig_days, use_container_width=True)
        
        # Data Preview
        st.subheader("📄 Data Preview")
        st.dataframe(
            df.head(100),
            use_container_width=True,
            hide_index=True
        )
        
        # KPI Report
        if kpi_report:
            with st.expander("📋 Detailed KPI Report"):
                st.text(kpi_report)
    else:
        st.error("Unable to load data. Please ensure data files exist.")

# =============================
# PAGE 2 — VISUAL ANALYTICS
# =============================
elif page == "📈 Visual Analytics":
    st.title("📈 Visual Analytics")
    st.markdown("---")
    
    if df is not None:
        # Interactive Filters
        st.sidebar.subheader("🔍 Filters")
        
        # Date range filter
        if 'tpep_pickup_datetime' in df.columns:
            min_date = df['tpep_pickup_datetime'].min().date()
            max_date = df['tpep_pickup_datetime'].max().date()
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                df_filtered = df[
                    (df['tpep_pickup_datetime'].dt.date >= date_range[0]) &
                    (df['tpep_pickup_datetime'].dt.date <= date_range[1])
                ]
            else:
                df_filtered = df
        else:
            df_filtered = df
        
        # Peak hour filter
        peak_filter = st.sidebar.selectbox(
            "Peak Hours",
            ["All", "Peak Hours Only", "Off-Peak Only"]
        )
        
        if peak_filter == "Peak Hours Only":
            df_filtered = df_filtered[df_filtered['is_peak_hour'] == True]
        elif peak_filter == "Off-Peak Only":
            df_filtered = df_filtered[df_filtered['is_peak_hour'] == False]
        
        # Visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Static Visualizations",
            "💰 Revenue Analysis",
            "⏰ Time Patterns",
            "🗺️ Geographic Insights",
            "📈 Custom Analysis"
        ])
        
        with tab1:
            st.subheader("Pre-generated Visualizations")
            if VIS_DIR.exists():
                images = list(VIS_DIR.glob("*.png"))
                if images:
                    for img in images:
                        st.subheader(img.stem.replace("_", " ").title())
                        st.image(str(img), use_container_width=True)
                else:
                    st.info("No visualizations found. Please run Task 2 to generate visualizations.")
            else:
                st.warning("Visualizations directory not found.")
        
        with tab2:
            st.subheader("Revenue Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Monthly Revenue
                if 'pickup_month' in df_filtered.columns and 'pickup_year' in df_filtered.columns:
                    monthly_rev = df_filtered.groupby(['pickup_year', 'pickup_month'])['total_amount'].sum().reset_index()
                    monthly_rev['date'] = pd.to_datetime(
                        dict(year=monthly_rev['pickup_year'], month=monthly_rev['pickup_month'], day=1)
                    )
                    monthly_rev = monthly_rev.sort_values('date')
                    
                    fig = px.line(
                        monthly_rev,
                        x='date',
                        y='total_amount',
                        title='Monthly Revenue Trend',
                        markers=True
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue Distribution
                fig = px.histogram(
                    df_filtered,
                    x='total_amount',
                    nbins=50,
                    title='Revenue Distribution',
                    labels={'total_amount': 'Total Amount ($)', 'count': 'Frequency'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Revenue by Hour
            hourly_rev = df_filtered.groupby('pickup_hour')['total_amount'].agg(['sum', 'mean', 'count']).reset_index()
            hourly_rev.columns = ['hour', 'total_revenue', 'avg_revenue', 'trip_count']
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=hourly_rev['hour'], y=hourly_rev['total_revenue'], name="Total Revenue"),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=hourly_rev['hour'], y=hourly_rev['trip_count'], name="Trip Count", mode='lines+markers'),
                secondary_y=True,
            )
            fig.update_xaxes(title_text="Hour of Day")
            fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
            fig.update_yaxes(title_text="Trip Count", secondary_y=True)
            fig.update_layout(title="Revenue and Trip Count by Hour", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Time Patterns")
            
            # Heatmap: Day of Week vs Hour
            if 'pickup_day_name' in df_filtered.columns and 'pickup_hour' in df_filtered.columns:
                heatmap_data = df_filtered.pivot_table(
                    values='total_amount',
                    index='pickup_day_name',
                    columns='pickup_hour',
                    aggfunc='count',
                    fill_value=0
                )
                
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
                
                fig = px.imshow(
                    heatmap_data,
                    labels=dict(x="Hour of Day", y="Day of Week", color="Trip Count"),
                    title="Trip Heatmap: Day of Week vs Hour",
                    color_continuous_scale="YlOrRd",
                    aspect="auto"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Peak vs Off-Peak Comparison
            peak_comparison = df_filtered.groupby('is_peak_hour').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'trip_distance': 'mean',
                'trip_duration_minutes': 'mean'
            }).reset_index()
            
            st.dataframe(peak_comparison, use_container_width=True)
        
        with tab4:
            st.subheader("Geographic Insights")
            
            if 'pickup_latitude' in df_filtered.columns and 'pickup_longitude' in df_filtered.columns:
                # Sample data for map (too many points can be slow)
                sample_size = min(5000, len(df_filtered))
                df_sample = df_filtered.sample(n=sample_size)
                
                fig = px.scatter_mapbox(
                    df_sample,
                    lat='pickup_latitude',
                    lon='pickup_longitude',
                    color='total_amount',
                    size='trip_distance',
                    hover_data=['fare_amount', 'trip_duration_minutes'],
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    size_max=15,
                    zoom=10,
                    mapbox_style="open-street-map",
                    title="Pickup Locations (Sample)"
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Geographic data not available in the dataset.")
        
        with tab5:
            st.subheader("Custom Analysis")
            
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Fare vs Distance", "Tip Analysis", "Duration Analysis", "Payment Type Analysis"]
            )
            
            if analysis_type == "Fare vs Distance":
                fig = px.scatter(
                    df_filtered.sample(min(5000, len(df_filtered))),
                    x='trip_distance',
                    y='fare_amount',
                    color='pickup_hour',
                    size='total_amount',
                    hover_data=['trip_duration_minutes'],
                    title="Fare vs Distance",
                    labels={'trip_distance': 'Distance (miles)', 'fare_amount': 'Fare ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Tip Analysis":
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.box(
                        df_filtered,
                        y='tip_percentage',
                        title="Tip Percentage Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    tip_by_hour = df_filtered.groupby('pickup_hour')['tip_percentage'].mean().reset_index()
                    fig = px.bar(
                        tip_by_hour,
                        x='pickup_hour',
                        y='tip_percentage',
                        title="Average Tip % by Hour"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Duration Analysis":
                fig = px.histogram(
                    df_filtered,
                    x='trip_duration_minutes',
                    nbins=50,
                    title="Trip Duration Distribution",
                    labels={'trip_duration_minutes': 'Duration (minutes)', 'count': 'Frequency'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Payment Type Analysis":
                if 'payment_type' in df_filtered.columns:
                    payment_analysis = df_filtered.groupby('payment_type').agg({
                        'total_amount': ['sum', 'mean', 'count'],
                        'tip_amount': 'mean'
                    }).reset_index()
                    st.dataframe(payment_analysis, use_container_width=True)
                else:
                    st.info("Payment type data not available.")
    else:
        st.error("Unable to load data.")

# =============================
# PAGE 3 — SQL INSIGHTS
# =============================
elif page == "🧮 SQL Insights":
    st.title("🧮 SQL Analytics Results")
    st.markdown("---")
    
    if sql_results:
        st.subheader("Available SQL Queries")
        
        query_names = list(sql_results.keys())
        selected_query = st.selectbox(
            "Select SQL Query Result",
            query_names,
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        if selected_query:
            result_df = sql_results[selected_query]
            
            st.subheader(f"Results: {selected_query.replace('_', ' ').title()}")
            
            # Display metrics if applicable
            if len(result_df) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Records", len(result_df))
                
                # Try to find numeric columns for summary
                numeric_cols = result_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    with col2:
                        st.metric("Numeric Columns", len(numeric_cols))
            
            # Interactive table
            st.dataframe(result_df, use_container_width=True, hide_index=True)
            
            # Visualizations for numeric data
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 0:
                st.subheader("📊 Visualizations")
                
                viz_type = st.selectbox(
                    "Visualization Type",
                    ["Bar Chart", "Line Chart", "Scatter Plot", "Heatmap"]
                )
                
                if viz_type == "Bar Chart" and len(numeric_cols) > 0:
                    x_col = st.selectbox("X-axis", result_df.columns)
                    y_col = st.selectbox("Y-axis", numeric_cols)
                    
                    if x_col and y_col:
                        fig = px.bar(
                            result_df.head(20),
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} by {x_col}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Line Chart" and len(numeric_cols) > 0:
                    x_col = st.selectbox("X-axis", result_df.columns, key="line_x")
                    y_col = st.selectbox("Y-axis", numeric_cols, key="line_y")
                    
                    if x_col and y_col:
                        fig = px.line(
                            result_df.sort_values(x_col),
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} Trend by {x_col}",
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No SQL results found. Please run Task 3 to generate SQL analytics.")

# =============================
# PAGE 4 — SPARK ANALYTICS
# =============================
elif page == "⚡ Spark Analytics":
    st.title("⚡ PySpark ETL Results")
    st.markdown("---")
    
    if spark_results:
        st.subheader("Available Spark Outputs")
        
        spark_outputs = list(spark_results.keys())
        selected_output = st.selectbox(
            "Select Spark Output",
            spark_outputs,
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        if selected_output:
            result_df = spark_results[selected_output]
            
            st.subheader(f"Data: {selected_output.replace('_', ' ').title()}")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(result_df))
            with col2:
                st.metric("Columns", len(result_df.columns))
            with col3:
                numeric_cols = result_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.metric("Numeric Columns", len(numeric_cols))
            
            # Display data
            st.dataframe(result_df, use_container_width=True, hide_index=True)
            
            # Visualizations
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 0:
                st.subheader("📊 Visualizations")
                
                if 'pickup_year' in result_df.columns and 'pickup_month' in result_df.columns:
                    # Monthly revenue chart
                    if 'total_revenue' in result_df.columns:
                        result_df['date'] = pd.to_datetime(
                            dict(year=result_df['pickup_year'], month=result_df['pickup_month'], day=1)
                        )
                        result_df = result_df.sort_values('date')
                        
                        fig = px.line(
                            result_df,
                            x='date',
                            y='total_revenue',
                            title='Monthly Revenue (Spark Processed)',
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No Spark results found. Please run Task 4 to generate Spark analytics.")
        
        # Show available parquet directories
        if SPARK_DIR.exists():
            parquet_dirs = [d.name for d in SPARK_DIR.glob("*.parquet") if d.is_dir()]
            if parquet_dirs:
                st.info(f"Found Parquet directories: {', '.join(parquet_dirs)}")
                st.info("Note: Install PyArrow to load Parquet files: pip install pyarrow")

# =============================
# PAGE 5 — GENAI CHATBOT
# =============================
elif page == "🤖 GenAI Chatbot":
    st.title("🤖 GenAI Urban Mobility Insights Assistant")
    st.markdown("---")
    
    if not GENAI_AVAILABLE:
        st.error("GenAI Assistant is not available. Please check the configuration.")
        st.info("Make sure the GenAI assistant module is properly configured and dependencies are installed.")
    else:
        # Initialize assistant (cached)
        @st.cache_resource
        def init_assistant():
            try:
                # Use absolute paths relative to project root
                project_root = Path(__file__).parent.parent
                assistant = MobilityGenAIAssistant(
                    data_path=str(project_root / "data" / "cleaned" / "cleaned_taxi_data.csv"),
                    kpi_path=str(project_root / "outputs" / "kpi_report.txt"),
                    sql_results_dir=str(project_root / "outputs" / "sql_results")
                )
                assistant.load_context()
                return assistant
            except Exception as e:
                st.error(f"Error initializing assistant: {e}")
                import traceback
                st.code(traceback.format_exc())
                return None
        
        assistant = init_assistant()
        
        if assistant:
            # Chat interface
            st.markdown("""
            <div style='background-color: #e8f4f8; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h4>💡 Ask questions about your mobility data!</h4>
                <p>Examples:</p>
                <ul>
                    <li>"What were the busiest pickup zones?"</li>
                    <li>"When is surge demand highest during the day?"</li>
                    <li>"What are the peak hours for trips?"</li>
                    <li>"How does weekend demand compare to weekdays?"</li>
                    <li>"Why did revenue drop in February?"</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask a question about the mobility data..."):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = assistant.answer_question(prompt)
                            # Check if response is an error message
                            if response.startswith("Error generating answer:"):
                                st.error("⚠️ API Error: " + response)
                                st.info("💡 The GenAI service may be experiencing issues. Please try again later or check your API quota.")
                            else:
                                st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            error_msg = f"Error generating response: {str(e)}"
                            st.error("⚠️ " + error_msg)
                            if "quota" in error_msg.lower() or "429" in error_msg:
                                st.info("💡 API quota exceeded. Please check your API plan and billing details.")
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Quick action buttons
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Generate Monthly Summary"):
                    with st.spinner("Generating summary..."):
                        try:
                            # Get current month/year from data
                            if df is not None and 'pickup_month' in df.columns:
                                current_month = df['pickup_month'].iloc[0]
                                current_year = df['pickup_year'].iloc[0]
                                # Use answer_question instead of generate_monthly_summary
                                question = f"Generate a comprehensive monthly summary for {current_month:02d}/{current_year} including key metrics, trends, and insights."
                                summary = assistant.answer_question(question)
                                st.session_state.messages.append({"role": "assistant", "content": f"**Monthly Summary for {current_month:02d}/{current_year}:**\n\n{summary}"})
                                st.rerun()
                            else:
                                st.warning("Data not available for monthly summary.")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            with col2:
                if st.button("🔄 Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()
            
            with col3:
                if st.button("❓ Example Questions"):
                    examples = [
                        "What were the busiest pickup zones?",
                        "When is surge demand highest during the day?",
                        "What are the peak hours for trips?",
                        "How does weekend demand compare to weekdays?"
                    ]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "**Example Questions:**\n\n" + "\n".join([f"- {q}" for q in examples])
                    })
                    st.rerun()
        else:
            st.error("Failed to initialize GenAI Assistant. Please check the logs.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Intelligent Urban Mobility Analytics Platform | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)

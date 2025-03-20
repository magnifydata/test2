import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import scipy.stats as stats

# Set a wider default layout
st.set_page_config(layout="wide")

# --- Dark Mode Toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

st.sidebar.button("Toggle Dark Mode", on_click=toggle_dark_mode)

# --- Define Colors Based on Mode ---
if st.session_state.dark_mode:
    background_color = "#262730"  # Dark gray
    text_color = "#FAFAFA"       # Light gray
    sidebar_color = "#363740"     # Slightly lighter dark gray
    accent_color = "#6495ED"      # Cornflower blue
else:
    background_color = "#FFFFFF"  # White
    text_color = "#000000"       # Black
    sidebar_color = "#D4E6F1"     # Light Blue
    accent_color = "#2E86C1"      # Steel Blue

# --- Custom CSS for styling ---
st.markdown(
    f"""
    <style>
    .reportview-container .main .block-container{{
        max-width: 1200px;
    }}
    body {{
        background-color: {background_color} !important;
        color: {text_color} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {accent_color} !important;
    }}
    .stDataFrame {{
        border: 1px solid #EBF4FA;
        border-radius: 5px;
        padding: 10px;
        background-color: #F0F8FF;
        color: {text_color} !important;
    }}
    .streamlit-expanderHeader {{
        font-size: 1.2em !important;
        font-weight: bold !important;
        color: {text_color} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_color} !important;
        color: {text_color} !important; /* Sidebar text color */
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li, [data-testid="stSidebar"] ul, [data-testid="stSidebar"] ol{{
        color: {text_color} !important;
    }}
    .css-1adrfps {{
        color: {text_color}
    }}
    div.block-container.css-91a74f.egzxvld4{{
        color: {text_color}
    }}
    .css-1n76uv {{
        color: {text_color}
    }}
    .css-keje6w{{
        color: {text_color} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# Use Markdown/HTML to style the title
st.markdown(f"<h1 style='color: {accent_color};'>Employee Data Filter</h1>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    # Data Validation: Check for NaNs in 'Salary' and handle them.
    if df['Salary'].isnull().any():
        st.warning("Warning: Missing values found in 'Salary' column.  Filling with the mean.")
        df['Salary'] = df['Salary'].fillna(df['Salary'].mean())  # Fill with mean

    return df

try:
    df = load_data()

    # Calculate summary metrics
    total_employees = len(df)
    average_salary = df["Salary"].mean()

    with st.sidebar:  # Put sidebar elements in a 'with' block
        st.header("Filter Options")

        # Multiselect widget for filtering by category (in the sidebar)
        selected_categories = st.multiselect(
            "Select Employee Categories:",
            options=df["Category"].unique(),
            default=df["Category"].unique(),
        )

        # Multiselect widget for filtering by department
        selected_departments = st.multiselect(
            "Select Departments:",
            options=df["Department"].unique(),
            default=df["Department"].unique(),
        )

        # Slider for filtering by salary (in the sidebar)
        min_salary = float(df["Salary"].min())
        max_salary = float(df["Salary"].max())
        salary_range = st.slider(
            "Select Salary Range ($):",
            min_value=min_salary,
            max_value=max_salary,
            value=(min_salary, max_salary),
        )

        # Text input for filtering by name or city
        search_term = st.text_input("Search by Name or City:", "")

    # Filter the DataFrame
    filtered_df = df[
        (df["Category"].isin(selected_categories)) &
        (df["Department"].isin(selected_departments)) &
        (df["Salary"] >= salary_range[0]) &
        (df["Salary"] <= salary_range[1])
    ]

    # Filter by search term (name or city)
    if search_term:
        filtered_df = filtered_df[
            (filtered_df["Name"].str.contains(search_term, case=False)) |
            (filtered_df["City"].str.contains(search_term, case=False))
        ]

    # Dynamic Chart Title
    chart_title_suffix = f" (Filtered)" if len(filtered_df) < len(df) else ""

    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Employees", total_employees)
    with col2:
        st.metric("Average Salary", f"${average_salary:,.2f}")  # Format with commas and 2 decimals

    # Calculate average salary per category for the filtered data
    avg_salary_per_category = filtered_df.groupby("Category")["Salary"].mean().reset_index()

    # --- CHART SECTION ---
    # Chart type selector
    chart_type = st.selectbox("Select Chart Type:", ["Bar Chart", "Pie Chart", "Scatter Chart", "Histogram", "Box Plot"])

    if chart_type == "Bar Chart":
        fig = px.bar(
            avg_salary_per_category,
            x="Category",
            y="Salary",
            labels={"Category": "Employee Category", "Salary": "Average Salary ($)"},
            title=f"Average Salary per Employee Category{chart_title_suffix}",
            height=400,
            hover_data=["Salary"]  # Add Salary to hover data
        )
    elif chart_type == "Pie Chart":
        fig = px.pie(
            avg_salary_per_category,
            values="Salary",
            names="Category",
            title=f"Average Salary per Employee Category{chart_title_suffix}",
            height=400,
            hover_data=["Salary"]  # Add Salary to hover data
        )
    elif chart_type == "Scatter Chart":
        # Add Age to scatter chart
        fig = px.scatter(
           filtered_df, # scatter charts takes the entire data frame.
           x="Category",
           y="Salary",
           size="Age",
           color="Category",
           hover_data=['Name', 'Age', 'City'],
           labels={"Category": "Employee Category", "Salary": "Salary ($)"},
           title=f"Salary vs Category (Size: Age){chart_title_suffix}",
           height=400 # Adjust height as needed
       )
    elif chart_type == "Histogram":
        fig = px.histogram(
            filtered_df,
            x="Salary",
            nbins=20, # Adjust the number of bins as needed
            title=f"Salary Distribution{chart_title_suffix}",
            labels={"Salary": "Salary ($)"}
        )
    elif chart_type == "Box Plot":
        fig = px.box(
            filtered_df,
            x="Category",
            y="Salary",
            color="Category",
            title=f"Salary Distribution by Category{chart_title_suffix}",
            labels={"Salary": "Salary ($)", "Category": "Employee Category"}
        )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(" ")  # Add a small caption for spacing

    # --- Correlation Analysis ---
    st.subheader("Correlation Analysis")
    numeric_columns = filtered_df.select_dtypes(include=np.number).columns.tolist() # Get numeric columns
    if len(numeric_columns) > 1:
        selected_columns = st.multiselect("Select columns for correlation analysis:", numeric_columns, default=numeric_columns[:2]) # select column
        if len(selected_columns) >= 2:
            correlation_matrix = filtered_df[selected_columns].corr(method='pearson') # generates the correlation value
            fig_corr = px.imshow(correlation_matrix,
                                  labels=dict(x="Columns", y="Columns", color="Correlation"),
                                  x=selected_columns,
                                  y=selected_columns,
                                  color_continuous_scale="RdBu", # red-blue color scheme
                                  title=f"Correlation Heatmap{chart_title_suffix}")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Please select at least two numeric columns for correlation analysis.")
    else:
        st.warning("No numeric columns found for correlation analysis.")

    # --- EMPLOYEE INFORMATION SECTION ---
    with st.expander("Employee Information", expanded=False):
        st.markdown("<h2 style='text-align: left;'>Employee Information</h2>", unsafe_allow_html=True)
        data_editor = st.data_editor(filtered_df)

        st.write(f"Number of results: {len(filtered_df)}")

        # Add download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Filtered Data",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv",
            key='download-csv'
        )

except FileNotFoundError:
    st.error("Error: data.csv not found.")
except KeyError as e:
    st.error(
        f"Error: Column '{e}' not found in data.csv.  Make sure 'Salary' and 'Category' and 'Department' columns exist."
    )
except ValueError:
    st.error(
        "Error: 'Salary' column contains non-numeric values. Please ensure it only contains numbers."
    )

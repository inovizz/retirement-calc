import streamlit as st
import pandas as pd
import numpy as np
import yaml
import plotly.graph_objs as go

def calculate_corpus(monthly_contribution, years, annual_return, initial_amount=0):
    months = years * 12
    monthly_rate = (1 + annual_return) ** (1/12) - 1
    future_value = initial_amount * (1 + annual_return) ** years
    corpus = monthly_contribution * ((1 + monthly_rate) ** months - 1) / monthly_rate * (1 + monthly_rate)
    return round(corpus + future_value, 2)

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

def get_default_values():
    return {
        'current_savings': {category: 0.0 for category in ['Stocks', 'Mutual Funds', 'ESOPs', 'EPF', 'Gold Bond', 'Fixed Deposits', 'Other Savings']},
        'monthly_income': 0.0,
        'monthly_breakdown': [
            {'category': category, 'amount': 0.0}
            for category in ['Living Expenses', 'Home Loan EMIs', 'Retirement Savings', 'Short-Term Goals', 'Other Savings']
        ],
        'personal_info': {
            'current_age': 30,
            'retirement_age': 60,
            'num_kids': 0,
            'kids_ages': [],
            'education_start_ages': []
        },
        'page': 'input'
    }

# Initialize session state with default values
if 'initialized' not in st.session_state:
    default_values = get_default_values()
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.initialized = True

def reset_to_default():
    default_values = get_default_values()
    for key, value in default_values.items():
        st.session_state[key] = value

def load_data_from_yaml():
    st.session_state.current_savings = {k: float(v) for k, v in config['current_savings'].items()}
    st.session_state.monthly_income = float(config['monthly_income'])
    st.session_state.monthly_breakdown = [
        {'category': item['category'], 'amount': float(item['amount'])}
        for item in config['monthly_breakdown']
    ]
    st.session_state.personal_info = config.get('personal_info', get_default_values()['personal_info'])

def input_page():
    st.title('Retirement Corpus Calculator')

    # Load and Reset buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Load Dummy Data'):
            load_data_from_yaml()
            st.success("Data loaded!")
            st.rerun()

    with col2:
        if st.button('Reset All to Default'):
            reset_to_default()
            st.success("All data reset to default values")
            st.rerun()

    # Personal Information
    st.header('Personal Information')
    current_age = st.number_input('Your Current Age', value=st.session_state.personal_info['current_age'], min_value=18, max_value=100)
    retirement_age = st.number_input('Expected Retirement Age', value=st.session_state.personal_info['retirement_age'], min_value=current_age, max_value=100)
    num_kids = st.number_input('Number of Kids', value=st.session_state.personal_info['num_kids'], min_value=0, max_value=10, step=1)

    kids_ages = []
    education_start_ages = []
    for i in range(num_kids):
        col1, col2 = st.columns(2)
        with col1:
            kid_age = st.number_input(f'Age of Kid {i+1}', value=st.session_state.personal_info['kids_ages'][i] if i < len(st.session_state.personal_info['kids_ages']) else 0, min_value=0, max_value=30)
            kids_ages.append(kid_age)
        with col2:
            edu_start_age = st.number_input(f'Education Start Age for Kid {i+1}', value=st.session_state.personal_info['education_start_ages'][i] if i < len(st.session_state.personal_info['education_start_ages']) else 18, min_value=kid_age, max_value=30)
            education_start_ages.append(edu_start_age)

    st.session_state.personal_info = {
        'current_age': current_age,
        'retirement_age': retirement_age,
        'num_kids': num_kids,
        'kids_ages': kids_ages,
        'education_start_ages': education_start_ages
    }

    # Monthly Income
    st.header('Monthly Income')
    st.session_state.monthly_income = st.number_input(
        'Monthly Income (INR)', 
        value=st.session_state.monthly_income,
        min_value=0.0,
        step=1000.0,
        format="%.2f",
        key="monthly_income_widget"
    )

    # Monthly Breakdown
    st.header('Monthly Breakdown')
    default_categories = ['Living Expenses', 'Home Loan EMIs', 'Retirement Savings']
    for i in range(num_kids):
        default_categories.append(f"Kid-{i+1} Education Saving")
    default_categories.extend(['Short-Term Goals', 'Other Savings'])

    st.session_state.monthly_breakdown = [
        item for item in st.session_state.monthly_breakdown
        if item['category'] in default_categories
    ]

    for category in default_categories:
        if not any(item['category'] == category for item in st.session_state.monthly_breakdown):
            st.session_state.monthly_breakdown.append({'category': category, 'amount': 0.0})

    total_monthly_allocation = 0
    for item in st.session_state.monthly_breakdown:
        item['amount'] = st.number_input(
            f"{item['category']} (INR)",
            value=float(item['amount']),
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key=f"monthly_breakdown_input_{item['category']}"
        )
        total_monthly_allocation += item['amount']

    # Warning for overspending
    if total_monthly_allocation > st.session_state.monthly_income:
        st.warning(f"⚠️ Warning: Your total monthly allocation (₹{total_monthly_allocation:,.2f}) exceeds your monthly income (₹{st.session_state.monthly_income:,.2f})!")
    
    # Display summary
    st.subheader('Monthly Summary')
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{st.session_state.monthly_income:,.2f}")
    col2.metric("Total Allocation", f"₹{total_monthly_allocation:,.2f}")
    
    disposable_income = st.session_state.monthly_income - total_monthly_allocation
    col3.metric("Disposable Income", f"₹{disposable_income:,.2f}", 
                delta=f"₹{disposable_income:,.2f}", 
                delta_color="normal" if disposable_income >= 0 else "inverse")

    # Current Savings
    st.header('Current Savings')
    savings_categories = ['Stocks', 'Mutual Funds', 'ESOPs', 'EPF', 'Gold Bond', 'Fixed Deposits', 'Other Savings']
    for category in savings_categories:
        st.session_state.current_savings[category] = st.number_input(
            f'{category} (INR)', 
            value=st.session_state.current_savings.get(category, 0.0),
            min_value=0.0,
            step=1000.0,
            format="%.2f",
            key=f"current_savings_input_{category}"
        )

    if st.button('Proceed to Calculations'):
        st.session_state.page = 'calculation'
        st.rerun()

def calculation_page():
    st.title('Retirement Savings and Corpus Projections')

    # Calculate years to retirement
    years_to_retirement = st.session_state.personal_info['retirement_age'] - st.session_state.personal_info['current_age']

    # Display summary of inputs
    st.header('Input Summary')
    st.write(f"Years to Retirement: {years_to_retirement}")
    st.write(f"Total Current Savings: INR {sum(st.session_state.current_savings.values()):,.2f}")
    st.write(f"Monthly Income: INR {st.session_state.monthly_income:,.2f}")

    # Monthly Breakdown Summary
    total_monthly_allocation = sum(item['amount'] for item in st.session_state.monthly_breakdown)
    disposable_income = st.session_state.monthly_income - total_monthly_allocation

    st.subheader('Monthly Breakdown Summary')
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{st.session_state.monthly_income:,.2f}")
    col2.metric("Total Expenses", f"₹{total_monthly_allocation:,.2f}")
    col3.metric("Disposable Income", f"₹{disposable_income:,.2f}", 
                delta=f"₹{disposable_income:,.2f}", 
                delta_color="normal" if disposable_income >= 0 else "inverse")

    if total_monthly_allocation > st.session_state.monthly_income:
        st.warning('⚠️ Warning: Your total expenses exceed your monthly income!')

    # Visualize expense breakdown
    st.subheader('Expense Breakdown')
    expense_data = {item['category']: item['amount'] for item in st.session_state.monthly_breakdown}
    fig = go.Figure(data=[go.Pie(labels=list(expense_data.keys()), values=list(expense_data.values()))])
    fig.update_layout(height=300, width=500)
    st.plotly_chart(fig)

    # Expected returns
    expected_return = st.slider('Expected Annual Return (%)', 
                                min_value=0.0, 
                                max_value=20.0, 
                                value=float(config['default_expected_return']),
                                step=0.1) / 100

    # Corpus Projection
    st.header('Corpus Projection')
    projection_data = {
        'Goal': [],
        'Years': [],
        'Monthly Contribution': [],
        'Initial Amount': []
    }

    total_current_savings = sum(st.session_state.current_savings.values())

    # Retirement projection
    projection_data['Goal'].append('Retirement')
    projection_data['Years'].append(years_to_retirement)
    retirement_contribution = next((item['amount'] for item in st.session_state.monthly_breakdown if item['category'] == 'Retirement Savings'), 0)
    projection_data['Monthly Contribution'].append(retirement_contribution)
    projection_data['Initial Amount'].append(total_current_savings)

    # Kids education projections
    for i in range(st.session_state.personal_info['num_kids']):
        years_to_education = st.session_state.personal_info['education_start_ages'][i] - st.session_state.personal_info['kids_ages'][i]
        projection_data['Goal'].append(f'Kid-{i+1} Education')
        projection_data['Years'].append(years_to_education)
        edu_contribution = next((item['amount'] for item in st.session_state.monthly_breakdown if item['category'] == f'Kid-{i+1} Education Saving'), 0)
        projection_data['Monthly Contribution'].append(edu_contribution)
        projection_data['Initial Amount'].append(0)

    # Short-term goals projection
    short_term_contribution = next((item['amount'] for item in st.session_state.monthly_breakdown if item['category'] == 'Short-Term Goals'), 0)
    projection_data['Goal'].append('Short-Term Goals')
    projection_data['Years'].append(5)  # Assuming 5 years for short-term goals
    projection_data['Monthly Contribution'].append(short_term_contribution)
    projection_data['Initial Amount'].append(0)

    # Other savings projection
    other_savings_contribution = next((item['amount'] for item in st.session_state.monthly_breakdown if item['category'] == 'Other Savings'), 0)
    projection_data['Goal'].append('Other Savings')
    projection_data['Years'].append(years_to_retirement)
    projection_data['Monthly Contribution'].append(other_savings_contribution)
    projection_data['Initial Amount'].append(0)

    df_projection = pd.DataFrame(projection_data)

    df_projection['Projected Corpus'] = df_projection.apply(lambda row: calculate_corpus(row['Monthly Contribution'], row['Years'], expected_return, row['Initial Amount']), axis=1)

    # Round all numeric columns to 2 decimal places
    numeric_columns = df_projection.select_dtypes(include=[np.number]).columns
    df_projection[numeric_columns] = df_projection[numeric_columns].round(2)

    st.dataframe(df_projection)

    # Visualization of Projected Corpus
    st.subheader('Projected Corpus for Each Goal')
    fig = go.Figure(data=[go.Bar(x=df_projection['Goal'], y=df_projection['Projected Corpus'])])
    fig.update_layout(xaxis_title='Goal', yaxis_title='Projected Corpus (INR)')
    st.plotly_chart(fig)

    # Download link for the data
    csv = df_projection.to_csv(index=False)
    st.download_button(
        label="Download projection data as CSV",
        data=csv,
        file_name="financial_projection.csv",
        mime="text/csv",
    )

    if st.button('Back to Input Page'):
        st.session_state.page = 'input'
        st.rerun()

# Main app logic
if st.session_state.page == 'input':
    input_page()
elif st.session_state.page == 'calculation':
    calculation_page()
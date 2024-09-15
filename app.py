import streamlit as st
import pandas as pd
import numpy as np
import yaml
import plotly.graph_objs as go

@st.cache_data
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

@st.cache_data
def calculate_corpus(monthly_contribution, years, annual_return, initial_amount=0, annual_step_up=0):
    corpus = initial_amount
    for year in range(int(years)):
        yearly_contribution = monthly_contribution * 12 * (1 + annual_step_up) ** year
        corpus = (corpus + yearly_contribution) * (1 + annual_return)
    return round(corpus, 2)

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
        'page': 'input',
        'annual_savings_increase': 0.0
    }

# Initialize session state
if 'initialized' not in st.session_state:
    default_values = get_default_values()
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.initialized = True

@st.cache_data
def reset_to_default():
    return get_default_values()

@st.cache_data
def load_data_from_yaml(config):
    return {
        'current_savings': {k: float(v) for k, v in config['current_savings'].items()},
        'monthly_income': float(config['monthly_income']),
        'monthly_breakdown': [
            {'category': item['category'], 'amount': float(item['amount'])}
            for item in config['monthly_breakdown']
        ],
        'personal_info': config.get('personal_info', get_default_values()['personal_info']),
        'annual_savings_increase': 0.0
    }

def input_page():
    st.title('Retirement Corpus Calculator')

    config = load_config()

    with st.form("input_form"):
        # Load and Reset buttons
        col1, col2 = st.columns(2)
        with col1:
            load_dummy = st.form_submit_button('Load Dummy Data')
        with col2:
            reset_all = st.form_submit_button('Reset All to Default')

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
                edu_start_age = st.number_input(f'Higher Education Start Age for Kid {i+1}', value=st.session_state.personal_info['education_start_ages'][i] if i < len(st.session_state.personal_info['education_start_ages']) else 18, min_value=kid_age, max_value=30)
                education_start_ages.append(edu_start_age)

        # Monthly Income
        st.header('Monthly Income')
        monthly_income = st.number_input('Monthly Income (INR)', value=st.session_state.monthly_income, min_value=0.0, step=1000.0, format="%.2f")

        # Annual Savings Increase
        st.header('Annual Savings Increase')
        annual_savings_increase = st.number_input('Annual Savings Increase (%)', value=st.session_state.annual_savings_increase * 100, min_value=0.0, max_value=100.0, step=0.1) / 100

        # Monthly Breakdown
        st.header('Monthly Breakdown')
        default_categories = ['Living Expenses', 'Home Loan EMIs', 'Retirement Savings']
        for i in range(num_kids):
            default_categories.append(f"Kid-{i+1} Education Saving")
        default_categories.extend(['Short-Term Goals', 'Other Savings'])

        monthly_breakdown = []
        for category in default_categories:
            amount = next((item['amount'] for item in st.session_state.monthly_breakdown if item['category'] == category), 0.0)
            amount = st.number_input(f"{category} (INR)", value=float(amount), min_value=0.0, step=100.0, format="%.2f")
            monthly_breakdown.append({'category': category, 'amount': amount})

        # Current Savings
        st.header('Current Savings')
        savings_categories = ['Stocks', 'Mutual Funds', 'ESOPs', 'EPF', 'Gold Bond', 'Fixed Deposits', 'Other Savings']
        current_savings = {}
        for category in savings_categories:
            current_savings[category] = st.number_input(f'{category} (INR)', value=st.session_state.current_savings.get(category, 0.0), min_value=0.0, step=1000.0, format="%.2f")

        submitted = st.form_submit_button("Proceed to Calculations")

    if submitted:
        st.session_state.personal_info = {
            'current_age': current_age,
            'retirement_age': retirement_age,
            'num_kids': num_kids,
            'kids_ages': kids_ages,
            'education_start_ages': education_start_ages
        }
        st.session_state.monthly_income = monthly_income
        st.session_state.monthly_breakdown = monthly_breakdown
        st.session_state.current_savings = current_savings
        st.session_state.annual_savings_increase = annual_savings_increase
        st.session_state.page = 'calculation'
        st.rerun()

    if load_dummy:
        dummy_data = load_data_from_yaml(config)
        for key, value in dummy_data.items():
            st.session_state[key] = value
        st.success("Data loaded!")
        st.rerun()

    if reset_all:
        default_values = reset_to_default()
        for key, value in default_values.items():
            st.session_state[key] = value
        st.success("All data reset to default values")
        st.rerun()

@st.cache_data
def prepare_projection_data(personal_info, monthly_breakdown, current_savings, annual_savings_increase):
    years_to_retirement = personal_info['retirement_age'] - personal_info['current_age']
    total_current_savings = sum(current_savings.values())

    projection_data = {
        'Goal': ['Retirement'],
        'Years': [years_to_retirement],
        'Monthly Contribution': [next((item['amount'] for item in monthly_breakdown if item['category'] == 'Retirement Savings'), 0)],
        'Initial Amount': [total_current_savings],
        'Annual Savings Increase': [annual_savings_increase]
    }

    for i in range(personal_info['num_kids']):
        years_to_education = personal_info['education_start_ages'][i] - personal_info['kids_ages'][i]
        projection_data['Goal'].append(f'Kid-{i+1} Education')
        projection_data['Years'].append(years_to_education)
        projection_data['Monthly Contribution'].append(next((item['amount'] for item in monthly_breakdown if item['category'] == f'Kid-{i+1} Education Saving'), 0))
        projection_data['Initial Amount'].append(0)
        projection_data['Annual Savings Increase'].append(annual_savings_increase)

    projection_data['Goal'].append('Short-Term Goals')
    projection_data['Years'].append(5)
    projection_data['Monthly Contribution'].append(next((item['amount'] for item in monthly_breakdown if item['category'] == 'Short-Term Goals'), 0))
    projection_data['Initial Amount'].append(0)
    projection_data['Annual Savings Increase'].append(annual_savings_increase)

    projection_data['Goal'].append('Other Savings')
    projection_data['Years'].append(years_to_retirement)
    projection_data['Monthly Contribution'].append(next((item['amount'] for item in monthly_breakdown if item['category'] == 'Other Savings'), 0))
    projection_data['Initial Amount'].append(0)
    projection_data['Annual Savings Increase'].append(annual_savings_increase)

    return pd.DataFrame(projection_data)

def calculation_page():
    st.title('Retirement Savings and Corpus Projections')

    years_to_retirement = st.session_state.personal_info['retirement_age'] - st.session_state.personal_info['current_age']

    st.header('Input Summary')
    st.write(f"Years to Retirement: {years_to_retirement}")
    st.write(f"Total Current Savings: INR {sum(st.session_state.current_savings.values()):,.2f}")
    st.write(f"Monthly Income: INR {st.session_state.monthly_income:,.2f}")
    st.write(f"Annual Savings Increase: {st.session_state.annual_savings_increase:.2%}")

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

    st.subheader('Expense Breakdown')
    expense_data = {item['category']: item['amount'] for item in st.session_state.monthly_breakdown}
    fig = go.Figure(data=[go.Pie(labels=list(expense_data.keys()), values=list(expense_data.values()))])
    fig.update_layout(height=300, width=500)
    st.plotly_chart(fig)

    expected_return = st.slider('Expected Annual Return (%) on Savings', 
                                min_value=0.0, 
                                max_value=20.0, 
                                value=float(load_config()['default_expected_return']),
                                step=0.1) / 100

    st.header('Corpus Projection')
    df_projection = prepare_projection_data(st.session_state.personal_info, st.session_state.monthly_breakdown, st.session_state.current_savings, st.session_state.annual_savings_increase)

    df_projection['Projected Corpus'] = df_projection.apply(lambda row: calculate_corpus(row['Monthly Contribution'], row['Years'], expected_return, row['Initial Amount'], row['Annual Savings Increase']), axis=1)

    numeric_columns = df_projection.select_dtypes(include=[np.number]).columns
    df_projection[numeric_columns] = df_projection[numeric_columns].round(2)

    st.dataframe(df_projection)

    st.subheader('Projected Corpus for Each Goal')
    fig = go.Figure(data=[go.Bar(x=df_projection['Goal'], y=df_projection['Projected Corpus'])])
    fig.update_layout(xaxis_title='Goal', yaxis_title='Projected Corpus (INR)')
    st.plotly_chart(fig)

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

if 'page' not in st.session_state:
    st.session_state.page = 'input'

if st.session_state.page == 'input':
    input_page()
elif st.session_state.page == 'calculation':
    calculation_page()
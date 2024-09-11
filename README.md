
# Retirement Corpus Planner

This app is designed to help users project their retirement corpus based on their current savings, monthly income, and breakdown of expenses. The app uses financial planning strategies to provide insights into future goals and savings targets.

## Features

- View your current savings and monthly income details.
- Input personalized financial goals like retirement or education savings.
- Visualize the projected savings corpus over time.
  
## Requirements

The app requires the following Python packages:

```bash
pandas
numpy
pyyaml
plotly
```

## Files

1. **app.py**: The main script that runs the app.
2. **requirements.txt**: A list of dependencies required to run the app.
3. **config.yaml**: A configuration file containing current savings, monthly income, and projection goals.

## Configuration

The `config.yaml` file is essential for setting up your financial details. Below is a brief structure of the configuration:

```yaml
# Current Savings
current_savings:
  Stocks: 1200000.0
  Mutual Funds: 500000.0
  ...

# Monthly Income
monthly_income: 125000.0

# Monthly Breakdown (Example)
monthly_breakdown:
  - category: Living Expenses
    amount: 35000.0
  - category: Home Loan EMIs
    amount: 25000.0
  ...

# Corpus Projection
corpus_projection:
  - goal: Retirement
    years: 27
  - goal: Kid-1 Education Saving
    years: 10

# Personal Information
personal_info:
  current_age: 28
  retirement_age: 55
  num_kids: 1
  kids_ages: [3]
  education_start_ages: [18]

# Default Expected Return
default_expected_return: 10
```

## Running the App Locally

### Step 1: Clone the repository

Clone the repository or download the source files to your local machine.

### Step 2: Install dependencies

Navigate to the project directory and install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

### Step 3: Set up configuration

Edit the `config.yaml` file to match your personal financial information.

### Step 4: Run the app

Use the following command to start the app locally:

```bash
streamlit run app.py
```

### Step 5: Access the app

Once the app is running, open your web browser and navigate to:

```
http://localhost:8501
```

## Future Enhancements

- Adding more customizable financial goals.
- More detailed projections and charts.
- Integration with external financial APIs.

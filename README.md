# LifeMarket
A real-world lifetime cashflow simulator that answers key questions pertaining to a user's financial future.

**Key Questions Answered:**
- When does buying a house break even compared to renting?
- What is the total cost of car ownership over 5 years?
- Should I aggressively pay off student loans or invest the money?
- What will my monthly burn rate be in 3 years with expected cost increases?

## Installation

### Requirements
- Python 3.12 or higher
- pip package manager
- Virtual environment tool (venv)

### Setup Instructions
1. Clone the repository:
```bash
git clone 
cd lifemarket
```

2. Create virtual environment:
```bash
python3.12 -m venv .venv
```

3. Activate virtual environment:
```bash
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install pydantic python-dateutil pandas pyyaml pytest
```

5. Verify installation:
```bash
python -c "from pydantic import BaseModel; from dateutil.relativedelta import relativedelta; import pandas as pd; print('Installation successful')"
```

### VS Code Setup
1. Open Command Palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Select "Python: Select Interpreter"
3. Choose the `.venv` interpreter

## Project Structure
```
lifemarket/
├── domain/                      # Pure business logic (no I/O)
│   ├── models/                  # Data schemas (Pydantic)
│   │   ├── __init__.py         # Central imports
│   │   ├── base.py             # GlobalInputs, RateSpec, enums
│   │   ├── housing.py          # RentInputs, MortgageInputs
│   │   ├── transport.py        # CarInputs, TransitInputs
│   │   ├── debt.py             # StudentLoanInputs
│   │   ├── insurance.py        # HealthInsuranceInputs
│   │   ├── taxes.py            # TaxInputs
│   │   └── living.py           # LivingExpensesInputs
│   │
│   ├── modules/                 # Calculation functions
│   │   ├── __init__.py
│   │   ├── housing.py          # rent_cashflow(), mortgage_cashflow()
│   │   ├── transport.py        # car_cashflow()
│   │   ├── debt.py             # loan_amortization()
│   │   ├── insurance.py        # insurance_cashflow()
│   │   ├── taxes.py            # tax_cashflow()
│   │   └── living.py           # living_expenses_cashflow()
│   │
│   ├── user_profile.py         # User identity & current expenses
│   ├── user_preferences.py     # Economic assumptions & growth rates
│   ├── timeline.py             # Date range builders
│   ├── inflation.py            # Deflator helpers (display only)
│   └── aggregator.py           # Combine outputs, calculate KPIs
│
├── application/                 # Orchestration layer
│   ├── config_loader.py        # Load/merge profile+preferences+scenario
│   ├── simulate.py             # Main simulation runner
│   ├── validator.py            # Pre-flight validation
│   └── rates.py                # Resolve RateSpec to pandas Series
│
├── adapters/                    # I/O layer
│   ├── user_store/             # Profile persistence (JSON/DB)
│   ├── data_providers/         # External API clients (FRED, CPI)
│   └── exporters/              # CSV/Excel/PDF output
│
├── tests/
│   ├── unit/                   # Domain module tests (no I/O)
│   ├── integration/            # Adapter tests with mocks
│   └── e2e/                    # End-to-end simulation tests
│
├── configs/
│   ├── profiles/               # User profile examples
│   ├── preferences/            # Economic assumption sets
│   └── scenarios/              # Scenario configurations
│
├── docs/                        # Documentation
├── .venv/                      # Virtual environment (gitignored)
├── .gitignore
├── requirements.txt
├── pytest.ini
├── pyproject.toml
└── README.md
```

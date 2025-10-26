"""
File Purpose: Main place to define the data models for the simulation engine.
    - Inputs machine expects for each module (types, defaults, constraints).
    - Outputs utilized by aggregator and UI.
    - App-wide settings (user-tunable defaults).
    - Data organization blueprint and minimal overhead with high efficiency.
    - Utilizes 3 part system (schema defaults -> user settings -> line provider)
        * Implemented in application/rates.py using these schemas.
        * Providers live under domain/providers/.
        * Keeps models pure and system easy to test and evolve.

Reasoning: Helps make math modules simpler and predictable. Use this file if changing a field is necessary.

Use: 
    - Import the modules and accept them as parameters.
    - Add new models here when creating new modules.

Definitions:
    - Schema: formal description of data -> what fields exist, their types, defaults, and rules
        - Example...
        RentInputs Schema:
            - Fields: base_monthly_rent: float, roommates: int >= 0, renters_insurance_monthly: float >= 0
            - Purpose: Any bad inputs are caught before the math actually runs
    - Shape: the structure of a data object (its fields)
        - Example...
        RateSchedule(kind, by_year) is one shape
    - Union: a type that can be one of several shapes
        - Example...
        RateSpec = RateValue | RateSchedule | RateProvider
    - Discriminated Union: a union that uses a special field (kind) to decide which shape to parse
        - Example...
        Annotated[Union, Field(discriminator="kind")]
"""

# Allows for forward references before classes are defined. Improves clarity and compatibility.
from __future__ import annotations

# Represents scenario windows as real calendar dates from start to end, making timeline building more straightforward.
from datetime import date

# Controlled string choices and avoids typos. Enables editor autocomplete and better validation.
from enum import Enum 

# Typing primitives used in Schemas
# - Dict/Any: Free-form maps for parameters and flexible configs.
# - Literal: Used to "tag" union models like RateSpec
# - Annotated: Treats the union as a discriminated union
from typing import Dict, Any, Literal, Annotated

# Pydantic version 2.6 - Ensures that validation is fast and keeps schemas clean for 3 part system.
# - BaseModel: core class for typed, validated objects.
# - Field: attach defaults, bounds (ge/le/gt/lt), descriptions.
# - PositiveFloat: convenience type that enforces > 0.
# - model_validator: cross-field validation hook (end_date > start_date).
from pydantic import BaseModel, Field, PositiveFloat, model_validator

# ...................................................CONSTANTS...........................................................

# Used to increment when breaking changes are made to schemas so downstream code can detect mismatches.
SCHEMA_VERSION: str = "0.1.0"

# .....................................................ENUMS.............................................................

# Federal filing status. The state differentiation can be handled later.
class FilingStatus(str, Enum):
    single = "single"
    married = "married"

# .........................................FLEXIBLE RATE SPEC (3 PART SYSTEM)............................................

# Identifies the shape through "kind" and bounds the annual growth rate as a decimal (Ex: 0.03 = 3%).
class RateValue(BaseModel):
    kind: Literal["value"] = "value"
    annual: float = Field(0.03, ge = -1.0, le = 2.0, description = "Annual growth rate as a decimal")

# Represents the varying growth rates by year (Ex: 2020 @ 4% growth && 2022 @ 3.5% growth).
class RateSchedule(BaseModel):
    kind: Literal["schedule"] = "schedule"
    by_year: Dict[int, float]

# Specifies the rate that should be fetched from an outside provider.
# The source will accept any string for now until the outside provider is implemented (Placeholder structure).
class RateProvider(BaseModel):
    kind: Literal["provider"] = "provider"
    source: str = Field(..., description="Provider identifier (Examples...)")
    param: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    
# .........................................RATE SPEC UNION (3 PART SYSTEM - COMPLETE)....................................

# Brings together all specifications of the rate specifications (value, schedule, and provider options).
# Pydantic determines which model to parse (discriminator=kind) so it can understand which shape to parse through.
# Math modules recieve this type so application.py and rates.py can resolve it to actual series data.
# Use: Annotated(actual type, metadata(Ex: Field))
RateSpec = Annotated[RateValue | RateSchedule | RateProvider, Field(discriminator="kind")]

# ...............................................REPORTING DEFLATOR OPTIONS..............................................

# Creates the deflator that will determine which conversion to use (None, fixed deflation rate, provided rate).
# Only affects the user's "real" value columns NOT the values used in calculations.
class ReportingDeflator(str, Enum):
    none = "none" # No deflation - Shows dollar values for what they are.
    fixed_rate = "fixed_rate" # Applies a constant deflation rate
    provider = "provider" # Uses an external provider to fetch rates

# ..........................................GLOBAL INPUTS (SIMULATION-WIDE SETTINGS).....................................
# NOTE: User profiles are managed separately in domain/user_profile.py and adapters/user_store/.
# The global inputs will auto-populate from the user's profile by the application/config_loader.py

# Configuration settings that apply to the entire simulation.
# Keeps category growth independent while also allowing optional reporting adjustments.
class GlobalInputs(BaseModel):

    # Compares versions to warn if it is using an old saved scenario.
    schema_version: str = Field(SCHEMA_VERSION, description="Schema version used to check compatibility")
    
    # Simulation timeline window.
    # Birth date for the age based timeline which is autopopulated if profile is filled out.
    birth_date: date | None = Field(None, 
        description="Birth date for the age based timeline which is autopopulated if profile is filled out")
    # Current age which is automatically calulcated from the birth_date unless it isn't provided.
    # Used as a reference point for the age-based timeline mode.
    current_age: float | None = Field(None, 
        description="Current age which is automatically calulcated from the birth_date unless it isn't provided")
    # Determines whether the dates are specified directly or calculated from given age.
    timeline_mode: Literal["date", "age"] = Field("date", 
        description="Specifies 'date' for direct dates and 'age' for age-based calculations")
    

    # Used when the timeline_mode is only in "age".
    # Start age defaults to current_age if not specified and end_age defaults to end_option preset if not specified.
    start_age_years: int | None = Field(None, ge = 0, le = 120,
        description = "Starting age for the simulation in whole years where 'None' means to use the current_age")
    start_age_months: int | None = Field(None, ge = 0, le = 11,
        description = "Starting age for the simulation in months")
    
    # End age in years and months.
    end_age_years: int | None = Field(None, ge = 0, le = 120,
        description="Ending age for simulation in years where 'None' means to use the end_option preset")
    end_age_months: int | None = Field(None, ge = 0, le = 11,
        description="Ending age for the simulation in months")

    end_option: Literal["retirement", "lifespan"] | None = Field("retirement", 
        description="The present endpoint when end_age is not specified ('retirement' = 67 and 'lifespan' = 80)")


    # Actual timeline dates used in simulation (either provided directly or calculated from ages).
    # Fields are required but can be "None" initially if it is using age-based mode.
    start_date: date | None = Field(None,
        description="First month of simulation (YYYY-MM-DD) - calculated if it is on age-based mode")
    end_date: date | None = Field(None,
        description="Last month of simulation (YYYY-MM-DD) - calculated if it is on age-based mode")


    # Different filing statuses for tax purposes - can auto-populate from profile or be user-specified scenario.
    filing_status: FilingStatus = Field(FilingStatus.single,
        description="Federal tax filing status which can auto-populate from profile if provided")
    state: str = Field("NY",
        description="Two letter state code for tax purposes which can auto-populate from profile if provided")


    # NPV (Net present value) discount rate for comparing the cash flows across different time periods.
    # Utilized to weigh out different scenarios (Ex: "Is buying better than renting?")
    annual_discount_rate: float = Field(0.025, ge = 0.0, le = 0.75,
        description="The annual discount rate for NPV calculations")

    
    # Reporting deflator calculation which controls the conversion from nominal to real dollars.
    # DISPLAY PURPOSES ONLY (NOT USED IN CALCULATIONS)
    reporting_deflator: ReportingDeflator = Field(ReportingDeflator.none,
        description="Deflator mode used to convert nominal to real dollars for the outputs")
    # Deflation used ONLY when reporting_deflator is at a "fixed_rate".
    annual_deflator_rate: float = Field(0.025, ge = -0.3, le = 0.3,
        description="Annual deflation rate when using the fixed_rate mode")
    provider_source_deflator: str | None = Field(None,
        description="Provider source used only when in provider mode")
    

    # model_validator usage...
    # A cross-field validation checker that will handle the calculations and validation of the models.
    # If the models are in age-based mode, it will calculate the dates from the ages, then validate the logic.
    # Will run AFTER the individual field validation ->>>>> (mode="after").
    @model_validator(mode="after")
    # Function which validates and calculates the timeline and will return a GlobalInputs object.
    def validate_and_calculate_timeline(self) -> "GlobalInputs":
        # Used to call date.today() and avoids conflicts with the type annotation "date".
        from datetime import date as dt_date
        # Handles date arithmetic (months/years) precisely as actual dates rather than values.
        from dateutil.relativedelta import relativedelta
        
        # Gets today's date as a baseline for calculations.
        today = dt_date.today()
        # Will calculate the current_age from birth_date if it isn't provided.
        if self.birth_date and self.current_age is None:
            age_change = relativedelta(today, self.birth_date)
            self.current_age = age_change.years + (age_change.months / 12.0)
        
        # AGE-BASED MODE - Calculates the dates from ages.
        if self.timeline_mode == "age":
            # Ensures that we at least have the user's age.
            if not self.birth_date or self.current_age is None:
                raise ValueError("The age-based timeline requires current age or birthdate.")
            
            # Figures out what age to actually START the model at.
            if self.start_age_years is not None and self.start_age_months is not None:
                actual_start_age = self.start_age_years + (self.start_age_months / 12.0)
            elif self.start_age_years is not None:
                actual_start_age = self.start_age_years
            else:
                actual_start_age = self.current_age

            # Figures out what age to END the model at.
            if self.end_age_years is not None and self.end_age_months is not None:
                actual_end_age = self.end_age_years + (self.end_age_months / 12.0)
            elif self.end_age_years is not None:
                actual_end_age = self.end_age_years
            elif self.end_option == "retirement":
                actual_end_age = 67.0
            else:
                actual_end_age = 80.0

            # Ensures that the end age is older than the starting age.
            if actual_start_age >= actual_end_age:
                raise ValueError("Starting age must be less than the ending age")
            
            # Checks to see if the actual start age is less than the current age
            if actual_start_age < self.current_age:
                raise ValueError("The starting age cannot be less than your current age.")
            
            # Finds the number of years until the model starts its predictions.
            years_to_start = actual_start_age - self.current_age
            # Calculates the number of years until the model ends its predictions.
            years_to_end = actual_end_age - self.current_age

            # Converts the starting date into an actual calendar date.
            self.start_date = today + relativedelta(
                years = int(years_to_start), months = int((years_to_start % 1) * 12)
            )
            # Converts the ending date into an actual calendar date.
            self.end_date = today + relativedelta(
                years = int(years_to_end), months = int((years_to_end % 1) * 12)
            )

        
        # DATE-BASED MODE - Validates the originally provided dates.
        # timeline_mode == date
        else:
            if not self.start_date or not self.end_date:
                raise ValueError("Date-based timeline requires both a start_date and end_date")

        # The final validation check to see if the end_date comes after the start_date.
        if self.start_date >= self.end_date:
            raise ValueError("The end_date must be later than the start_date")

        return self
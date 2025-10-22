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
    start_age: float | None = Field(None, 
        description = "Starting age for the simulation where 'None' means to use the current_age")
    end_option: Literal["retirement", "lifespan"] | None = Field("retirement", 
        description="The present endpoint when end_age is not specified ('retirement' = 65.5 and 'lifespan' = 80)")
    end_age: float | None = Field(None, 
        description="Ending age for simulation where 'None' means to use the end_option preset)


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
    


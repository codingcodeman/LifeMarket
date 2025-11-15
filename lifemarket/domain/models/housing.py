"""
File Purpose: Housing input models for rent and mortgage scenarios.
    - Defines the data schemas for housing-related calculations.
    - RentInputs: Configuration for rental scenarios with growth parameters.
    - MortgageInputs: Configuration for home purchase scenarios (future).
    - These models are used by domain/modules/housing.py to perform calculations.
    - Growth rates use the 3-part system (RateSpec) for flexibility.

Reasoning: Separates housing data validation from calculation logic. Allows scenario configs
           to override profile defaults while maintaining type safety.

Use:
    - Import and use in domain/modules/housing.py calculation functions.
    - Scenario configs instantiate these models with user-specific values.
    - Application layer merges profile defaults with scenario overrides.
"""

# Allows for type hints or references to be defined later (forward references).
from __future__ import annotations
# Pydantic version 2.6 - Ensures that validation is fast and keeps schemas clean for 3 part system.
# - BaseModel: core class for typed, validated objects.
# - Field: attach defaults, bounds (ge/le/gt/lt), descriptions.
# - PositiveFloat: convenience type that enforces > 0.
from pydantic import BaseModel, Field, PositiveFloat
# Imports the 3-part rate system and default rate value from base models
from lifemarket.domain.models.base import RateSpec, RateValue

# ..........................................RENTAL HOUSING INPUTS.....................................

# Configuration for rental housing scenarios where the user is renting a place.
# Values can come from UserProfile.housing but can be overridden in scenario configs.
class RentInputs(BaseModel):
    
    # Base rent amount before any adjustments (from profile.housing.housing_payment_monthly by default).
    base_monthly_rent: PositiveFloat = Field(
        ...,  # Required field - must be provided
        description="Monthly rent before roommate contributions or other adjustments"
    )
    
    # Roommate configuration to split rent costs.
    roommates: int = Field(default = 0, ge = 0, le = 10,
        description="Number of roommates sharing the rent (0 means living alone)")
    roommate_contribution_percent: float = Field(default = 0.0, ge = 0.0, le = 1.0,
        description="Percentage of rent paid by roommates (0.5 = they pay 50% of total rent)")
    
    # Renters insurance (from profile.housing.has_renters_insurance).
    renters_insurance_monthly: float = Field(default = 0.0, ge = 0.0,
        description="Monthly renters insurance premium in dollars")
    
    # Utilities if not included in rent.
    utilities_monthly: float = Field(default = 0.0, ge = 0.0,
        description="Monthly utilities cost (electric, gas, water, internet) in dollars")
    
    # Growth rates using the 3-part system - THE KEY PART for per-category inflation.
    # Each expense component can grow at its own rate independent of other categories.
    rent_growth: RateSpec = Field(
        default_factory = lambda: RateValue(annual = 0.05),
        description="How rent increases over time (default 5% annually)"
    )
    insurance_growth: RateSpec = Field(
        default_factory = lambda: RateValue(annual = 0.03),
        description="How renters insurance premium increases over time (default 3% annually)"
    )
    utilities_growth: RateSpec = Field(
        default_factory = lambda: RateValue(annual = 0.025),
        description="How utility costs increase over time (default 2.5% annually)"
    )
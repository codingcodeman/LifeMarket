"""
File Purpose: Defines the user profile identity and preferences utilized by LifeMarket.
    - Exposes the user-tunable defaults in a typed way.
    - Allows the profiles to belong to the domain itself where the adapters can control the persistence (Storage after execution).
    - Keeps the validation here (Pydantic) so bad data is caught before any math is executed.
    - This profile stores SIMPLE METRICS (Ex: do you rent or have a mortgage, what is your monthly payment, 
      are you paying health insurance or are your parents paying).
    - No percentages live here as growth rates are handled elsewhere.
    - This file is only about the shapes of the data (what fields exist + basic rules).

Use:
    - Adapters (Ex: json_store.py) load and save the user profile.
    - Application layer (Ex: config_loader.py) reads a profile and translates it into a particular "rate".

Definitions:
    - Persistence: the ability of data to last beyond the programs execution to be saved and retrieved later.
"""

# Allows for type hints or references to be defined later (forward references).
from __future__ import annotations
# Stores dates as actual calendar dates.
from datetime import date
# Optional - Either utlizes a type object or has it as missing (None).
# Dict - A dictionary that has a box of key-value pairs.
from typing import Optional, Dict
# Controlled string choices and avoids typos. Enables editor autocomplete and better validation.
from enum import Enum 
# Pydantic version 2.6 - Ensures that validation is fast and keeps schemas clean for 3 part system.
# - BaseModel: core class for typed, validated objects.
# - Field: attach defaults, bounds (ge/le/gt/lt), descriptions.
# - model_validator: cross-field validation hook (end_date > start_date).
from pydantic import BaseModel, Field, model_validator
# This reuses the class from the base.py file so there is only one place that lists "single" or "married"
from lifemarket.domain.models.base import FilingStatus

# ...................................................CONSTANTS...........................................................

# Used to increment when breaking changes are made to schemas so downstream code can detect mismatches.
PROFILE_SCHEMA_VERSION: str = "0.1.0"

# .....................................................ENUMS.............................................................

# How the user lives in respect to housing payments.
class HousingKind(str, Enum):
    none = "none"
    rent = "rent"
    mortgage = "mortgage"

# Finds who pays health insurance for the user.
class HealthPayer(str, Enum):
    none = "none"
    self_pay = "self_pay"
    parents = "parents"

# Car payment situation
class CarStatus(str, Enum):
    none = "none"
    paid_off = "paid_off"
    parents_paying = "parents_paying"
    monthly_payment = "monthly_payment"

# ................................................GROUPS OF METRICS......................................................

# CHANGE THE DEFAULTS FOR THESE CLASSES!!!!!!!! **** **** **** *****

# Choice made plus the monthly payment
class HousingMetrics(BaseModel):
    housing_kind: HousingKind = Field(default = HousingKind.rent,
        description="How you pay for housing")
    housing_payment_monthly: Optional[float] = Field(default = None, ge = 0.0,
        description="Your monthly rent or mortgage payment in dollars (leave blank if unknown).")
    has_renters_insurance: Optional[bool] = Field(default = None,
        description="If you are renting, are you also paying for renters insurance?")
    
    @model_validator(mode="after")
    # If you are paying rent or mortgage, the payment must be greater than 0.
    def check_housing_payment(self) -> "HousingMetrics":
        if self.housing_kind in (HousingKind.rent, HousingKind.mortgage):
            if self.housing_payment_monthly is None or self.housing_payment_monthly <= 0:
                raise ValueError("Please enter a monthly rent/mortgage value greater than 0.")
        return self

# Who pays? If the user pays itself, the monthly premium should be a number.
# The monthly premium also must be greater than 0.
class HealthInsuranceMetrics(BaseModel):
    payer: HealthPayer = Field(default = HealthPayer.parents,
        description="Who pays for your health insurance")
    health_premium_monthly: Optional[float] = Field(default = None, ge = 0.0,
        description="How many dollars per month you pay (leave blank if parents/None)")
    
    @model_validator(mode="after")
    # If the user is paying, the monthly payment should be greater than 0.
    def check_health_payment(self) -> "HealthInsuranceMetrics":
        # Checks to see if the payer is self_pay and that the monthly premium is also less than or equal to 0.
        if self.payer == HealthPayer.self_pay:
            if self.health_premium_monthly is None or self.health_premium_monthly <= 0:
                raise ValueError("Please enter a positive value for the monthly premium.")
        return self
    

# The car loan situation (none / paid_off / parents_paying / monthly_payment).
# If the user is doing a monthly payment, they have to enter in the numeric monthly payment.
# Gas information: price per gallon, miles per month, miles per gallon (all optional).
class CarMetrics(BaseModel):
    status: CarStatus = Field(default = CarStatus.parents_paying,
        description="Your car payment status")
    monthly_car_payment: Optional[float] = Field(default = None, ge = 0.0,
        description="If you have a monthly car payment, enter that amount here.")
    # Optional metrics
    avg_price_per_gallon: Optional[float] = Field(default = None, ge = 0.0,
        description="Average price per gallon. Leave empty to use app default later.")
    miles_per_month: Optional[float] = Field(default = None, ge = 0.0,
        description="Approximate number of miles you drive each month.")
    miles_per_gallon: Optional[float] = Field(default = None, ge = 1.0,
        description="Your car's miles per gallon (must be >= 1 if set).")
    
    @model_validator(mode="after")
    def check_car_payment(self) -> "CarMetrics":
        if self.status == CarStatus.monthly_payment:
            if self.monthly_car_payment is None or self.monthly_car_payment <= 0:
                raise ValueError("Please enter a positive value for the monthly car payment")
        return self
    
# Creates the everyday spending buckets if they would like to enter in their own values or not.
# When a user does not use a bucket, it is left as 0
class CoreExpenses(BaseModel):
    groceries_monthly: float = Field(default = 0.0, ge = 0.0,
        description="Monthly grocery bill")

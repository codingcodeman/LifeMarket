"""
File Purpose: Unit tests for housing input models.
    - Tests validation logic for RentInputs model.
    - Ensures field constraints work correctly (positive values, ranges).
    - Verifies default values are set properly.
    - Tests edge cases and error conditions.

Reasoning: Catch validation errors before they reach calculation modules. Ensures data
           integrity at the schema level.

Use:
    - Run with: pytest tests/unit/test_housing_models.py -v
    - Part of unit test suite (no I/O, fast execution).
"""

import pytest
from domain.models import RentInputs


# ..........................................BASIC INSTANTIATION TESTS.....................................

def test_rent_inputs_basic():
    """Test creating RentInputs with minimal required fields."""
    r = RentInputs(base_monthly_rent = 2000.0)
    
    # Check required field
    assert r.base_monthly_rent == 2000.0
    
    # Check defaults
    assert r.roommates == 0
    assert r.roommate_contribution_percent == 0.0
    assert r.renters_insurance_monthly == 0.0
    assert r.utilities_monthly == 0.0


def test_rent_inputs_with_all_fields():
    """Test creating RentInputs with all fields specified."""
    r = RentInputs(
        base_monthly_rent = 2500.0,
        roommates = 2,
        roommate_contribution_percent = 0.5,
        renters_insurance_monthly = 25.0,
        utilities_monthly = 150.0
    )
    
    assert r.base_monthly_rent == 2500.0
    assert r.roommates == 2
    assert r.roommate_contribution_percent == 0.5
    assert r.renters_insurance_monthly == 25.0
    assert r.utilities_monthly == 150.0


# ..........................................VALIDATION TESTS.....................................

def test_rent_inputs_negative_rent_fails():
    """Test that negative rent raises validation error."""
    with pytest.raises(ValueError):
        RentInputs(base_monthly_rent = -1000.0)


def test_rent_inputs_zero_rent_fails():
    """Test that zero rent raises validation error (must be positive)."""
    with pytest.raises(ValueError):
        RentInputs(base_monthly_rent = 0.0)


def test_rent_inputs_roommate_percent_out_of_range():
    """Test that roommate contribution percent must be between 0 and 1."""
    # Test percent > 1 fails
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            roommate_contribution_percent = 1.5
        )
    
    # Test negative percent fails
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            roommate_contribution_percent = -0.1
        )


def test_rent_inputs_negative_roommates_fails():
    """Test that negative number of roommates fails validation."""
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            roommates = -1
        )


def test_rent_inputs_too_many_roommates_fails():
    """Test that more than 10 roommates fails validation."""
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            roommates = 11
        )


def test_rent_inputs_negative_insurance_fails():
    """Test that negative insurance premium fails validation."""
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            renters_insurance_monthly = -10.0
        )


def test_rent_inputs_negative_utilities_fails():
    """Test that negative utilities cost fails validation."""
    with pytest.raises(ValueError):
        RentInputs(
            base_monthly_rent = 2000.0,
            utilities_monthly = -50.0
        )


# ..........................................ROOMMATE CONFIGURATION TESTS.....................................

def test_rent_inputs_with_roommates():
    """Test RentInputs with roommate configuration."""
    r = RentInputs(
        base_monthly_rent = 3000.0,
        roommates = 2,
        roommate_contribution_percent = 0.5
    )
    
    assert r.roommates == 2
    assert r.roommate_contribution_percent == 0.5


def test_rent_inputs_roommates_pay_full_rent():
    """Test edge case where roommates pay 100% of rent."""
    r = RentInputs(
        base_monthly_rent = 2000.0,
        roommate_contribution_percent = 1.0
    )
    
    assert r.roommate_contribution_percent == 1.0


def test_rent_inputs_no_roommate_contribution():
    """Test that 0% roommate contribution is valid."""
    r = RentInputs(
        base_monthly_rent = 2000.0,
        roommates = 2,
        roommate_contribution_percent = 0.0
    )
    
    assert r.roommate_contribution_percent == 0.0


# ..........................................GROWTH RATE TESTS.....................................

def test_rent_inputs_default_growth_rates():
    """Test that default growth rates are set correctly."""
    r = RentInputs(base_monthly_rent = 2000.0)
    
    # Default rent growth should be 5% annually
    assert r.rent_growth.kind == "value"
    assert r.rent_growth.annual == 0.05
    
    # Default insurance growth should be 3% annually
    assert r.insurance_growth.kind == "value"
    assert r.insurance_growth.annual == 0.03
    
    # Default utilities growth should be 2.5% annually
    assert r.utilities_growth.kind == "value"
    assert r.utilities_growth.annual == 0.025


def test_rent_inputs_custom_growth_rate():
    """Test that custom growth rates can be specified."""
    from lifemarket.domain.models import RateValue
    r = RentInputs(
        base_monthly_rent = 2000.0,
        rent_growth = RateValue(kind='value', annual=0.07)
    )
    assert r.rent_growth.kind == "value"
    assert r.rent_growth.annual == 0.07
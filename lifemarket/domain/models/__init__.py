"""
Central import point for all LifeMarket data models.

Purpose:
    - Provides single import location for all models across the application
    - Prevents circular import issues by centralizing exports
    - Allows clean imports: `from domain.models import GlobalInputs, RentInputs`
    - Maintains explicit __all__ list for IDE autocomplete and documentation

Usage:
    # In any file needing models:
    from lifemarket.domain.models import GlobalInputs, RentInputs
    
    # Instead of:
    from lifemarket.domain.models.base import GlobalInputs
    from lifemarket.domain.models.housing import RentInputs

Architecture:
    - This file lives in domain/models/__init__.py
    - It re-exports from submodules (base.py, housing.py, transport.py, etc.)
    - Submodules should NOT import from each other (to avoid circular deps)
    - Submodules can import from base.py (since base has no dependencies)
"""

# ================================ PHASE 1: FOUNDATION ================================
# Core models that everything else depends on

from domain.models.base import (
    # Version
    SCHEMA_VERSION,
    
    # Enums
    FilingStatus,
    ReportingDeflator,
    
    # 3-Part Rate System
    RateValue,
    RateSchedule,
    RateProvider,
    RateSpec,
    
    # Global Configuration
    GlobalInputs,
)

# ================================ PHASE 2: MODULE INPUT MODELS ================================
# Housing module inputs
from lifemarket.domain.models.housing import (
    RentInputs,
)

# ================================ EXPORTS ================================
# Explicit __all__ list for clean imports and IDE support

__all__ = [
    # ===== Phase 1: Foundation =====
    "SCHEMA_VERSION",
    "FilingStatus",
    "ReportingDeflator",
    "RateValue",
    "RateSchedule",
    "RateProvider",
    "RateSpec",
    "GlobalInputs",
    
    # ===== Phase 2: Module Inputs =====
    # --- Housing ---
    "RentInputs",
]
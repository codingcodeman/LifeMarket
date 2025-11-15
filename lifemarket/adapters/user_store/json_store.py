"""
json_store.py
-------------
This file is the "real worker" that saves and loads user profiles using JSON files.

Think of it like a librarian:
- It knows where the (folder) lives.
- It knows how to put (files) on the shelf safely.
- It knows how to take (files) off the shelf and check they're not wrong or damaged.

Main ideas for safety:
- We write to a TEMP file first, then swap it in one quick move (atomic replace).
  That way, if the power goes out, we don't leave a half-written file behind.
- We "validate" the profile shape with Pydantic (strict) so bad data gets caught early.
- We "sanitize" the user_id, so people can't sneak weird characters into file names.
"""

# --------IMPORTS---------

from __future__ import annotations
# This tells Python: "Don't panic about type hints right now. You can figure them
# out later." It helps avoid import loops and keeps big projects calm.

import json
# json helps us turn Python data into text format (JSON) that we can save in a file
# and turn it back into python later.

import os
# os gives us tools to communicate to the operating system:
# - replace files safely
# - check if files exist
# - sync writes to disk

import tempfile
# tempfile makes safe, unique temp. files for us to write to first
# We use this to avoid half-written files if something goes wrong mid-write

from pathlib import Path 
# Path is a friendly way to work with file system paths (folders/files).
# Its easier to read than using than using raw strings everywhere

from typing import Optional, Iterable
# Optional[T] means "either T or None" (maybe there is a profile, maybe not).
# Iterable[str] means "something we can loop over to get strings" (like user IDs).

from lifemarket.domain.user_profile import UserProfile
# This is the official shape of a user's profile (Pydantic model).
# We use it to make sure the data we load really matches our rules.

from .errors import (ProfileNotFound, ProfileCorrupt, ProfileWriteFailed,)


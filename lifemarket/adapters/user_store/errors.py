"""
errors.py
---------
This file gives names to common problems that can happen when we save or load
a user's profile. Having clear names makes it easier to catch and handle them.


"""

# We use simple custom exceptions (these are just special kinds of errors).
# Why custom ones? Because "JSONDecodeError" or "OSError" are too generic.
# Our own names tell the app exactly what type of trouble happened.

class ProfileStoreError(Exception):
    # Big umbrella error for all the profile store problems
    pass

class ProfileCorrupt(ProfileStoreError):
    # this error is for if we found a file but there is missing stuff inside
    # broken or not in the right shape
    # (for example) feilds are missing or have the wrong type
    pass

class ProfileWriteFailed(ProfileStoreError):
    # lets say we tried to write a profile to disk, but something went wrong
    # EX: we ran out of space or lost permission
    pass



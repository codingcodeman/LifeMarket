"""
Profile Store Contract (Protocol)
---------------------------------
This file defines the *rules* for any profile storage system.

Why this exists:
- The application should NOT care if profiles live in JSON, Postgres, Supabase, etc.
- We define a small interface (load/save) that any storage must follow.
- Later, we can write *multiple* stores (json_store.py, pg_store.py) that all obey this contract.

How others will use it:
- The app imports `ProfileStore` as a *type* and calls `load_profile(...)` / `save_profile(...)`.
- Tests can create fake stores that also match this shape.

-----------

It doesnt save or load anything itself.

It only describes the shape of a thing that can save or load profiles.

Later well build a JSON class that follows these rules.


"""

from __future__ import annotations
# ^ This lets type hints refer to things that might be defined later or lazily,
#   and keeps Python from needing to import everything immediately. It's safe,
#   lightweight, and avoids circular import headaches in larger projects.


from typing import Protocol, Optional, Iterable, runtime_checkable
# - Protocol: lets us define a "shape" (set of methods) that a class must have.
#             Any class with these methods "fits" the Protocol (duck typing).
# - Optional[T]: means "either a T or None". We use this for load_profile,
#                because sometimes a profile might not exist yet.
# - Iterable[str]: means "something we can loop over to get strings (user ids)".
#                  Useful for tooling (list all profiles).
# - runtime_checkable: a decorator so we can check at runtime with isinstance(obj, ProfileStore)
#                      during debugging/tests. Without it, Protocols are mostly
#                      for static type checkers only.

from lifemarket.domain.user_profile import UserProfile
# - UserProfile is the validated data model (Pydantic) for a user's saved info.
#   We import the *type* here so the rest of the app knows exactly what shape
#   load_profile returns and save_profile accepts.
#   NOTE: This is okay because adapters can depend on domain models,
#   but domain models must NOT depend on adapters (one-way arrows).
#   That keeps the domain "pure" and reusable.


@runtime_checkable
class ProfileStore(Protocol):
    """
    The small set of actions the app expects any profile storage to support.

    IMPORTANT:
    - This class does NOT implement the methods (no actual I/O here).
    - It only defines the method *signatures* (names + parameters + return types).
    - Any class with these methods is considered a ProfileStore (duck typing).
    """

    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Read and return the saved profile for this user, or None if it doesn't exist.

        Params:
        - user_id: a short string that identifies the user.
                   (The JSON implementation will sanitize it for filenames.)

        Returns:
        - UserProfile if found, otherwise None.

        Errors:
        - Implementations should raise a clear, custom exception for *corrupt*
          data (e.g., ProfileCorrupt) so the app can tell "missing" vs "broken".
        """

    def save_profile(self, user_id: str, profile: UserProfile) -> None:
        """
        This will create/overwrite the profile for this user

        Contract:
        - Should be *atomic* (meaning that if there is some interuption then the file will not be saved, only complete files saved)
        - Should only write out valid data (data that is approved)
        - On failure, thie will print custom errors that can show what went wrong and needs to be done

        Returns
        - on success it will return nothing to show that it ran successfully 
        """
    
    # --------The Following Are For Admin Use Only ----------------

    def delete_profile(self, user_id: str) -> None:
        """
        Remove the users profile from storage.
        - If it doesnt exist, it will raise a "profile not found"
        """

    def list_user_ids(self) -> Iterable[str]:
        """
        return all of the know user IDs in this store
        """

    def exist(self, user_id: str) -> bool:
        """
        Quick check to see if a profile exist
        """ 
 
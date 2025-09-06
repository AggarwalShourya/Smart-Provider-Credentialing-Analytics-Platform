import pandas as pd
from typing import Tuple

def validate_licenses(roster: pd.DataFrame, ny: pd.DataFrame, ca: pd.DataFrame) -> pd.DataFrame:
    """
    Validates roster licenses against NY/CA databases.
    - Flags:
      license_found, license_expired, license_state_mismatch
    """
    df = roster.copy()
    # Normalize key join column early
    if "license_number" in df.columns:
        df["license_number"] = df["license_number"].astype(str).str.strip()
    # Consolidate state DBs
    ny_src = ny.copy(); ny_src["validation_state"] = "NY"
    ca_src = ca.copy(); ca_src["validation_state"] = "CA"

    # Ensure join key is normalized for state sources as well
    for s in (ny_src, ca_src):
        if "license_number" in s.columns:
            s["license_number"] = s["license_number"].astype(str).str.strip()

    # Normalize expected columns in state DBs
    for s in (ny_src, ca_src):
        if "license_expiration_date" not in s.columns:
            # fallbacks commonly seen in state data
            for c in ["expiration_date", "exp_date", "license_exp"]:
                if c in s.columns:
                    s["license_expiration_date"] = pd.to_datetime(s[c], errors="coerce", utc=True).dt.date
                    break

    state_db = pd.concat([ny_src, ca_src], ignore_index=True)

    # Avoid 1-to-many expansion on merge: keep most recent expiration per license
    if "license_expiration_date" in state_db.columns:
        state_db = state_db.sort_values("license_expiration_date", ascending=False)
    if "license_number" in state_db.columns:
        state_db = state_db.drop_duplicates(subset=["license_number"], keep="first")

    # Join by license_number where available
    # Preserve both roster and state expiration dates distinctly
    left_df = df.copy()
    had_roster_exp = False
    if "license_expiration_date" in left_df.columns:
        left_df = left_df.rename(columns={"license_expiration_date": "license_expiration_date_roster"})
        had_roster_exp = True

    state_sel = state_db[["license_number", "validation_state", "license_expiration_date"]].rename(
        columns={"license_expiration_date": "license_expiration_date_state"}
    )

    joined = left_df.merge(
        state_sel,
        on="license_number", how="left"
    )

    # Heuristic state match
    if "license_state" in joined.columns:
        joined["license_state_mismatch"] = (
            (joined["validation_state"].notna()) &
            (joined["license_state"].notna()) &
            (joined["validation_state"] != joined["license_state"])
        )
    else:
        joined["license_state_mismatch"] = False

    # Found flag
    joined["license_found"] = joined["validation_state"].notna()

    # Expired flag: prefer state expiration if present, else roster field
    date_state = joined.get("license_expiration_date_state")
    date_roster = joined.get("license_expiration_date_roster") if had_roster_exp else None
    today = pd.Timestamp("today").date()
    # Build the best available expiration series aligned with joined
    if date_state is not None and date_roster is not None:
        best_exp = date_state.fillna(date_roster)
    elif date_state is not None:
        best_exp = date_state
    else:
        best_exp = date_roster if date_roster is not None else pd.Series([pd.NaT] * len(joined), index=joined.index)
    joined["license_expired"] = best_exp.apply(lambda d: bool(d and d < today))

    return joined

def validate_npi(roster: pd.DataFrame, npi: pd.DataFrame) -> pd.DataFrame:
    """
    Validates NPI presence and linkage by direct join.
    Flags: npi_missing, npi_found
    """
    df = roster.copy()
    result = df.merge(npi[["npi"]].drop_duplicates(), on="npi", how="left", indicator=True)
    result["npi_missing"] = result["npi"].isna()
    result["npi_found"] = (result["_merge"] == "both")
    result = result.drop(columns=["_merge"])
    return result
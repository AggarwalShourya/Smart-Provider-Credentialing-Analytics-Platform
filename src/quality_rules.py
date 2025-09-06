import pandas as pd

def rule_phone_format(df: pd.DataFrame) -> pd.Series:
    # Valid if phone_clean is not null; otherwise flagged
    return df["phone_clean"].isna()

def rule_missing_npi(df: pd.DataFrame) -> pd.Series:
    return df["npi"].isna()

def rule_specialty_missing(df: pd.DataFrame) -> pd.Series:
    return ~df["specialty"].astype(str).str.strip().astype(bool)

def rule_multi_state_single_license(df: pd.DataFrame) -> pd.Series:
    """
    Flag providers appearing in multiple address_state values but having only one license_number.
    Group by provider (NPI preferred, fall back to full_name).
    """
    gkey = df["npi"].fillna(df["full_name_clean"])
    states_per = df.groupby(gkey)["address_state"].nunique()
    lic_per = df.groupby(gkey)["license_number"].nunique()
    flags = (states_per > 1) & (lic_per <= 1)
    return gkey.map(flags).fillna(False)

def summarize_by_state(issues_df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = issues_df.select_dtypes(include="bool").columns.tolist()
    grp = issues_df.groupby("address_state")[numeric_cols].sum().reset_index()
    grp["total_records"] = issues_df.groupby("address_state").size().values
    return grp
import pandas as pd
import logging

log = logging.getLogger(__name__)

def clean_ohlcv(df, source_name="DataCleaner"):
    """
    Ensures OHLCV structure is valid:
    - Flattens MultiIndex columns
    - Converts all columns to lowercase
    - Ensures datetime column exists
    - Fills missing OHLC columns with NaN/dummy values
    - Ensures volume is usable (replaces with dummy values if bad)
    """
    if df is None or df.empty:
        log.warning(f"[{source_name}] Empty DataFrame passed to cleaner.")
        return pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

    # Flatten MultiIndex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip().lower() for col in df.columns.values]
    else:
        df.columns = [c.lower() for c in df.columns]

    # Ensure datetime column
    if "datetime" not in df.columns:
        if "date" in df.columns:
            df.rename(columns={"date": "datetime"}, inplace=True)
        else:
            log.warning(f"[{source_name}] No datetime column found. Creating placeholder.")
            df["datetime"] = pd.NaT

    # Required OHLCV columns
    required_cols = ["open", "high", "low", "close", "volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        log.warning(f"[{source_name}] Missing OHLC columns: {missing_cols}. Filling with NaN/dummy values.")
        for col in missing_cols:
            if col == "volume":
                df[col] = 1
            else:
                df[col] = float("nan")

    # Safe volume check
    vol_series = df["volume"]
    no_volume_column = "volume" not in df.columns
    volume_all_na = bool(vol_series.isna().all())
    volume_all_zero = bool((vol_series == 0).all())

    if no_volume_column or volume_all_na or volume_all_zero:
        log.warning(f"[{source_name}] No valid volume data. Using dummy values.")
        df["volume"] = 1

    # Ensure correct column order
    df = df[["datetime", "open", "high", "low", "close", "volume"]]
    df = df.sort_values("datetime").reset_index(drop=True)

    return df


def sort_by_datetime_safe(df, datetime_col="datetime"):
    """
    Sort DataFrame by datetime column safely:
    - Drops NA datetime rows before sorting to avoid Pandas FutureWarning.
    - Works for both Timestamp and NaT values.
    """
    if datetime_col not in df.columns:
        log.warning(f"[DataCleaner] No '{datetime_col}' column found. Skipping sort.")
        return df

    clean_df = df.dropna(subset=[datetime_col])
    return clean_df.sort_values(by=datetime_col).reset_index(drop=True)

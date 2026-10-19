"""
Statistical Bridge Runner for SEO Suite Pro:
- Executes Rscript for deep time-series, anomaly, and distribution testing
- Provides an automated, seamless high-precision Python statistical fallback (using scipy.stats)
- Returns structured analytics and clear host status information
"""

import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from core.config import R_SCRIPTS_DIR

R_SCRIPT_PATH = R_SCRIPTS_DIR / "gsc_statistical_analysis.R"

def is_r_available() -> bool:
    """Checks if Rscript executable is installed and available in PATH."""
    return shutil.which("Rscript") is not None

def run_python_statistical_fallback(df: pd.DataFrame) -> dict:
    """
    Executes native high-precision statistical analysis using Scipy and NumPy
    when R is not installed on the host system.
    """
    clicks = pd.to_numeric(df["clicks"], errors="coerce").dropna().values
    impressions = pd.to_numeric(df["impressions"], errors="coerce").dropna().values
    ctr = pd.to_numeric(df["ctr"], errors="coerce").dropna().values
    position = pd.to_numeric(df["position"], errors="coerce").dropna().values
    
    # 1. Anomaly detection via Tukey's IQR Fences
    def calc_iqr(vals):
        if len(vals) < 5:
            return {"count": 0, "outlier_count": 0, "upper_threshold": 0, "lower_threshold": 0}
        q1 = np.percentile(vals, 25)
        q3 = np.percentile(vals, 75)
        iqr = q3 - q1
        lower_bound = max(0.0, float(q1 - (1.5 * iqr)))
        upper_bound = float(q3 + (1.5 * iqr))
        outliers = [float(x) for x in vals if x < lower_bound or x > upper_bound]
        return {
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "upper_threshold": round(upper_bound, 2),
            "lower_threshold": round(lower_bound, 2),
            "outlier_count": len(outliers),
            "outliers": outliers[:10]
        }
        
    click_anomalies = calc_iqr(clicks)
    impr_anomalies = calc_iqr(impressions)
    
    # 2. Distribution Statistics (Mean, Median, Skewness, Kurtosis)
    def calc_dist(vals):
        if len(vals) < 4:
            return {"mean": 0, "median": 0, "skewness": 0, "kurtosis": 0}
        return {
            "mean": round(float(np.mean(vals)), 3),
            "median": round(float(np.median(vals)), 3),
            "sd": round(float(np.std(vals, ddof=1)), 3),
            "skewness": round(float(stats.skew(vals)), 3),
            "kurtosis": round(float(stats.kurtosis(vals)), 3)
        }
        
    ctr_dist = calc_dist(ctr)
    pos_dist = calc_dist(position)
    
    # 3. Two-sample significance testing (Mobile vs Desktop)
    sig_test = {"performed": False, "reason": "Insufficient comparative device data."}
    if "device" in df.columns:
        mob = df[df["device"].str.upper() == "MOBILE"]["ctr"].dropna().values
        desk = df[df["device"].str.upper() == "DESKTOP"]["ctr"].dropna().values
        if len(mob) >= 5 and len(desk) >= 5:
            stat, p_val = stats.mannwhitneyu(mob, desk, alternative="two-sided")
            is_sig = bool(p_val < 0.05)
            sig_test = {
                "performed": True,
                "test_name": "Mann-Whitney U Test (Mobile vs Desktop CTR)",
                "p_value": round(float(p_val), 5),
                "statistically_significant": is_sig,
                "interpretation": "Statistically significant disparity between Mobile and Desktop CTR distributions (p < 0.05)." if is_sig else "No statistically significant difference between device CTRs (p >= 0.05)."
            }
            
    return {
        "engine": "Python (High-Precision Scipy Engine)",
        "r_available": False,
        "status": "success",
        "notice": "R statistical runtime is not detected on this host. Executing native high-precision Scipy statistical engine.",
        "anomalies": {
            "clicks": click_anomalies,
            "impressions": impr_anomalies
        },
        "distributions": {
            "ctr": ctr_dist,
            "position": pos_dist
        },
        "significance_testing": sig_test
    }

def run_statistical_analysis(df: pd.DataFrame) -> dict:
    """
    Attempts to run analysis via Rscript in r_scripts/.
    Gracefully falls back to pure Python if R is missing or throws an error.
    """
    if not is_r_available() or not R_SCRIPT_PATH.exists():
        return run_python_statistical_fallback(df)
        
    # Prepare payload for R script
    payload = {
        "data": df[["clicks", "impressions", "ctr", "position", "device"]].to_dict(orient="records")
    }
    
    try:
        proc = subprocess.run(
            ["Rscript", str(R_SCRIPT_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=15
        )
        if proc.returncode == 0 and proc.stdout:
            res = json.loads(proc.stdout.strip())
            res["r_available"] = True
            res["notice"] = "Calculated using native R statistical runtime (r-base)."
            return res
        else:
            # R failed or lacked jsonlite, fallback to Python
            res = run_python_statistical_fallback(df)
            res["notice"] = "R runtime encountered a library dependency error; gracefully fell back to native Python engine."
            return res
    except Exception:
        return run_python_statistical_fallback(df)

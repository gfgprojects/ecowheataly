import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import skew


def simplified_medcouple(series):
    """
    Stima semplificata della skewness basata sui quartili.
    Valori positivi indicano coda lunga a destra, negativi coda lunga a sinistra.
    """
    series = series.dropna()
    q1 = series.quantile(0.25)
    q2 = series.median()
    q3 = series.quantile(0.75)

    num = (q3 - q2) - (q2 - q1)
    denom = q3 - q1 if (q3 - q1) != 0 else 1e-9  # Evita divisione per 0

    return num / denom



def adjusted_boxplot_outliers_skew_asymmetric(series, k_lower=1.5, k_upper=1.5, max_skew=1.5):
    """
    Identifica outlier in una serie numerica utilizzando un boxplot adattato
    in base a una stima robusta dell'asimmetria (simplified medcouple).

    Parametri:
    - k_lower, k_upper: moltiplicatori IQR per limiti inferiori/superiori
    - max_skew: limite massimo per la skewness (per evitare cutoff estremi)
    """
    series = series.dropna()
    if series.empty:
        return pd.Series([False] * len(series), index=series.index)

    q1 = np.percentile(series, 25)
    q3 = np.percentile(series, 75)
    iqr = q3 - q1 if (q3 - q1) != 0 else 1e-9

    mc = simplified_medcouple(series)
    mc = np.clip(mc, -max_skew, max_skew)  # contenere l'effetto dello skew

    if mc >= 0:
        lower_fence = q1 - k_lower * np.exp(-4 * mc) * iqr
        upper_fence = q3 + k_upper * np.exp(3 * mc) * iqr
    else:
        lower_fence = q1 - k_lower * np.exp(-3 * mc) * iqr
        upper_fence = q3 + k_upper * np.exp(4 * mc) * iqr

    return (series < lower_fence) | (series > upper_fence)


def remove_outliers_adjusted_boxplot(df, columns):
    """
    Rimuove righe dal DataFrame `df` che contengono outlier in almeno
    una delle colonne specificate (basato su boxplot aggiustato).
    """
    outlier_mask = pd.Series(False, index=df.index)

    for col in columns:
        if df[col].dropna().empty:
            continue  # Salta colonne completamente vuote

        col_outliers = adjusted_boxplot_outliers_skew_asymmetric(df[col])
        outlier_mask |= col_outliers.reindex(df.index, fill_value=False)

    return df.loc[~outlier_mask].copy()

def clean_and_plot(df, columns, plot=False, title_prefix=""):
    """
    Pulisce un DataFrame da outlier e opzionalmente mostra boxplot prima/dopo con conteggio osservazioni.
    """
    cleaned_df = remove_outliers_adjusted_boxplot(df, columns)

    if plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.boxplot(df[columns].dropna().values, labels=columns)
        plt.title(f"{title_prefix} - Before (n={df.shape[0]})")

        plt.subplot(1, 2, 2)
        plt.boxplot(cleaned_df[columns].dropna().values, labels=columns)
        plt.title(f"{title_prefix} - After (n={cleaned_df.shape[0]})")

        plt.tight_layout()
        plt.show()

    return cleaned_df
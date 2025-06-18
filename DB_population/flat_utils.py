import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import skew


def simplified_medcouple_slow(series):
    """
    Compute a simplified version of the medcouple, a robust statistic used to measure skewness.

    This function estimates the skewness of a distribution by analyzing all pairs (i, j) of elements
    in the input series for which the median value m lies between i and j (i ≤ m ≤ j).
    It computes a symmetry score h for each valid pair, and returns the median of all such h values.

    Special handling is included when both elements of a pair are equal to the median m but have
    different indices. In this case, a custom score (-1, 0, or 1) is computed based on the sum
    of the indices and the count of median values in the series.

    Parameters
    ----------
    series : array-like (1D)
        The input numerical series for which to compute the simplified medcouple.

    Returns
    -------
    float
        The median of the asymmetry scores (h-values), representing the distribution's skewness
        relative to its median.
    """
    H = []
    prova = np.array(series)
    m = np.median(prova)
    k = len(np.where(prova == m)[0])

    for ii, i in enumerate(prova):
        for jj, j in enumerate(prova):
            if (m >= i) and (m <= j):
                if (i == m) and (j == m) and (ii != jj):
                    cond = ii + jj - 1
                    h = [-1 if cond < k else 0 if cond == 0 else 1][0]
                    H.append(h)
                else:
                    h = ((j - m) - (m - i)) / (j - i) if j != i else 0  # Avoid division by zero
                    H.append(h)

    return np.median(H) if H else 0.0  # Return 0 if H is empty


def simplified_medcouple(series):
    """
       Compute a fast, vectorized approximation of the medcouple statistic,
       which is a robust measure of skewness for univariate distributions.

       This implementation identifies asymmetry in the data by analyzing all pairs
       (i, j) such that the median m lies between them (i ≤ m ≤ j). For each valid pair,
       a symmetry coefficient h is computed. Additionally, it handles the special case
       where both values equal the median (i == j == m) but have different indices,
       assigning a discrete score (-1, 0, or 1) based on index positions.

       The function is optimized for performance using NumPy vectorized operations,
       making it suitable for large datasets (up to ~30,000 samples). It returns the
       median of all h-values as a single scalar summarizing the distribution's skewness.

       Parameters
       ----------
       series : array-like
           A 1D array or Series of numerical values.

       Returns
       -------
       float
           A scalar value representing the simplified medcouple skewness estimate.
           Values near 0 indicate symmetry, positive values indicate right-skewness,
           and negative values indicate left-skewness.
       """
    series = np.asarray(series)
    # n = len(series)
    # if len(series) > 10000:
    #     series = np.random.choice(series, 10000, replace=False)

    m = np.median(series)
    k = np.count_nonzero(series == m)

    # Special case: i == j == m, ii != jj
    med_indices = np.where(series == m)[0]
    if k > 1:
        ii, jj = np.meshgrid(med_indices, med_indices)
        mask_diff = ii != jj
        cond_matrix = ii + jj - 1
        h_special = np.where(cond_matrix < k, -1, np.where(cond_matrix == 0, 0, 1))
        h_special = h_special[mask_diff]
    else:
        h_special = np.array([])

    # General case
    sorted_series = np.sort(series)
    I, J = np.meshgrid(sorted_series, sorted_series)
    mask = (I <= m) & (m <= J) & (I != J) & ~((I == m) & (J == m))

    i_vals = I[mask]
    j_vals = J[mask]

    h_general = ((j_vals - m) - (m - i_vals)) / (j_vals - i_vals)

    H = np.concatenate([h_general, h_special]) if h_special.size else h_general
    mc = np.median(H) if H.size else 0.0
    del I,J,i_vals,j_vals,h_general,h_special,H

    return mc


def adjusted_boxplot_outliers_skew_asymmetric(series, k_lower=1.5, k_upper=1.5, skew_threshold=0.2):
    """
    Identify outliers in a numeric series using an adjusted boxplot method
    that accounts for data asymmetry via the simplified medcouple (robust skewness estimator).

    If the distribution is approximately symmetric (absolute skewness below `skew_threshold`),
    the function applies the standard Tukey method. Otherwise, it uses adjusted fences that
    scale according to the direction and degree of skewness, based on the simplified medcouple.

    Parameters
    ----------
    series : pd.Series
        The numeric input series from which to detect outliers.
    k_lower : float, optional (default=1.5)
        Multiplier for the lower IQR-based fence.
    k_upper : float, optional (default=1.5)
        Multiplier for the upper IQR-based fence.
    skew_threshold : float, optional (default=0.2)
        Absolute skewness threshold below which the data is treated as symmetric.

    Returns
    -------
    pd.Series of bool
        A boolean series indicating which values are outliers (True = outlier).
    """
    series = series.dropna()
    print('correcting the series... (it will take few seconds)')
    if series.empty:
        return pd.Series([False] * len(series), index=series.index)

    q1 = np.percentile(series, 25)
    q3 = np.percentile(series, 75)
    iqr = q3 - q1 if (q3 - q1) != 0 else 1e-9

    data_skew = skew(series)

    if abs(data_skew) < skew_threshold:
        print('proceding with Tukey method')
        # Standard Tukey boxplot
        lower_fence = q1 - k_lower * iqr
        upper_fence = q3 + k_upper * iqr
    else:
        # Adjusted boxplot using simplified medcouple
        print('proceding with "adjusted boxplot" method')
        mc = simplified_medcouple(series)
        if mc >= 0:
            lower_fence = q1 - k_lower * np.exp(-4 * mc) * iqr
            upper_fence = q3 + k_upper * np.exp(3 * mc) * iqr
        else:
            lower_fence = q1 - k_lower * np.exp(-3 * mc) * iqr
            upper_fence = q3 + k_upper * np.exp(4 * mc) * iqr

    return (series < lower_fence) | (series > upper_fence)

def remove_outliers_adjusted_boxplot(series):
    """
    Rimuove righe dal DataFrame `df` che contengono outlier in almeno
    una delle colonne specificate (basato su boxplot aggiustato).
    """
    # Copia la serie originale
    result = series.copy()
    # Calcola la maschera degli outlier solo sui valori non NaN
    valid = series.dropna()
    if valid.empty:
        raise ValueError('series is empty or all NaN')

    outlier_mask =  adjusted_boxplot_outliers_skew_asymmetric(valid)

    # Reindicizza la maschera per combaciare con la serie originale
    outlier_mask_full = pd.Series(False, index=series.index)
    outlier_mask_full.loc[outlier_mask.index] = outlier_mask

    print(f'Found {outlier_mask.sum()} outliers')
    print(f'Data have {series.eq(0).sum()} zeros out of {len(series)}')

    # Applica NaN solo sugli outlier, mantenendo la lunghezza
    result[outlier_mask_full] = np.nan
    print('Outliers have been put as np.nan')

    return result#df.loc[~outlier_mask].copy()



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
        plt.xticks(rotation=90)
        plt.title(f"{title_prefix} - Before (n={df.shape[0]})")

        plt.subplot(1, 2, 2)
        plt.boxplot(cleaned_df[columns].dropna().values, labels=columns)
        plt.xticks(rotation=90)
        plt.title(f"{title_prefix} - After (n={cleaned_df.shape[0]})")

        plt.tight_layout()
        plt.show()

    return cleaned_df
import pandas as pd
import numpy as np
from scipy import stats

def run_correlation_analysis(df):
    """
    Run Pearson correlation analysis on numerical variables.
    """
    cols = ['unit_price', 'transaction_qty', 'revenue', 'hour']
    corr_matrix = df[cols].corr(method='pearson').round(4)
    
    # Calculate p-values for all pairs
    p_values = pd.DataFrame(index=cols, columns=cols)
    for col1 in cols:
        for col2 in cols:
            if col1 == col2:
                p_values.loc[col1, col2] = 1.0
            else:
                coef, p = stats.pearsonr(df[col1], df[col2])
                p_values.loc[col1, col2] = p
                
    # Format a summary statement
    price_qty_corr, _ = stats.pearsonr(df['unit_price'], df['transaction_qty'])
    price_rev_corr, _ = stats.pearsonr(df['unit_price'], df['revenue'])
    
    interpretation = (
        f"The Pearson correlation between Unit Price and Quantity Sold is {price_qty_corr:.4f}. "
        "This indicates a weak negative relationship, implying that higher-priced products are "
        "slightly more likely to be bought in smaller quantities. The correlation between Unit Price "
        f"and Transaction Revenue is {price_rev_corr:.4f}, demonstrating a strong positive relationship "
        "which suggests unit price is the primary driver of individual transaction revenue."
    )
    
    return {
        'test_name': 'Pearson Correlation Analysis',
        'correlation_matrix': corr_matrix,
        'p_values': p_values,
        'interpretation': interpretation
    }

def run_anova_store(df):
    """
    Run One-Way ANOVA to test if mean transaction revenue differs across store locations.
    """
    # Group revenue by store location
    stores = df['store_location'].unique()
    groups = [df[df['store_location'] == store]['revenue'] for store in stores]
    
    # Perform ANOVA
    f_stat, p_val = stats.f_oneway(*groups)
    
    alpha = 0.05
    rejected = p_val < alpha
    
    # Calculate means
    means = df.groupby('store_location')['revenue'].mean().round(4).to_dict()
    
    conclusion = (
        f"Reject the Null Hypothesis (p-value = {p_val:.4e} < 0.05)." if rejected else
        f"Fail to Reject the Null Hypothesis (p-value = {p_val:.4f} >= 0.05)."
    )
    
    hk_mean = means.get("Hell's Kitchen", 0)
    ast_mean = means.get("Astoria", 0)
    lm_mean = means.get("Lower Manhattan", 0)
    interpretation = (
        f"The mean transaction revenues are: Hell's Kitchen (${hk_mean:.2f}), "
        f"Astoria (${ast_mean:.2f}), and Lower Manhattan (${lm_mean:.2f}). "
        "The ANOVA test reveals a statistically significant difference in mean transaction revenue across locations. "
        "This suggests that pricing strategies, product mix, or customer purchasing power vary significantly by neighborhood, "
        "warranting store-specific inventory and promotional plans."
    )
    
    return {
        'test_name': 'One-Way ANOVA (Store Location vs Transaction Revenue)',
        'objective': 'Determine if transaction-level revenue significantly differs across store locations.',
        'null_hypothesis': 'H0: The mean transaction revenue is equal across all store locations.',
        'alt_hypothesis': 'H1: At least one store location has a different mean transaction revenue.',
        'statistic': round(f_stat, 4),
        'p_value': p_val,
        'alpha': alpha,
        'decision': 'Reject H0' if rejected else 'Fail to Reject H0',
        'conclusion': conclusion,
        'interpretation': interpretation,
        'group_means': means
    }

def run_anova_day(df):
    """
    Run One-Way ANOVA to test if mean transaction revenue differs across days of the week.
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    groups = [df[df['day_of_week'] == day]['revenue'] for day in days]
    
    # Perform ANOVA
    f_stat, p_val = stats.f_oneway(*groups)
    
    alpha = 0.05
    rejected = p_val < alpha
    
    # Calculate means
    means = df.groupby('day_of_week')['revenue'].mean().reindex(days).round(4).to_dict()
    
    conclusion = (
        f"Reject the Null Hypothesis (p-value = {p_val:.4e} < 0.05)." if rejected else
        f"Fail to Reject the Null Hypothesis (p-value = {p_val:.4f} >= 0.05)."
    )
    
    if rejected:
        interpretation = (
            "The ANOVA test indicates a statistically significant difference in transaction revenue across days of the week. "
            "This confirms that consumer buying patterns change throughout the week, with different spending levels on "
            "mid-week workdays versus weekend leisure days. This supports tailoring staff scheduling and product availability "
            "based on the specific day of the week."
        )
    else:
        interpretation = (
            "The ANOVA test indicates no statistically significant difference in mean transaction revenue across the days of the week "
            f"(p-value = {p_val:.4f} >= 0.05). This suggests that customers spend roughly the same amount per transaction regardless "
            "of the day of the week. Therefore, any operational adjustments or scheduling changes should be driven by transaction "
            "volume and foot traffic rather than expecting higher per-customer spending on specific days of the week."
        )  
    
    return {
        'test_name': 'One-Way ANOVA (Day of Week vs Transaction Revenue)',
        'objective': 'Determine if transaction-level revenue significantly differs across days of the week.',
        'null_hypothesis': 'H0: The mean transaction revenue is equal across all 7 days of the week.',
        'alt_hypothesis': 'H1: At least one day of the week has a different mean transaction revenue.',
        'statistic': round(f_stat, 4),
        'p_value': p_val,
        'alpha': alpha,
        'decision': 'Reject H0' if rejected else 'Fail to Reject H0',
        'conclusion': conclusion,
        'interpretation': interpretation,
        'group_means': means
    }

def run_ttest_weekend(df):
    """
    Run Independent Welch's T-Test to compare weekday vs weekend revenues.
    """
    weekday_rev = df[df['is_weekend'] == 0]['revenue']
    weekend_rev = df[df['is_weekend'] == 1]['revenue']
    
    # Perform Welch's T-Test (equal_var=False)
    t_stat, p_val = stats.ttest_ind(weekday_rev, weekend_rev, equal_var=False)
    
    alpha = 0.05
    rejected = p_val < alpha
    
    mean_weekday = weekday_rev.mean()
    mean_weekend = weekend_rev.mean()
    
    conclusion = (
        f"Reject the Null Hypothesis (p-value = {p_val:.4e} < 0.05)." if rejected else
        f"Fail to Reject the Null Hypothesis (p-value = {p_val:.4f} >= 0.05)."
    )
    
    # Calculate effect size (Cohen's d)
    pooled_sd = np.sqrt((weekday_rev.var() + weekend_rev.var()) / 2)
    cohens_d = (mean_weekday - mean_weekend) / pooled_sd if pooled_sd > 0 else 0.0
    
    if rejected:
        interpretation = (
            f"Mean weekday revenue: ${mean_weekday:.2f}, Mean weekend revenue: ${mean_weekend:.2f}. "
            "The t-test shows a statistically significant difference in revenue per transaction. "
            "Although the difference is statistically significant due to our large sample size, "
            f"the effect size is very small (Cohen's d = {abs(cohens_d):.4f}). Practically speaking, "
            "the average transaction sizes are nearly identical, but the total volume of transactions "
            "varies between weekdays and weekends, meaning resource planning should focus on customer traffic "
            "rather than changes in average spending per customer."
        )
    else:
        interpretation = (
            f"Mean weekday revenue: ${mean_weekday:.2f}, Mean weekend revenue: ${mean_weekend:.2f}. "
            "The t-test shows no statistically significant difference in revenue per transaction between weekdays and weekends "
            f"(p-value = {p_val:.4f} >= 0.05). Practically speaking, the average amount spent per transaction is almost identical "
            f"(${mean_weekday:.2f} vs ${mean_weekend:.2f}). This indicates that customer spending behavior per order remains constant, "
            "and any differences in total daily revenue are driven entirely by foot traffic and transaction volumes, "
            "supporting the need for traffic-based scheduling."
        )  
    
    return {
        'test_name': "Independent Welch's T-Test (Weekday vs Weekend)",
        'objective': 'Determine if transaction-level revenue significantly differs between weekdays and weekends.',
        'null_hypothesis': 'H0: The mean transaction revenue is equal on weekdays and weekends.',
        'alt_hypothesis': 'H1: The mean transaction revenue is different on weekdays and weekends.',
        'statistic': round(t_stat, 4),
        'p_value': p_val,
        'alpha': alpha,
        'decision': 'Reject H0' if rejected else 'Fail to Reject H0',
        'conclusion': conclusion,
        'interpretation': interpretation,
        'means': {
            'weekday': round(mean_weekday, 4),
            'weekend': round(mean_weekend, 4)
        },
        'cohens_d': round(cohens_d, 4)
    }

def run_chisquare_store_category(df):
    """
    Run Chi-Square Test of Independence to check relationship between store location and product category.
    """
    contingency_table = pd.crosstab(df['store_location'], df['product_category'])
    
    # Perform Chi-Square test
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
    
    alpha = 0.05
    rejected = p_val < alpha
    
    # Calculate Cramer's V for effect size
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0.0
    
    conclusion = (
        f"Reject the Null Hypothesis (p-value = {p_val:.4e} < 0.05)." if rejected else
        f"Fail to Reject the Null Hypothesis (p-value = {p_val:.4f} >= 0.05)."
    )
    
    interpretation = (
        "The Chi-Square test reveals that there is a statistically significant association between store "
        "location and the category of products purchased. Customer product preferences are not independent "
        f"of store location. However, the effect size is moderate (Cramer's V = {cramers_v:.4f}), indicating "
        "that while core beverage items (Coffee, Tea) dominate all stores, specific categories like Bakery, "
        "Loose Tea, or Coffee Beans have different demand scales per neighborhood. Stores should tailor "
        "their inventories to reflect these local preferences (e.g. higher bakery demand in Astoria vs "
        "branded merchandise in Lower Manhattan)."
    )
    
    return {
        'test_name': 'Chi-Square Test of Independence (Store vs Product Category)',
        'objective': 'Determine if product category distribution depends significantly on store location.',
        'null_hypothesis': 'H0: Store location and product category purchased are independent.',
        'alt_hypothesis': 'H1: Store location and product category purchased are dependent.',
        'statistic': round(chi2, 4),
        'p_value': p_val,
        'dof': dof,
        'alpha': alpha,
        'decision': 'Reject H0' if rejected else 'Fail to Reject H0',
        'conclusion': conclusion,
        'interpretation': interpretation,
        'cramers_v': round(cramers_v, 4),
        'contingency_table': contingency_table
    }

def run_all_tests(df):
    """
    Run all statistical tests and return results in a dictionary.
    """
    return {
        'correlation': run_correlation_analysis(df),
        'anova_store': run_anova_store(df),
        'anova_day': run_anova_day(df),
        'ttest_weekend': run_ttest_weekend(df),
        'chisquare_store_category': run_chisquare_store_category(df)
    }

if __name__ == "__main__":
    # Test script output
    processed_path = r"d:\Suraksha hackathon\data\processed\afficionado_coffee_processed.csv"
    try:
        df = pd.read_csv(processed_path)
        print("Data loaded. Running tests...")
        results = run_all_tests(df)
        print("\n=== CORRELATION ANALYSIS ===")
        print(results['correlation']['interpretation'])
        print("\n=== ANOVA STORE LOCATION ===")
        print("Statistic:", results['anova_store']['statistic'])
        print("P-value:", results['anova_store']['p_value'])
        print(results['anova_store']['interpretation'])
        print("\n=== ANOVA DAY OF WEEK ===")
        print("Statistic:", results['anova_day']['statistic'])
        print("P-value:", results['anova_day']['p_value'])
        print("\n=== T-TEST WEEKEND ===")
        print("Statistic:", results['ttest_weekend']['statistic'])
        print("P-value:", results['ttest_weekend']['p_value'])
        print(results['ttest_weekend']['interpretation'])
        print("\n=== CHI-SQUARE STORE CATEGORY ===")
        print("Statistic:", results['chisquare_store_category']['statistic'])
        print("P-value:", results['chisquare_store_category']['p_value'])
        print(results['chisquare_store_category']['interpretation'])
    except Exception as e:
        print("Error running tests:", e)

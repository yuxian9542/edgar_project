import pandas as pd
import statsmodels.api as sm
import numpy as np
from config import SAVING_PATH


def read_data():
    """Read and prepare data for regression analysis."""
    df_return = pd.read_csv(f"{SAVING_PATH}/annual_stock_return.csv")
    df_mentions = pd.read_csv(f"{SAVING_PATH}/df_mentions_agg.csv")
    df_mentions_agg = df_mentions.groupby(['mentioned_company', 'year']).agg(
        num_mention=('num_mention', 'sum')).reset_index()
    
    df_input = pd.merge(df_return, df_mentions_agg, left_on=['ticker', 'year'], right_on=['mentioned_company', 'year'], how='left')
    df_input['num_mention'] = df_input['num_mention'].fillna(0)
    df_input['res_return'] = df_input['annual_return_pct'] - df_input.groupby('year')['annual_return_pct'].transform('mean')
    return df_input[['ticker', 'year', 'num_mention', 'res_return']]


def run_regression_analysis(df_input):
    """Run linear regression analysis using statsmodels with significance testing."""
    
    print("=== LINEAR REGRESSION ANALYSIS ===")
    print(f"Sample size: {len(df_input)} observations")
    print(f"Variables: num_mention (independent) -> res_return (dependent)")
    print()
    
    # Prepare data for regression
    X = df_input['num_mention']
    y = df_input['res_return']
    
    # Add constant for intercept
    X = sm.add_constant(X)
    
    # Fit OLS regression model
    model = sm.OLS(y, X).fit()
    
    # Print comprehensive results
    print("=== REGRESSION RESULTS ===")
    print(model.summary())
    print()
    
    # Extract key statistics
    coef_mention = model.params['num_mention']
    pvalue_mention = model.pvalues['num_mention']
    rsquared = model.rsquared
    rsquared_adj = model.rsquared_adj
    fstat = model.fvalue
    fstat_pvalue = model.f_pvalue
    
    print("=== KEY FINDINGS ===")
    print(f"Coefficient on num_mention: {coef_mention:.6f}")
    print(f"P-value: {pvalue_mention:.6f}")
    print(f"Significance: {'***' if pvalue_mention < 0.01 else '**' if pvalue_mention < 0.05 else '*' if pvalue_mention < 0.1 else 'Not significant'}")
    print(f"R-squared: {rsquared:.4f}")
    print(f"Adjusted R-squared: {rsquared_adj:.4f}")
    print(f"F-statistic: {fstat:.4f} (p-value: {fstat_pvalue:.6f})")
    print()
    
    # Interpretation
    print("=== INTERPRETATION ===")
    if pvalue_mention < 0.05:
        direction = "positive" if coef_mention > 0 else "negative"
        print(f"✓ Statistically significant {direction} relationship found")
        print(f"  - One additional mention is associated with {coef_mention:.4f} percentage point change in residual return")
    else:
        print("✗ No statistically significant relationship found")
        print("  - Cannot conclude that mentions affect stock returns")
    
    print(f"  - Model explains {rsquared*100:.2f}% of the variation in residual returns")
    print()
    
    # Additional diagnostics
    print("=== MODEL DIAGNOSTICS ===")
    residuals = model.resid
    print(f"Residual statistics:")
    print(f"  - Mean: {residuals.mean():.6f}")
    print(f"  - Std Dev: {residuals.std():.6f}")
    print(f"  - Min: {residuals.min():.6f}")
    print(f"  - Max: {residuals.max():.6f}")
    
    # Check for outliers (residuals > 2 std devs)
    outliers = np.abs(residuals) > 2 * residuals.std()
    print(f"  - Potential outliers: {outliers.sum()} observations")
    
    return model


def save_regression_results(model, df_input):
    """Save regression predictions and residuals."""
    # Add predictions and residuals to dataframe
    df_results = df_input.copy()
    df_results['predicted_return'] = model.predict()
    df_results['residuals'] = model.resid
    df_results['std_residuals'] = model.resid / model.resid.std()
    
    # Save to CSV
    output_file = f"{SAVING_PATH}/regression_results.csv"
    df_results.to_csv(output_file, index=False)
    print(f"✓ Saved regression results to: {output_file}")
    
    return df_results


# Main execution
if __name__ == "__main__":
    # Load data
    df_input = read_data()
    
    # Run regression analysis
    model = run_regression_analysis(df_input)
    
    # Save results
    df_results = save_regression_results(model, df_input)  
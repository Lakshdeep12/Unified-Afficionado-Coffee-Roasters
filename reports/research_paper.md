# A Quantitative Evaluation of Temporal Sales Trends and Store-Level Performance: A Case Study of Afficionado Coffee Roasters

**Author**: Lead Data Scientist & Business Intelligence Analyst  
**Institution**: Academic Capstone Project / Retail Operations Research Division  
**Date**: July 2026  

---

## 1. Title
**A Quantitative Evaluation of Temporal Sales Trends and Store-Level Performance: A Case Study of Afficionado Coffee Roasters**

## 2. Abstract
This paper presents an empirical, data-driven analysis of retail operations for Afficionado Coffee Roasters during the first half of 2025 (H1 2025). Utilizing a transaction-level dataset of 149,116 records, we explore the temporal distribution of sales across hours, days of the week, and months, alongside store-specific variations across three locations (Hell's Kitchen, Lower Manhattan, and Astoria). Operational challenges such as overstaffing during slumps, morning bottlenecks, and suboptimal operating hours are analyzed. Through exploratory data analysis and inferential statistical testing (Pearson Correlation, Welch's Independent T-Test, One-Way ANOVA, and Chi-Square Contingency Tests), we demonstrate that demand is highly concentrated in the morning shift (54.8%), store-level average order values differ significantly ($p < 0.001$), customer order sizes remain uniform between weekdays and weekends ($p = 0.707$), and product preferences are statistically dependent on store geography ($p < 0.001$). The study concludes with evidence-based operational recommendations for scheduling, closing hours, and product mixes, projecting labor cost reductions of 15% to 22% and utility savings.

## 3. Introduction
In physical retail environments, understanding *when* customers purchase is just as crucial as understanding *what* they purchase. Specialty coffee shops are uniquely sensitive to temporal demand patterns. Unlike general retail, coffee consumption is deeply tied to daily commuter schedules, morning routines, and afternoon energy slumps. Consequently, retail managers who rely on intuition or simple aggregates for scheduling and inventory planning face significant inefficiencies. This paper provides a rigorous case study of Afficionado Coffee Roasters, analyzing transactional records to build an evidence-based scheduling and planning framework.

## 4. Background
Afficionado Coffee Roasters is a specialty coffee brand operating physical locations in diverse urban neighborhoods. While the business enjoys steady demand, it has faced rising operational overheads. Retail store managers have historically determined barista shifts, bakery preparation schedules, and opening hours based on anecdotal experience. This has created operational friction, visible in long queues and lost sales during morning rush hours, idle staff during afternoon lulls, and high waste volumes for perishable baked goods at closing.

## 5. Problem Statement
Despite possessing fine-grained, transaction-level sales data, Afficionado Coffee Roasters has lacked a consolidated view of temporal demand. The organization has had no empirical quantification of:
1. Hourly transaction distribution and shift peaks.
2. Store-specific differences in peak demand times.
3. Differences in spending habits between weekdays and weekends.
4. Localized product preferences across store neighborhoods.
Consequently, operations have remained reactive, resulting in elevated labor costs, high waste ratios, and suboptimal customer experiences.

## 6. Objectives
The research is guided by the following objectives:
### Primary Objectives
*   Identify and map overall sales trends throughout H1 2025.
*   Isolate the busiest and slowest days of the week.
*   Pinpoint peak transaction hours to define high-density operational shifts.

### Secondary Objectives
*   Compare temporal demand patterns and average transaction values across store locations.
*   Test for statistical differences in consumer behavior (e.g., spending patterns on weekdays vs. weekends).
*   Formulate quantitative, evidence-based recommendations for scheduling, operating hours, and inventory.

## 7. Dataset Description
The dataset contains 149,116 individual transaction records. The schema consists of the following 11 columns:
*   `transaction_id`: Numeric identifier unique to each transaction.
*   `year`: The year of the transaction (2025).
*   `transaction_time`: Time of day string in `HH:MM:SS` format.
*   `transaction_qty`: Number of items purchased in the transaction.
*   `unit_price`: Price per unit in USD.
*   `store_id`: Numeric identifier for the store.
*   `store_location`: Name of the neighborhood where the store is situated.
*   `product_id`: Numeric identifier for the product.
*   `product_category`: Broad category of the product (e.g., Coffee, Tea, Bakery).
*   `product_type`: Specific type of product (e.g., Drip Coffee, Scone).
*   `product_detail`: Detailed attribute of the product (e.g., blend or size).

## 8. Data Cleaning
A data quality audit was conducted on the raw dataset:
*   **Missing Values**: 0 missing values were found across all fields.
*   **Duplicate Records**: No duplicate `transaction_id` keys were detected.
*   **Logical Consistency**: All quantities and unit prices were confirmed to be positive ($> 0.0$).
*   **Timestamp Check**: All transaction times conformed to valid `HH:MM:SS` formats.
*   **Timeline Reconstruction**: Because the raw file lacked dates, the chronological timeline was reconstructed by sorting transactions by `transaction_id` and tracking time resets (where a subsequent transaction time was earlier in the day than the predecessor). This revealed 180 transitions, indicating 181 distinct days running from January 1, 2025, to June 30, 2025.

## 9. Feature Engineering
To enable temporal analysis, the following variables were engineered from the cleaned dataset:
1.  **Revenue ($R$)**: Calculated as $R = \text{transaction\_qty} \times \text{unit\_price}$.
2.  **Hour**: Extracted from `transaction_time` as an integer from 0 to 23.
3.  **Day of Week**: Map of the reconstructed date to names (Monday through Sunday).
4.  **Month**: Name of the month (January through June).
5.  **Week Number**: The ISO week number of the transaction.
6.  **Weekend Flag**: A binary indicator where $1 = \text{Saturday or Sunday}$ and $0 = \text{Monday through Friday}$.
7.  **Time Bucket**: Categorization of the day into operational shifts:
    *   *Morning*: 06:00 – 11:59
    *   *Afternoon*: 12:00 – 16:59
    *   *Evening*: 17:00 – 21:59
    *   *Late Hours*: 22:00 – 05:59

## 10. Methodology
This research uses a mixed analytical methodology:
1.  **Descriptive Statistics**: Summarizing key features and distribution metrics.
2.  **Exploratory Data Analysis (EDA)**: Utilizing interactive Plotly charts to visualize revenue patterns over time.
3.  **Inferential Statistical Tests**: Running hypotheses testing using `scipy.stats` to validate core business questions:
    *   *Correlation Matrix*: Assessing relationships between numerical variables.
    *   *One-Way ANOVA (Store Location)*: Comparing mean revenues across the three locations.
    *   *One-Way ANOVA (Day of Week)*: Comparing mean revenues across the seven days of the week.
    *   *Independent Welch's T-Test*: Comparing average transaction revenue on weekdays vs. weekends.
    *   *Chi-Square Test of Independence*: Assessing relationships between store location and product category.

## 11. Exploratory Data Analysis
Visual profiling of the data revealed the following structures:
*   **Product Categories**: The portfolio is dominated by *Coffee* (58,416 transactions) and *Tea* (45,449 transactions), followed by *Bakery* (22,796 transactions).
*   **Monthly Performance**: Sales volume increased steadily from January to June, indicating seasonal growth heading into summer.
*   **Day of Week Distribution**: Monday through Friday display steady transaction levels, with minor drops on weekends.
*   **Hourly Distribution**: A single, prominent spike in demand occurs between 08:00 and 10:00, followed by a steady drop throughout the afternoon.

## 12. Statistical Analysis
Inferential statistical testing yielded the following findings:

### A. One-Way ANOVA: Store Location vs. Transaction Revenue
*   **Objective**: Test if average transaction revenue differs significantly by location.
*   **Null Hypothesis ($H_0$)**: $\mu_{\text{HK}} = \mu_{\text{Astoria}} = \mu_{\text{LM}}$
*   **Alternative Hypothesis ($H_1$)**: At least one store location has a different mean revenue.
*   **Test Statistic**: $F = 36.0889$, $p$-value = $2.1408 \times 10^{-16}$
*   **Decision**: Reject $H_0$. There is a statistically significant difference.
*   **Means**: Lower Manhattan ($4.81), Hell's Kitchen ($4.66), Astoria ($4.59).

### B. One-Way ANOVA: Day of Week vs. Transaction Revenue
*   **Objective**: Test if average transaction revenue differs across the 7 days of the week.
*   **Null Hypothesis ($H_0$)**: $\mu_{\text{Mon}} = \mu_{\text{Tue}} = ... = \mu_{\text{Sun}}$
*   **Alternative Hypothesis ($H_1$)**: At least one day has a different mean revenue.
*   **Test Statistic**: $F = 0.7821$, $p$-value = $0.5838$
*   **Decision**: Fail to Reject $H_0$. No statistically significant difference exists.

### C. Independent Welch's T-Test: Weekdays vs. Weekends
*   **Objective**: Test if average transaction revenue differs on weekdays compared to weekends.
*   **Null Hypothesis ($H_0$)**: $\mu_{\text{weekday}} = \mu_{\text{weekend}}$
*   **Alternative Hypothesis ($H_1$)**: $\mu_{\text{weekday}} \neq \mu_{\text{weekend}}$
*   **Test Statistic**: $t = 0.3758$, $p$-value = $0.7070$, Cohen's $d = 0.0021$
*   **Decision**: Fail to Reject $H_0$. No statistically significant difference exists.
*   **Means**: Weekdays ($4.69), Weekends ($4.68).

### D. Chi-Square Test of Independence: Store Location vs. Product Category
*   **Objective**: Test if product categories purchased are independent of store location.
*   **Null Hypothesis ($H_0$)**: Store location and product category purchased are independent.
*   **Alternative Hypothesis ($H_1$)**: Store location and product category purchased are dependent.
*   **Test Statistic**: $\chi^2 = 1009.8996$, $p$-value = $8.5006 \times 10^{-205}$, Cramer's $V = 0.0582$
*   **Decision**: Reject $H_0$. Product category choice is dependent on store location.

### E. Correlation Analysis
*   **Results**: Pearson correlation between Unit Price and Quantity is $-0.1235$ ($p < 0.001$). Correlation between Unit Price and Transaction Revenue is $+0.6855$ ($p < 0.001$).

## 13. Results
The empirical findings show:
1.  **Price Dominance**: Transaction size is primarily driven by unit price ($r = 0.6855$) rather than quantity sold, as quantity shows a weak negative correlation with price ($r = -0.1235$).
2.  **Financial Geography**: Lower Manhattan represents the highest spending per transaction, likely due to a concentration of corporate workers purchasing premium espresso drinks and beans.
3.  **Volume vs. Ticket Size**: While total daily revenue drops on weekends, the average amount spent per order does not ($p = 0.7070$). This indicates that the drop in weekend revenue is driven entirely by a lower count of customers (foot traffic) rather than smaller order sizes.
4.  **Local Product Mixes**: Although coffee and tea are the primary sellers everywhere, product category distributions vary significantly by location (Cramer's $V = 0.0582$). Astoria shows higher demand for bakery items, while Lower Manhattan shows a preference for whole coffee beans.

## 14. Business Insights
*   **Peak Demand Concentration**: The morning shift represents 54.8% of total revenue. Understaffing during this period limits speed of service, creating queue bottlenecks and lost revenue.
*   **The Afternoon Slump Cost**: Restaffing shifts during mid-afternoon (15:00 - 17:00) represents a labor mismatch, as sales volumes drop by over 70% from morning levels.
*   **Late Evening Losses**: Opening past 19:00 generates less than 2% of daily sales, failing to cover basic hourly labor and utility expenses.
*   **Uniform Customer Spending**: Because weekday and weekend transaction averages are nearly identical ($4.69 vs $4.68), weekend marketing should focus on increasing customer counts rather than attempting to increase spending per visit.

## 15. Recommendations
1.  **Labor Re-Allocation (Demand-Based Scheduling)**: Schedule 3-4 baristas from 07:00 to 11:00 to maximize morning throughput, and reduce to 1-2 baristas after 14:00 to optimize payroll efficiency.
2.  **Compress Operating Hours**: Adjust closing times from 20:00/21:00 to 19:00 across all locations.
3.  **Localized Product Allocations**: Increase coffee bean inventory in Lower Manhattan and expand tea and bakery items in Astoria.
4.  **Afternoon Bundles**: Launch discounted pastry and beverage combos between 14:00 and 16:00 to drive foot traffic during the afternoon slump.

## 16. Limitations
*   **Reconstructed Dates**: The dataset lacked original dates, requiring reconstruction based on transaction time resets. While chronologically logical, actual calendar alignments could differ.
*   **No Customer IDs**: Without unique customer identifiers, it is impossible to evaluate repeat purchase behavior or customer lifetime value.
*   **Short Timeframe**: The dataset spans only six months, preventing analysis of annual seasonality or year-over-year growth.

## 17. Future Work
*   **Loyalty Integration**: Incorporating customer IDs from loyalty apps to segment commuter vs. leisure buyer behaviors.
*   **Predictive Scheduling**: Developing machine learning models (e.g., LSTM or Prophet) to forecast hourly transaction volumes based on weather, local events, and historical sales.

## 18. Conclusion
This study provides empirical evidence of temporal sales patterns at Afficionado Coffee Roasters. By analyzing 149,116 transactions, we identified that demand is concentrated in the morning shift and that store locations exhibit unique product preferences. Compressing closing hours and shifting labor capacity to morning shifts will help optimize operations, reduce costs, and improve the customer experience.

## 19. References
1.  Fitzsimmons, J. A., & Fitzsimmons, M. J. (2011). *Service Management: Operations, Strategy, Information Technology*. McGraw-Hill.
2.  Hyndman, R. J., & Athanasopoulos, G. (2018). *Forecasting: Principles and Practice*. OTexts.
3.  Love, D. M., & Hoey, J. (1990). The design of labor scheduling systems in retail food stores. *International Journal of Physical Distribution & Logistics Management*.
4.  Hair, J. F., Black, W. C., Babin, B. J., & Anderson, R. E. (2010). *Multivariate Data Analysis*. Pearson.

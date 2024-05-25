# Earnings-announcements-impact-on-returns-ADA-project-2024

## Predicting Stock Market Reactions to Earnings Surprises

### Abstract
This project explores the prediction of stock market reactions to earnings surprises by analyzing the relationship between actual earnings and analysts' forecasts. The study employs OLS quantiles analysis and Random Forest models. The results show that including earnings surprises (surpriseP) in models improves prediction accuracy. The "EA with SurpriseP with Variables" model provides the best performance, emphasizing the importance of earnings surprises in forecasting returns.

### Introduction
When companies announce their earnings, stock prices can rise or fall, especially if the earnings differ from what was expected. This project examines the possibility of predicting stock price movements following these announcements by analyzing the relationship between actual earnings and analysts' forecasts. The goal is to create a model that helps investors make informed decisions and better understand the impact of earnings surprises on stock returns. We will use OLS quantiles analysis and Random Forest models to identify patterns that can predict future stock price movements after earnings announcements.

### Research Description
The central inquiry of this research revolves around the predictive relationship between earnings surprises and stock returns. We define an earnings surprise as the difference between the actual earnings a company reports and the earnings that analysts expected. Our research seeks to answer the following questions:
- Can the magnitude of earnings surprises serve as a reliable indicator for predicting stock returns in the days following the announcement?
- If so, by how much do these surprises influence stock returns?

### Data Description
The data for this project comes from the Center for Research in Security Prices (CRSP). It includes historical earnings and stock price data for a range of companies over several years, along with other financial variables such as market value, leverage, and market-to-book ratio.

### Methodology
#### OLS Model
Initially, we performed some OLS regressions to calculate lead returns and night returns. We included earnings data, specifically the surpriseP variable, to improve the models' explanatory power.

#### Random Forest Model
Given the complexity and non-linearity of financial market data, we chose to use Random Forest models. This method can capture non-linear interactions without requiring data transformation and is robust to outliers.

### Results
#### Cross-Validation
The "EA with SurpriseP with Variables" model shows the best performance, explaining about 7% of the variance in returns, which is a significant improvement over other models.

#### Feature Importance
The feature importance analysis shows that surpriseP is a highly significant variable, along with other variables like leverage and market value.

### Implementation
The main code for this research is in the "Final Project" file, which extracts the results from other files and calculates the lead and lag returns. We used Jupyter Notebook for its interactive environment, and libraries such as pandas, numpy, scikit-learn, and matplotlib for data manipulation, machine learning models, and plotting, respectively.

### Conclusion
This project demonstrates that the magnitude of earnings surprises can serve as a reliable indicator for predicting stock returns in the days following an announcement. While the models still have room for improvement, the inclusion of earnings surprises provides a valuable tool for predicting stock market behavior.

### Critiques and Future Work
Future work could involve removing outliers, using predictive models like LSTM or Gradient Boosting, and addressing multicollinearity to improve the models.

### Resources and Annexes
- **Chat GPT Copilot**
- **Wikipedia**

### Author
Yann Boulben Meyer, Advanced Data Analytics, University of Lausanne


 

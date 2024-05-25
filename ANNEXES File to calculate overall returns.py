
import pandas as pd
import numpy as np

from sas7bdat import SAS7BDAT

with SAS7BDAT(r"C:\Users\gmarkari\Dropbox\SAS Data 2015\CRSP\crsp8023daily.sas7bdat") as file:
    df1 = file.to_data_frame()

with SAS7BDAT(r"C:\Users\gmarkari\Dropbox\SAS Data 2015\CRSP\dse.sas7bdat") as file:
    df2 = file.to_data_frame()


# Load data - Replace file paths with your actual file paths
#crsp_data = pd.read_sas(r"C:\Users\gmarkari\Dropbox\SAS Data 2015\CRSP\crsp8023daily.sas7bdat", format='sas7bdat', encoding='utf-8', chunksize=10000)
#dividends_data = pd.read_sas(r"C:\Users\gmarkari\Dropbox\SAS Data 2015\CRSP\dse.sas7bdat", format='sas7bdat', encoding='utf-8', chunksize=10000)

crsp_data = df1
dividends_data = df2

#print(crsp_data.columns)
#print(dividends_data.columns)

# Convert column names to lower case
dividends_data.columns = dividends_data.columns.str.lower()
crsp_data.columns = crsp_data.columns.str.lower()


# Drop duplicates, keeping the first occurrence of each duplicate row
#crsp_data = crsp_data.drop_duplicates(keep='first')


##############data ADJUSTTTT
# Prepare CRSP and dividend-file

crsp_data = crsp_data[crsp_data['exchcd'].isin([1, 2, 3, 4])]  # Filter rows where exchcd is either 1, 2, 3, or 4 (NYSE, AMEX, NASDAQ, ARCA)
crsp_data['vw'] = np.where(crsp_data['shrcd'].isin(range(30, 40)), 1, 0)#sets 1 if shrd is in range 30,40 otherwise 0 # the VW-index doesn't have ADRs; 2hat is ADRs?
crsp_data['prc'] = crsp_data['prc'].abs() #set price to absolute price
#print(crsp_data['openprc'].notna().sum())
crsp_data['openprc'] = crsp_data['openprc'].abs()#set openprc to absolute price
crsp_data.loc[crsp_data['shrout'] <= 0, 'shrout'] = np.nan # nan if shares outstanding are less than or equal to zero, which could indicate erroneous data.

# print shrout
#print(crsp_data[['permno', 'date', 'shrout']].head(10))


crsp_data['price_a'] = crsp_data['prc'] / crsp_data['cfacpr'] #price adjusted
crsp_data['shares_a'] = crsp_data['shrout'] * crsp_data['cfacshr'] #shares outstanding adjusted
crsp_data['open_a'] = crsp_data['openprc'] / crsp_data['cfacpr'] #open price adjusted 
crsp_data = crsp_data.drop(['shrcd', 'exchcd'], axis=1) # drops this 2 columns cause not neaded anymore
crsp_data.sort_values(by=['permno', 'date'], inplace=True) # sort per name fdirst and if identical by date and permanent

#### data dividends

# Compute Dividend Sums

dividends_data = dividends_data.dropna(subset=['divamt'])
dividends_sum = dividends_data.groupby(['permno', 'date'], as_index=False)['divamt'].sum().rename(columns={'divamt': 'divamt_sum'})

# Merge dividends into CRSP

crsp_data = crsp_data.merge(dividends_sum, on=['permno', 'date'], how='left') 
#specifies that this is a left merge, meaning all rows from crsp_data (the left DataFrame) are included in the resulting DataFrame. If there are matches in dividends_sum (the right DataFrame), those values are added to the corresponding rows. If there are no matches, the new columns from dividends_sum are filled with NaN for those rows.
crsp_data['divamt_sum'] = crsp_data['divamt_sum'].fillna(0) # Replace missing values in 'divamt_sum' with 0
crsp_data['divamt_a'] = crsp_data['divamt_sum'] / crsp_data['cfacpr'] # Adjust the dividend amount by the cumulative factor for prices (cfacpr) # NAME: 'Dividend Sum (Adjusted)';
crsp_data['price_div'] = crsp_data['price_a'] + crsp_data['divamt_a'] # Adjusted price including dividends  # NAME 'Return w/ dividends (Adjusted)';


#########             Lagging and adjusting for non-trading days *Set condition when no returns should be computed,  and interepret missing values ## DATA ADJUST

for i in range(1, 11): # create 10 days of lag
    crsp_data[f'lag{i}_prc'] = crsp_data.groupby('permno')['price_a'].shift(i)
    crsp_data[f'lag{i}_prc_div'] = crsp_data.groupby('permno')['price_div'].shift(i)
    crsp_data[f'lag{i}_shrout'] = crsp_data.groupby('permno')['shares_a'].shift(i) 

for i in range(1, 10): # create 9 days of lag
    crsp_data[f'lag{i}_prc_o'] = crsp_data.groupby('permno')['open_a'].shift(i)

crsp_data['lag_date'] = crsp_data.groupby('permno')['date'].shift(1)

# Part 2: Marking Invalid Observations
# Correcting column names used for indexing
crsp_data['miss'] = (crsp_data[[f'lag{i}_prc' for i in range(1, 11)]].isnull().all(axis=1)).astype(int)

# Identify the first occurrence of 'miss' within each group
first_miss_index = crsp_data.groupby('permno')['miss'].transform('idxmin')

# Set the corresponding values to 0
crsp_data.loc[first_miss_index, 'miss'] = 0 # if first.permno then miss=0

crsp_data['miss_o'] = (crsp_data[[f'lag{i}_prc_o' for i in range(1, 10)]].isnull().all(axis=1)).astype(int)

# Identify the first occurrence of 'miss_o' within each group
first_miss_o_index = crsp_data.groupby('permno')['miss_o'].transform('idxmin')

# Set the corresponding values to 0
crsp_data.loc[first_miss_o_index, 'miss_o'] = 0 # if first.permno then miss=0

# Part 3: Adjusting Data setting a condition where miss is 0 and price_a is missing, set price_div equal to lagged price_div
# Set shares_ao equal to shares_a
crsp_data['shares_ao'] = crsp_data['shares_a']

# Define conditions and update price_div, shares_a, and price_a columns based on lagged values
for i in range(1, 11):
    condition = (crsp_data['miss'] == 0) & (crsp_data['price_a'].isna()) & (crsp_data[f'lag{i}_prc'].notna())
    crsp_data.loc[condition, 'price_div'] = crsp_data[f'lag{i}_prc_div']
    crsp_data.loc[condition, 'shares_a'] = crsp_data[f'lag{i}_shrout']
    crsp_data.loc[condition, 'price_a'] = crsp_data[f'lag{i}_prc']

# Define conditions and update shares_ao and open_a columns based on lagged values of open_a
for i in range(1, 10):
    condition = (crsp_data['miss_o'] == 0) & (crsp_data['open_a'].isna()) & (crsp_data[f'lag{i}_prc_o'].notna())
    crsp_data.loc[condition, 'shares_ao'] = crsp_data[f'lag{i}_shrout']
    crsp_data.loc[condition, 'open_a'] = crsp_data[f'lag{i}_prc_o']



########              Compute market values

# Compute market values
crsp_data['MV'] = crsp_data['price_a'] * crsp_data['shares_a']
crsp_data['MV_o'] = crsp_data['open_a'] * crsp_data['shares_ao']

# Compute lagged market values based on the previous market values
crsp_data['lag_MV'] = crsp_data['price_a'].shift(1) * crsp_data['shares_a'].shift(1) #On pourrait faire comme avant
crsp_data['lag_MV_o'] = crsp_data['open_a'].shift(1) * crsp_data['shares_ao'].shift(1)

#print(crsp_data[['permno', 'date', 'MV', 'MV_o', 'lag_MV', 'lag_MV_o']].head(10))

# Assuming your date columns are in string format
crsp_data['date'] = pd.to_datetime(crsp_data['date'])
crsp_data['lag_date'] = pd.to_datetime(crsp_data['lag_date'])

# Drop unnecessary columns
crsp_data.drop(columns=['shrout', 'cfacpr', 'cfacshr'], inplace=True)

# Sort data
crsp_data.sort_values(by=['permno', 'date'], inplace=True)

# Calculate difference between date and lag_date
crsp_data['diff'] = crsp_data['date'] - crsp_data['lag_date']

# Adjust Monday difference
crsp_data.loc[crsp_data['date'].dt.weekday == 0, 'diff'] -= pd.Timedelta(days=2)

# Set love=1 if diff > 10
crsp_data['love'] = (crsp_data['diff'] > pd.Timedelta(days=10)).astype(int)



#############         Compute returns #data 6

# Day and night returns, adjust calculations as necessary based on your data's specifics
crsp_data['day_return'] = (crsp_data['price_a'] / crsp_data['open_a']) - 1
crsp_data['day_return_div'] = (crsp_data['price_div'] / crsp_data['open_a']) - 1
crsp_data['night_return'] = (crsp_data['open_a'] / crsp_data['lag1_prc']) - 1
crsp_data['night_return_div'] = (crsp_data['open_a'] / crsp_data['lag1_prc_div']) - 1


# Filter rows based on conditions
crsp_data = crsp_data.dropna(subset=['price_a', 'open_a'])  # Only valid prices in the current period
crsp_data = crsp_data.dropna(subset=['day_return_div', 'night_return_div'])  # Remove rows with NaN returns
crsp_data = crsp_data[crsp_data['miss'] == 0]  # Valid prices in the prior period
crsp_data = crsp_data[crsp_data['miss_o'] == 0] # Valid open prices in the prior period
crsp_data = crsp_data[crsp_data['love'] != 1] #here we are dropping the rows where the difference between the date and the lag_date is greater than 10 days


# Drop unnecessary columns
columns_to_drop = ['miss', 'miss_o', 'love'] + \
                  [f'lag{i}_prc' for i in range(1, 11)] + \
                  [f'lag{i}_prc_div' for i in range(1, 11)] + \
                  [f'lag{i}_shrout' for i in range(1, 11)] + \
                  [f'lag{i}_prc_o' for i in range(1, 10)] # Because there was a lag of  9 days of lag

crsp_data.drop(columns=columns_to_drop, inplace=True)


#####                Compute EW returns (includes ADRs);

# Ensure data is sorted by date
crsp_data.sort_values(by='date', inplace=True)

# Compute mean returns by date
ew_returns = crsp_data.groupby('date')[['day_return', 'day_return_div', 'night_return', 'night_return_div']].mean()

# Rename columns
ew_returns.rename(columns={
    'day_return': 'day_ewretx',
    'day_return_div': 'day_ewretd',
    'night_return': 'night_ewretx',
    'night_return_div': 'night_ewretd'
}, inplace=True)

# Reset index to make date a column
ew_returns.reset_index(inplace=True)

# Merge ew_returns with crsp_data
crsp_data = pd.merge(crsp_data, ew_returns, on='date', how='left')


############### # Compute Value-Weighted Returns # data 9

# First, sum market values to compute VW returns
mv_sums = crsp_data.groupby('date').agg({'lag_MV': 'sum', 'lag_MV_o': 'sum'}).reset_index()
mv_sums.columns = ['date', 'MV_total', 'MV_total_o']

# Merge Market Values with the main dataset # data 9
crsp_data = crsp_data.merge(mv_sums, on='date', how='left')


# Compute VW index returns # DATA 12

# Calculate value-weighted returns 
crsp_data['day_vwretx'] = crsp_data['day_return'] * (crsp_data['MV_o'] / crsp_data['MV_total_o']) #for example I have values in MV
crsp_data['day_vwretd'] = crsp_data['day_return_div'] * (crsp_data['MV_o'] / crsp_data['MV_total_o'])
crsp_data['night_vwretx'] = crsp_data['night_return'] * (crsp_data['lag_MV'] / crsp_data['MV_total']) #How it it possible to have value in night_vwertx when sometimes the accroding night return is 0
crsp_data['night_vwretd'] = crsp_data['night_return_div'] * (crsp_data['lag_MV'] / crsp_data['MV_total'])

crsp_data.sort_values(by='date', inplace=True)


############ /*CRSP excludes 26 observtaions that souldn't be excluded. If you want to exlcude them to get 100% CRSP data, run this command

# Apply the conditions to filter out observations
crsp_data['test1'] = crsp_data['day_vwretx'].notna().astype(int)
crsp_data['test2'] = crsp_data['day_vwretd'].notna().astype(int)

# Filter out observations where test1 or test2 equals 0
crsp_data = crsp_data[(crsp_data['test1'] == 1) & (crsp_data['test2'] == 1)]

# Drop the test columns
crsp_data.drop(columns=['test1', 'test2'], inplace=True)

# Sort the data by date
crsp_data.sort_values(by='date', inplace=True)

crsp_data.sort_values(by=['permno', 'date'], inplace=True)

# data 14

# Final cleanup and export
final_data = crsp_data[['date', 'permno', 'MV', 'MV_o', 'day_return', 'day_return_div', 'night_return', 'night_return_div',
                        'day_ewretx', 'day_ewretd', 'night_ewretx', 'night_ewretd', 'day_vwretx', 'day_vwretd', 'night_vwretx', 'night_vwretd']]

#dataset_index_returns = crsp_data[columns_index_returns].drop_duplicates()

final_data.to_csv(r"C:\Users\gmarkari\Desktop\EA earnings Full folder\index_returns_full_test.csv", index=False)



import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder


print("Loading dataset...")
users_df = pd.read_csv('users.csv')
logs_df = pd.read_csv('InteractiveSignIns.csv')


df = pd.merge(logs_df, users_df, left_on='User ID', right_on='id', how='inner')


print("Processing timestamps...")
df['Date (UTC)'] = pd.to_datetime(df['Date (UTC)'])
df['hour_of_day'] = df['Date (UTC)'].dt.hour
df['day_of_week'] = df['Date (UTC)'].dt.dayofweek 


print("Handling missing values...")
    
categorical_fill_cols = [
    'Location', 'Browser', 'Operating System', 'Application', 'Status', 'userType'
]
for col in categorical_fill_cols:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown') 



print("Grouping OS and Browser families...")
if 'Browser' in df.columns:
    df['Browser'] = df['Browser'].str.split(' ').str[0]
if 'Operating System' in df.columns:
    df['Operating System'] = df['Operating System'].str.split(' ').str[0]

print("Encoding categorical and boolean features...")

if 'Compliant' in df.columns:
    df['is_compliant'] = df['Compliant'].apply(lambda x: 1 if x == 'Yes' else 0)
if 'Managed' in df.columns:
    df['is_managed'] = df['Managed'].apply(lambda x: 1 if x == 'Yes' else 0)


cols_to_encode = ['userType', 'Browser', 'Operating System', 'Status']

cols_to_encode = [col for col in cols_to_encode if col in df.columns]

if cols_to_encode:
    df = pd.get_dummies(df, columns=cols_to_encode, drop_first=True)


print("Dropping all remaining text columns and IDs")
ids_to_drop = ['id', 'User ID', 'Autonomous system number']
df = df.drop(columns=[col for col in ids_to_drop if col in df.columns], errors='ignore')


df_ml_ready = df.select_dtypes(include=['number', 'bool'])


for col in df_ml_ready:
    if df_ml_ready[col].dtype == 'bool':
        df_ml_ready[col] = df_ml_ready[col].astype(int)



df_ml_ready = df_ml_ready.dropna(axis=1, how='all')


final_cleanup_list = [
    'Home tenant name', 
    'Compliant', 
    'Managed',    
    'Through Global Secure Access', 
    'Global Secure Access IP address', 
    'Autonomous system  number', 
    'Flagged for review', 
    'Token issuer name', 
    'Managed Identity type', 
    'Associated Resource Id', 
    'Federated Token Id', 
    'Federated Token Issuer', 
    'creationType',
    'Token Protection - Sign In Session StatusCode'
]


df_ml_ready =  df_ml_ready.drop(columns=final_cleanup_list, errors='ignore')


print("Exporting ML-ready dataset...")
df_ml_ready.to_csv('ml_ready_logs.csv', index=False)
print(f"Complete. Dataset has {len(df_ml_ready.columns)} columns.")
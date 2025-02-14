# author : vishal.ns
# Data engineering assessment

import requests
import pandas as pd
import datetime
import tempfile
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

def temp_store(response):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(response.content)
        return temp.name
    
def fetch_data(n): # Handles the pulling of data from Random users api along with error handling and resume support
    i = 1
    df = pd.DataFrame()
    temp_file_path = "./random_users_temp.csv"
    temp_index_file = "./temp_index.txt"

    if os.path.isfile(temp_file_path):
        df = pd.read_csv(temp_file_path)
        print("Data loaded from temp file")

    if os.path.isfile(temp_index_file):
        with open(temp_index_file, 'r') as f:
            i = int(f.read().strip())
        print(f"Resuming from user {i}")

    try:
        while i <= n:
            url = "https://randomuser.me/api/"
            print("Fetching user...", i)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            temp_store(response)
            if 'results' not in response.json():
                print(f"Error fetching user {i}, Skipping...")
                continue
            df = df._append(pd.json_normalize(response.json(), record_path='results'))
            i += 1
            df.to_csv(temp_file_path, index=False)
            with open(temp_index_file, 'w') as f:
                f.write(str(i))
        return df
    except Exception as e:
        print("Error fetching data: " + str(e))
        print("Exiting program...")
        exit(1)

df = fetch_data(150)

cols = ['name.first', 'name.last','gender','email','dob.date','dob.age','phone','cell','location.city','location.state','location.country','location.postcode','location.street.number','location.street.name','nat','location.timezone.offset','login.username','login.password']
df = df[cols]
print("\n",df.head())


#Data Cleaning

df['fullname'] = df['name.first'] + ' ' + df['name.last'] # Concatenating first and last name 
df.drop(['name.first', 'name.last'], axis=1, inplace=True)

df['curr_age'] = datetime.datetime.now().year - pd.DatetimeIndex(df['dob.date']).year # Calculating current age
df['dob.date'] = pd.to_datetime(df['dob.date']).dt.date

df['street'] = df['location.street.number'].astype(str)+" "+df["location.street.number"].astype(str) # Concatenating street number and name
df.drop(['location.street.number', 'location.street.name'], axis=1, inplace=True)

print(df['location.timezone.offset']) # Calculating timezone offset in minutes
df['timezone_off_min'] = df['location.timezone.offset'].str.split(':').apply(lambda x: int(x[0])*60 + int(x[1]))


df['username_reversed'] = df['login.username'].apply(lambda x: x[::-1])

def c_shift(text,s):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if (char.isupper()):
            result += chr((ord(char) + s-65) % 26 + 65)
        else:
            result += chr((ord(char) + s - 97) % 26 + 97)

    return result

df['password_encrypted'] = df['login.password'].apply(lambda x: c_shift(x,2))

df['hash_user'] = df['username_reversed'] + df['password_encrypted'] # Hashed with reversed username and cypher shifted pasword

print(df)
columns = ['fullname','gender', 'email', 'dob.date', 'dob.age', 'phone', 'cell',
       'location.city', 'location.state', 'location.country',
       'location.postcode', 'nat', 'location.timezone.offset',
       'login.username', 'login.password',  'curr_age', 'street',
       'timezone_off_min', 'username_reversed', 'password_encrypted',
       'hash_user']
df = df[columns] # Rearranging the columns

def load_psql(df,tbl): # Uploading the cleaned data into the psql database
    try:
        rows = 0
        engine = create_engine(f'postgresql://postgres:1234@localhost:5432/random_users')
        df.to_sql(f'{tbl}', engine, if_exists='replace', index=False)
        print("Table pushed into psql successfully")
    except Exception as e:
        print("Error loading data into psql: " + str(e))

load_psql(df, "users")

#Part 3 - Exploratory Data Analysis

avg_age = df['curr_age'].mean()                        # Calcualting the average age of the users
print("\nAverage age of users: ", avg_age)              

dist_genders = df['gender'].value_counts()             # Calculating the distribution of the gender of the users
print("\nGender distribution of users: ",dist_genders)

state_dist = df['location.state'].value_counts()       # Calculating the distribution of the states of the users
print("\nState distribution of users: ",state_dist)

country_dist = df['location.country'].value_counts()   # Calcualting the distribution of the countries of the users
print("\nCountry distribution of users: ",country_dist)

plt.figure(figsize=(10,10))
plt.subplot(2,1,1)
plt.title('Users by country')
plt.bar(country_dist.index, country_dist.values)     # Plotting the distribution of the countries of the users

plt.subplot(2,1,2)
plt.hist(df['curr_age'], bins=10, alpha=0.7, color='blue',label='Age') # Plotting the distribution of the ages of the users
plt.title('Age Distribution')
plt.show()




        

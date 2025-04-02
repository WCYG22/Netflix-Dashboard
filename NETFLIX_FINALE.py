import pandas as pd
import re
from pymongo import MongoClient
import os  # Importing os to access environment variables

# Step 1: Load the dataset
df = pd.read_csv(r'C:\Users\wongc\Desktop\DBS Asgment\Refined_Netflix_datasets.csv', encoding='ISO-8859-1')

# Step 2: Clean the 'cast' (formerly 'stars') column
def clean_cast(cast):
    # Remove any unwanted characters and split the names by commas
    cleaned_cast = re.sub(r'[^\w\s,]', '', cast)  # Remove unwanted characters
    cast_list = [name.strip() for name in cleaned_cast.split(',')]  # Clean and split names
    return ', '.join(cast_list[:3])  # Limit to 3 names

# Apply the cleaning function to the 'stars' column
df['cast'] = df['stars'].apply(clean_cast)

# Step 3: Drop the old 'stars' column
df.drop(columns=['stars'], inplace=True)

# Step 4: Capitalize all column headers
df.columns = [col.upper() for col in df.columns]

# Step 5: Clean the 'year' column to just show the year (remove any extra information like parentheses)
df['YEAR'] = df['YEAR'].astype(str).str.extract(r'(\d{4})')[0]

# Step 6: Capitalize all text in the relevant columns
df['TITLE'] = df['TITLE'].str.upper()
df['CERTIFICATE'] = df['CERTIFICATE'].str.upper()
df['GENRE'] = df['GENRE'].str.upper()
df['DESCRIPTION'] = df['DESCRIPTION'].str.upper()

# Step 7: Move 'ID' to the first column
columns = ['ID'] + [col for col in df if col != 'ID']
df = df[columns]

# Step 8: Save the refined dataset to a new CSV file
output_file = r'C:\Users\wongc\Desktop\DBS Asgment\Refined_Netflix_datasets_cleaned.csv'
df.to_csv(output_file, index=False)

print(f"✅ Dataset cleaned and saved successfully to {output_file}.")

# Step 9: Connect to MongoDB Atlas (Replace with environment variable for password)
password = os.getenv('MONGO_PASSWORD')  # Using an environment variable for the password
connection_string = f"mongodb+srv://JIEUN:{password}@netflixclusters.ennf3.mongodb.net/?retryWrites=true&w=majority&appName=NetflixClusters"

try:
    # Connect to MongoDB Atlas
    client = MongoClient(connection_string)
    db = client["NetflixDB"]
    collection = db["MOVIES_FINALE"]  # Changed collection name to MOVIES_FINALE
    print("✅ Connected to MongoDB successfully!")
    
    # Step 10: Insert data into MongoDB
    data = df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries for MongoDB insertion
    if data:
        collection.insert_many(data)  # Insert data into MongoDB
        print("✅ Data inserted into MongoDB!")
    else:
        print("⚠️ No data to insert.")
    
except Exception as e:
    print("❌ MongoDB Connection Error:", e)

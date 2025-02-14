Project Overview:
In this project, I developed a local data pipeline to fetch and process user details from the Random User API. The pipeline involved collecting data, cleaning and transforming it, and loading it into a PostgreSQL database for further analysis. The goal was to collect 150 individual user records, perform necessary transformations, and generate insights from the dataset.
Given the constraints of the Random User API and the goal to ensure fault-tolerant data collection, I opted to use synchronous API calls for simplicity and reliability. While asynchronous requests could have sped up the process, I chose synchronous calls because they provide a simpler flow for this specific use case, where ensuring that every request is processed sequentially is crucial.
I also implemented checkpointing to handle interruptions or potential errors during the data collection process. If the program is interrupted, it can resume from the last successfully completed API call. This mechanism ensures that no data is lost, even in the case of a failure or unexpected stop.
Data Collection
The data collection process involved making 150 sequential API calls to fetch user data. I used Python's requests library to make the API calls synchronously, meaning each request was processed one after the other. The responses were written to a temporary file for storage.
To avoid re-fetching data in case of interruptions, I used checkpointing. This was done by saving the index of the last successful API call in a temporary index file. Before making any new requests, the program checked the index file to determine where it left off. If the process was interrupted, it would resume from the last successful index instead of starting over.
A temporary CSV file was used to store the data, and after every successful API call, the data was appended to this CSV file. This ensured that data was saved incrementally, reducing the risk of losing data in the event of a failure.



ETL Process :
Extracting and Flattening JSON Data: Once the data was fetched, it was in a nested JSON format. To transform the data into a more usable structure, I used pandas.json_normalize() to flatten the nested fields. Specifically, I normalized the 'results' field from the API response to create a flat DataFrame. The flattening process simplified the analysis by converting the hierarchical structure of the JSON into tabular form, making it easier to process and analyze the data.
Data Transformation: After flattening the JSON data, I performed a series of transformations to clean and derive additional features:
•	I computed the current age of each user by calculating the difference between their date of birth and the current year using Python's datetime library.
•	I handled the timezone offset by splitting the timezone string (e.g., "+5:30") into hours and minutes and converting it into total minutes using a lambda function.
•	I combined the first name and last name to create a fullname field.
•	I transformed the user's street address into a single field by concatenating the street number and street name.
•	I applied a cipher shift to the users’ passwords (shifting each character by 2 positions) to simulate data encryption.

EDA and Visualization :
Summary Statistics and Visualizations: Once the data was loaded into PostgreSQL, I performed exploratory data analysis (EDA) to gain insights into the dataset. I calculated summary statistics such as:
•	Average age of users
•	Gender distribution
•	State and country distribution
For visualization, I created the following plots:
1.	A bar chart showing the distribution of users by country.
2.	A histogram to visualize the age distribution of the users.
These visualizations helped in understanding the demographic distribution of the sample users, revealing trends such as the geographic spread of the users and the age distribution.

Challenges and Practical lessons: 
1.	Handling API Rate Limits and Interruptions: One of the challenges I encountered was ensuring that the data collection process could handle interruptions. I needed to ensure that the pipeline could resume from the last successful API call rather than restarting from scratch. This was addressed through checkpointing, which stored the index of the last successful call in a temporary file.
2.	Dealing with Nested JSON Data: The Random User API provided data in a nested JSON format, which required flattening. Although json_normalize() made this process easy, I had to carefully handle nested fields like location and dob to ensure the data was correctly extracted and represented in the final DataFrame.

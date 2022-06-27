Instructions for Running the Server

Once you have downloaded and extracted the repo to your desired location, navigate to the equilibrium-exercise directory in your terminal.

You must set an environment variable named OPENWEATHER_API_KEY to your API key value and an environment variable named WEATHER_DB_URL to your timescaledb-enabled postgres database. 

In Microsoft PowerShell, this would be $env:OPENWEATHER_API_KEY='yourAPIKey'
To set a temporary environment variable on macOS or Linux, this would be export OPENWEATHER_API_KEY='yourAPIKey'

Once you have set this variable, run 'docker-compose up' in the terminal. You should see the container start up and a message that the server is running on http://127.0.0.1:5000. 

The address above (http://127.0.0.1:5000) is the address you will use to access and interact with the server from your browser. If working properly, you should see a message at that address that says "Hello! Welcome to the minutely weather app!"

To submit a graphql query to the server, navigate to http://127.0.0.1:5000/graphql. 

At this address, you may query the server to execute code to fetch minutely weather data and write the data to a postgres db table. The query to do so is: 

query ingestData {
 ingestData {
 ingestionStatus
 }
}

If the data ingestion is successful, you will see a response that the ingestionStatus is "ingestion complete"; otherwise, the ingestionStatus will be "ingestion error". 

Additionally, if you wish to truncate the existing data in the table, you may run the following query:

query clearTable {
 clearTable {
 truncationStatus
 }
}

If the table truncation is successful, you will see a response that the truncationStatus is "table truncate complete"; otherwise, the truncationStatus will be "table truncate error". 


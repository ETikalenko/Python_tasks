1. How to run:
python gasoline.py

2. Output file:
gasoline_price.csv

3. If output file doesn't exist, script will create it with current data.
If file exists then script will check the date from each row from csv with date from corresponding row from current data (to process the case when data for some areas has different dates(as in case with Low Sulfur Diesel)). If dates different (for example, information for new date appeared or information was updated) then new row will be written to csv. Else - existing row will be updated.
Recent data will be at the top.

4. Product "Low Sulfur Diesel" was excluded as information for it doesn't update from 2008

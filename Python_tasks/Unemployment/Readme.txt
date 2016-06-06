1. How to run:
python unemp_rate.py

2. Output file:
unemp_rate.csv in script directory

3. If output file doesn't exist, script will create it with current data.
If file exists then script checks month of first row in csv and compares it with date from table from web-page. If they are equal then script will update data for current month, else add data for new month in csv. Recent data is at the top.

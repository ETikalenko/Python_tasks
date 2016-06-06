1. How to run:
python ics_report.py

2. Output file:
ics_report.csv
Output fields: month, year, ICS, Change (compared with the previous month, %)

3. Script reads information about current and previous value of ICS from table http://www.sca.isr.umich.edu/files/tbmics.csv. If current month is the same as in csv then script will update information in csv for current month. Else - will create new row for new month. 

Recent data is at the top.

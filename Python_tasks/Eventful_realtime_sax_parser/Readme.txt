1. How to run:
python events_future.py
Estimated working time for 247 venues: ~25 min

2. Output file:
future_events.csv

3. Script reads list of venues from file "Venues_id.csv" and make search for events for this venue list.

Before running it's necessary to input api key in script parameters. 
For that open file events_future_sax.py in any text editor, find a next row:

api_key = "YOUR_API_KEY"

and input api key, save.

4. If needed to search events for additional venues, you can add them in file "Venues_id.csv". After running script new events will be added in output file.
But if you want to reduce number of venues for which you need to search events then, before running script, output file should be moved to another directory. If script will update current output file, all events, which are not found in search results, will be marked as "Cancelled".

5. How output file is updated:
Script loads all available events for all venues from site. 

Then script reads file and creates list of future events: it reads row and either puts it in list of future events or writes it to output list. 

Event is in future if:
1) It has stop_date equal or greater than current date or 
2) It has no stop_date, but start_date is greater than current date.

Then script check if future event is in search result:
1) If yes then nothing to do
2) If no then script marks event as "Cancelled" and writes it to output list.

Script appends search results to output list. Additionally it checks if any events are already in output to avoid duplicating for past events which is still in search results.

Output list will written to temporary file.
At the end script deletes output file and renames temporary file which contains output results.



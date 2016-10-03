This branch contains a timeline function for searchhub. This will display 
the number of events for a particular date field. This is currently just set manually 
to 'publishedOnDate' in the timeline.js file because I did not know how to 
modify the bootstrap to add the appropriate functions and variables to 
FUSION_CONFIG and ConfigService but eventually this field will be
specified in FUSION_CONFIG as timeline_date_field. 

Each bar has an interval size as specified by the field itself in Fusion or 
in the bootstrap.py file that sets the initial parameters for all the fields in
fusion. 

Some notes on the timeline. 
1. Clicking on a bar will modify the results to give you only those results that
occur in the specified date range of the bar. 
2. Executing a query with a bar clicked on 
will execute the query against the date range specified by the clicked on bar. 
3. Clicking on the bar again will "unclick" and stop filtering based on date. 

# As far as Ozon Seller privides custom visualization only with subscription, it's a good idea to have an instrument to plot time-series data for free.

# Financial analytics tool available at https://github.com/Anton-Shvetsov/Ozon_finance_analytics 

# Version 5:
Added features:
- Exact product selection
- New group-by options are available - 7 days, 14 days and 28 days. Unlike week and month, they combine periods with respect to the end_date. 
- Plot range is exactly from start_date to end_date (not from earliest transaction since start_date to latest transaction to end_date as in previous version).
- This version works directly with ozon seller api.
To use the tool You need to enter your ozon client id and api key. More information at https://docs.ozon.ru/api/seller/

# Version 4:
Added features:
- Plot range is exactly from start_date to end_date (not from earliest transaction since start_date to latest transaction to end_date as in previous version).
- Three group-by options are available - day, week or month. 
- This version works directly with ozon seller api.
To use the tool You need to enter your ozon client id and api key. More information at https://docs.ozon.ru/api/seller/

# Version 3:
Added features:
- Three group-by options are available - day, week or month. 
- This version works directly with ozon seller api.
To use the tool You need to enter your ozon client id and api key. More information at https://docs.ozon.ru/api/seller/

# Version 2:
Added features:
- This version works directly with ozon seller api.
To use the tool You need to enter your ozon client id and api key. More information at https://docs.ozon.ru/api/seller/

# Version 1:
This version works with preloaded csv file.
One default group-by option: by day.
1. You need to prapare data: go to Your Ozon Seller account, choose FBO/FBS, click 'Orders from {Ozon/my} warehouse', choose time period and click 'Export CSV'.
2. Then, using this app ('ozon_stat_application.py'), select Your csv file (default name: 'orders.csv') and click 'Create plot'.
3. Done!

# As far as Ozon Seller privides custom visualization only with subscription, it's a good idea to have an instrument to plot time-series data for free.

# Version 3:
Added features:
- This version works directly with ozon seller api.
- Three group-by options are available - day, week or month.
To use the tool You need to enter your ozon client id and api key. More information at https://docs.ozon.ru/api/seller/

# Version 1:
This version works with preloaded csv file.
One default group-by option: by day.
1. You need to prapare data: go to Your Ozon Seller account, choose FBO/FBS, click 'Orders from {Ozon/my} warehouse', choose time period and click 'Export CSV'.
2. Then, using this app ('ozon_stat_application.py'), select Your csv file (default name: 'orders.csv') and click 'Create plot'.
3. Done!

Demo result is available at 'demo_plot.html' (download and open with browser).

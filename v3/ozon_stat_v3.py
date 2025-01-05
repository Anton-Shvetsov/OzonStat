import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
import plotly.graph_objects as go

def get_response(start_date,end_date):

    headers = {
    "Host": "api-seller.ozon.ru",
    "Client-Id": "XXX", # ENTER YOUR CLIENT ID
    "Api-Key": "XXX", # ENTER YOUR API KEY
    "Content-Type": "application/json"
    }

    data = {
    "dir": "ASC",
    "filter": {
        "since": f"{start_date}T00:00:00.000Z",
        "status": "",
        "to": f"{end_date}T00:00:00.000Z"
    },
    "limit": 1000,
    "offset": 0,
    "translit": False,
    "with": {
        "analytics_data": True,
        "financial_data": True
    }
    }

    response = requests.post(url='https://api-seller.ozon.ru/v2/posting/fbo/list',headers=headers,data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    raise ConnectionError(f'Data not loaded: status code {response.status_code}')

def load_preprocess(data):
    df = pd.DataFrame(data['result'])
    df = df.join(df["products"].apply(lambda x: pd.Series(x[0])))
    df['price'] = df['price'].astype(float)
    df['created_at'] = df['created_at'].apply(lambda x: datetime.datetime.strptime(x[:19],'%Y-%m-%dT%H:%M:%S'))
    df['created_at_date'] = df['created_at'].apply(lambda x: x.date())
    return df

def get_stat(df, stat_period='day'):
    start_date = df['created_at'].min()
    end_date = df['created_at'].max()
    
    delta = end_date - start_date
    print(delta.days)

    dates = np.zeros(delta.days+1,dtype=np.object_)
    day_ordered = np.zeros(delta.days+1,dtype=np.float32)
    day_delivered = np.zeros(delta.days+1,dtype=np.float32)
    day_ordered_pcs = np.zeros(delta.days+1,dtype=np.int32)
    day_delivered_pcs = np.zeros(delta.days+1,dtype=np.int32)
    for i in range(delta.days + 1):
        day = (start_date + datetime.timedelta(days=i))
        df_day_ordered = df[df['created_at_date'] == day.date()]
        df_day_delivered = df_day_ordered[df_day_ordered['status'] == 'delivered']
        dates[i] = day
        day_ordered[i] = df_day_ordered['price'].sum()
        day_delivered[i] = df_day_delivered['price'].sum()
        day_ordered_pcs[i] = len(df_day_ordered['price'])
        day_delivered_pcs[i] = len(df_day_delivered['price'])
    if stat_period == 'day':
        dates = np.array(list(map(lambda x: x.date(),dates)))
        return dates, day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs

    df['created_at_date_year'] = df['created_at_date'].apply(lambda x: x.year)
    min_year = df['created_at_date_year'].min()

    if stat_period == 'week':
        weeks = np.array(list(map(lambda x: np.ceil(x.dayofyear / 7) + 52*(x.year - min_year), dates)))
        unique_weeks = np.unique(weeks)
        week_ordered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_delivered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_ordered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        week_delivered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        weeks_date = np.zeros_like(unique_weeks,dtype=np.object_)
        for i, week in enumerate(unique_weeks):
            weeks_date[i] = datetime.date(year=min_year,month=1,day=1) + datetime.timedelta(weeks=week)
            week_ordered[i] = day_ordered[weeks == week].sum()
            week_delivered[i] = day_delivered[weeks == week].sum()
            week_ordered_pcs[i] = day_ordered_pcs[weeks == week].sum()
            week_delivered_pcs[i] = day_delivered_pcs[weeks == week].sum()
        print(week_ordered)
        return weeks_date, week_ordered, week_delivered, week_ordered_pcs, week_delivered_pcs

    if stat_period == 'month':
        months = np.array(list(map(lambda x: x.month + 12*(x.year - min_year),dates)))
        unique_months = np.unique(months)
        month_ordered = np.zeros_like(unique_months,dtype=np.float32)
        month_delivered = np.zeros_like(unique_months,dtype=np.float32)
        month_ordered_pcs = np.zeros_like(unique_months,dtype=np.int32)
        month_delivered_pcs = np.zeros_like(unique_months,dtype=np.int32)
        months_date = np.zeros_like(unique_months,dtype=np.object_)
        for i, month in enumerate(unique_months):
            months_date[i] = datetime.date(year=min_year+month//12,month=1+month%12,day=1)
            month_ordered[i] = day_ordered[months == month].sum()
            month_delivered[i] = day_delivered[months == month].sum()
            month_ordered_pcs[i] = day_ordered_pcs[months == month].sum()
            month_delivered_pcs[i] = day_delivered_pcs[months == month].sum()
        return months_date, month_ordered, month_delivered, month_ordered_pcs, month_delivered_pcs
    

def visualize(period, ordered, delivered, ordered_pcs, delivered_pcs, save_path):

    x_type = "date"

    ordered_plot = go.Scatter(x=period, y=ordered, mode='lines', name='ordered',
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5))
    delivered_plot = go.Scatter(x=period, y=delivered, mode='lines', name='delivered',
                    line=dict(color='teal', width=0.1, shape='spline', smoothing = 0.5), fill='tozeroy',fillcolor='teal')
    ordered_pcs_plot = go.Scatter(x=period, y=ordered_pcs, mode='lines', name='ordered',
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5),visible=False)
    delivered_pcs_plot = go.Scatter(x=period, y=delivered_pcs, mode='lines', name='delivered',
                    line=dict(color='teal', width=0.1, shape='spline', smoothing = 0.5), fill='tozeroy',fillcolor='teal',visible=False)

    fig = go.Figure(data=[ordered_plot,delivered_plot,ordered_pcs_plot,delivered_pcs_plot])

    fig.update_layout(
    updatemenus=[
        dict(
            type = "buttons",
            direction = "right",
            active=0,
            buttons=list([
                dict(
                    args=[{"visible": [True, True, False, False], 'yaxis_title': ['sum']}],
                    label="rub",
                    method="update",
                ),
                dict(
                    args=[{"visible": [False, False, True, True], 'yaxis_title': ['pcs']}],
                    label="pcs",
                    method="update",
                )
            ]),
            pad={"r": 1, "t": 0},
            showactive=True,
            x=1,
            y=1.15,
        ),
        dict(
            buttons=list([
                dict(
                    args=[{"line.shape":'spline','smoothing':'0.5'}],
                    label="smooth",
                    method="restyle"
                ),
                dict(
                    args=[{"line.shape":'linear'},],
                    label="line",
                    method="restyle"
                )
            ]),
            type = "buttons",
            direction="right",
            showactive=True,
            x=0.11,
            y=1.15,
        )])
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type=x_type))
    fig.update_layout(title='OZON Statistics')
    fig.write_html(f"{save_path}", auto_open=True)

def __main__():
    start_date = input('Enter start date in format YYYY-MM-DD')
    end_date = input('Enter end date in format YYYY-MM-DD')
    stat_period = input('Enter group by type: {day, week or month}')
    data = get_response(start_date,end_date)
    df = load_preprocess(data)
    period, ordered, delivered, ordered_pcs, delivered_pcs = get_stat(df,stat_period=stat_period)
    print(ordered)
    visualize(period, ordered, delivered, ordered_pcs, delivered_pcs, save_path='ozon_demo.html')

if __name__ == '__main__':
    __main__()

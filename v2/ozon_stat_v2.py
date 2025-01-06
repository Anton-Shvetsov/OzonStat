import requests
import json
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

def get_stat(df):
    start_date = df['created_at_date'].min()
    end_date = df['created_at_date'].max()
    delta = end_date - start_date
    day_ordered = {}
    day_delivered = {}
    day_ordered_pcs = {}
    day_delivered_pcs = {}
    for i in range(delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        df_day_ordered = df[df['created_at_date'] == day]
        df_day_delivered = df_day_ordered[df_day_ordered['status'] == 'delivered']
        day_ordered[day] = df_day_ordered['price'].sum()
        day_delivered[day] = df_day_delivered['price'].sum()
        day_ordered_pcs[day] = len(df_day_ordered['price'])
        day_delivered_pcs[day] = len(df_day_delivered['price'])
    return day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs

def visualize(day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs, save_path):

    ordered = go.Scatter(x=list(day_ordered.keys()), y=list(day_ordered.values()), mode='lines', name='ordered',
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5))
    delivered = go.Scatter(x=list(day_delivered.keys()), y=list(day_delivered.values()), mode='lines', name='delivered',
                    line=dict(color='teal', width=0.1, shape='spline', smoothing = 0.5), fill='tozeroy',fillcolor='teal')
    ordered_pcs = go.Scatter(x=list(day_ordered_pcs.keys()), y=list(day_ordered_pcs.values()), mode='lines', name='ordered',
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5),visible=False)
    delivered_pcs = go.Scatter(x=list(day_delivered_pcs.keys()), y=list(day_delivered_pcs.values()), mode='lines', name='delivered',
                    line=dict(color='teal', width=0.1, shape='spline', smoothing = 0.5), fill='tozeroy',fillcolor='teal',visible=False)

    fig = go.Figure(data=[ordered,delivered,ordered_pcs,delivered_pcs])

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
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
    fig.update_layout(title='OZON Statistics')
    fig.write_html(f"{save_path}", auto_open=True)

def __main__():
    save_path = input('Enter path to save file')
    start_date = input('Enter start date in format YYYY-MM-DD')
    end_date = input('Enter end date in format YYYY-MM-DD')
    data = get_response(start_date,end_date)
    df = load_preprocess(data)
    day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs = get_stat(df)
    visualize(day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs,save_path=f'{save_path}.html')

if __name__ == '__main__':
    __main__()

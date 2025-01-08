import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
import plotly.graph_objects as go
import tkinter as tk
from tkinter import Label, messagebox, Button, Tk, filedialog, ttk
from tkcalendar import Calendar # type: ignore

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
        "to": f"{end_date}T23:59:59.999Z"
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
    if not 'products' in df.keys():
        raise AttributeError('No data for given period')
    df = df.join(df['products'].apply(lambda x: pd.Series(x[0])))
    df['price'] = df['price'].astype(float)
    df['created_at'] = df['created_at'].apply(lambda x: datetime.datetime.strptime(x[:19],'%Y-%m-%dT%H:%M:%S'))
    df['created_at_date'] = df['created_at'].apply(lambda x: x.date())
    products_id = ['All'] + sorted(df.offer_id.unique()) 
    return df, products_id

def get_stat(df, start_date, end_date, stat_period='day', product='All'):
    if product != 'All':
        df = df[df.offer_id == product]
    delta = end_date - start_date 
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

    if stat_period == '7 days':
        weeks = np.array(list(map(lambda x: np.trunc((end_date - x).days / 7), dates)))
        unique_weeks = np.unique(weeks)
        week_ordered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_delivered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_ordered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        week_delivered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        weeks_date = np.zeros_like(unique_weeks,dtype=np.object_)
        for i, week in enumerate(unique_weeks):
            weeks_date[i] = end_date - datetime.timedelta(weeks=week)
            week_ordered[i] = day_ordered[weeks == week].sum()
            week_delivered[i] = day_delivered[weeks == week].sum()
            week_ordered_pcs[i] = day_ordered_pcs[weeks == week].sum()
            week_delivered_pcs[i] = day_delivered_pcs[weeks == week].sum()
        return weeks_date, week_ordered, week_delivered, week_ordered_pcs, week_delivered_pcs
    
    if stat_period == '14 days':
        weeks = np.array(list(map(lambda x: np.trunc((end_date - x).days / 14), dates)))
        unique_weeks = np.unique(weeks)
        week_ordered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_delivered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_ordered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        week_delivered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        weeks_date = np.zeros_like(unique_weeks,dtype=np.object_)
        for i, week in enumerate(unique_weeks):
            weeks_date[i] = end_date - datetime.timedelta(weeks=2*week)
            week_ordered[i] = day_ordered[weeks == week].sum()
            week_delivered[i] = day_delivered[weeks == week].sum()
            week_ordered_pcs[i] = day_ordered_pcs[weeks == week].sum()
            week_delivered_pcs[i] = day_delivered_pcs[weeks == week].sum()
        return weeks_date, week_ordered, week_delivered, week_ordered_pcs, week_delivered_pcs
    
    if stat_period == '28 days':
        weeks = np.array(list(map(lambda x: np.trunc((end_date - x).days / 28), dates)))
        unique_weeks = np.unique(weeks)
        week_ordered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_delivered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_ordered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        week_delivered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        weeks_date = np.zeros_like(unique_weeks,dtype=np.object_)
        for i, week in enumerate(unique_weeks):
            weeks_date[i] = end_date - datetime.timedelta(weeks=4*week)
            week_ordered[i] = day_ordered[weeks == week].sum()
            week_delivered[i] = day_delivered[weeks == week].sum()
            week_ordered_pcs[i] = day_ordered_pcs[weeks == week].sum()
            week_delivered_pcs[i] = day_delivered_pcs[weeks == week].sum()
        return weeks_date, week_ordered, week_delivered, week_ordered_pcs, week_delivered_pcs
    
    if stat_period == 'week':
        weeks = np.array(list(map(lambda x: np.ceil((x - datetime.datetime(min_year,1,1)).days / 7) , dates)))
        unique_weeks = np.unique(weeks)
        week_ordered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_delivered = np.zeros_like(unique_weeks,dtype=np.float32)
        week_ordered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        week_delivered_pcs = np.zeros_like(unique_weeks,dtype=np.int32)
        weeks_date = np.zeros_like(unique_weeks,dtype=np.object_)
        for i, week in enumerate(unique_weeks):
            weeks_date[i] = datetime.date(year=min_year,month=1,day=1) + datetime.timedelta(weeks=week-1,days=6)
            week_ordered[i] = day_ordered[weeks == week].sum()
            week_delivered[i] = day_delivered[weeks == week].sum()
            week_ordered_pcs[i] = day_ordered_pcs[weeks == week].sum()
            week_delivered_pcs[i] = day_delivered_pcs[weeks == week].sum()
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
    

def visualize(period, ordered, delivered, ordered_pcs, delivered_pcs, save_path, product, stat_period):

    x_type = "date"

    ordered_plot = go.Scatter(x=period, y=ordered, name='ordered', 
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5))
    delivered_plot = go.Scatter(x=period, y=delivered, name='delivered',
                    line=dict(color='teal', width=0.1, shape='spline', smoothing = 0.5), fill='tozeroy',fillcolor='teal')
    ordered_pcs_plot = go.Scatter(x=period, y=ordered_pcs, name='ordered',
                    line=dict(color='teal', width=2, dash='solid', shape='spline', smoothing = 0.5),visible=False)
    delivered_pcs_plot = go.Scatter(x=period, y=delivered_pcs, name='delivered',
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
    fig.update_layout(title=f'OZON Statistics {product} {stat_period}')
    fig.write_html(f"{save_path}", auto_open=True)

def preprocess():
    try:
        global df
        global products_id
        global start_date
        global end_date
        global M_products
        start_date_str = L_start_date.cget('text')
        end_date_str = L_end_date.cget('text')
        start_date, end_date = get_dates(start_date_str,end_date_str)
        data = get_response(start_date_str,end_date_str)
        df, products_id = load_preprocess(data)
        V_products = tk.StringVar(top)
        V_products.set('All')
        M_products = tk.OptionMenu(top, V_products, *products_id)
        M_products.grid(row=9, column=1)
        M_products.configure(bg="#0058f7", foreground='white', activebackground='#0058f7', 
                    activeforeground='white',width=10,font='TimesNewRoman 10',state='active')
        M_group_by.configure(state='active')
        B_save_as.configure(state='active')
    except Exception as e:
        messagebox.showinfo("Error",str(e))

def process():
    try:
        global df
        global products_id
        global start_date
        global end_date
        global save_path
        check_path_valid(save_path)
        stat_period = M_group_by.cget('text')
        product = M_products.cget('text')
        period, ordered, delivered, ordered_pcs, delivered_pcs = \
            get_stat(df, start_date, end_date, stat_period=stat_period, product=product)
        visualize(period, ordered, delivered, ordered_pcs, delivered_pcs, save_path=save_path, product=product, stat_period=stat_period)
    except Exception as e:
        messagebox.showinfo("Error",str(e))

def check_path_valid(save_path):
    filename, ext = os.path.splitext(save_path)
    if not filename:
        raise AttributeError('Filename must be indicated')
    if ext != '.html':
        raise AttributeError('File must have an .html extension')
    
def get_dates(start_date,end_date):
    start_date += ' 00:00:00'
    end_date += ' 23:59:59'
    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')
    check_dates_valid(start_date,end_date)
    return start_date, end_date

def check_dates_valid(start_date,end_date):
    
    if start_date >= end_date:
        raise ValueError('Start date must be less then end date')
    period = end_date - start_date
    if period.days > 365:
        raise ValueError('Max period is 365 days')
    
def save_as():
    global save_path
    product = M_products.cget('text')
    start_date_str = L_start_date.cget('text')
    end_date_str = L_end_date.cget('text')
    stat_period = M_group_by.cget('text')
    save_path = filedialog.asksaveasfilename(initialdir = "/",
                                          title = "Save File",
                                          defaultextension=".html",
                                          initialfile=f"Ozon_statistics_{product}_{start_date_str}_{end_date_str}_by_{stat_period}.html",
                                          filetypes = (("HTML files", "*.html"), ('All Files', '*.*')),
                                          confirmoverwrite=True)
    process()

def get_start_date():
    def save_start_date():
        date_old = L_start_date.cget('text')
        date_new = cal.selection_get()
        if str(date_old) != str(date_new):
            L_start_date.configure(text=date_new)
            M_products.configure(state='disabled')
            M_group_by.configure(state='disabled')
            B_save_as.configure(state='disabled')
        root.withdraw()
        root.quit()     
    root = tk.Toplevel(top)
    root.config(background = "#0058f7")
    cal = Calendar(root,font="TimesNewRoman 12", selectmode='day',
                   background='#0058f7', foreground='white',
                   selectbackground='#0058f7', selectforeground='white',
                   headersbackground='#0058f7', headersforeground='white',
                   normalbackground='white', normalforeground='#0058f7',
                   weekendbackground ='white', weekendforeground='#0058f7',
                   othermonthbackground='white', othermonthforeground='white',
                   othermonthwebackground='white', othermonthweforeground='white',
                   bordercolor='#0058f7',tooltipbackground='#0058f7')
    cal.pack(fill="both", expand=True)
    style = ttk.Style()
    style.theme_use('alt')
    style.configure('TButton', background = 'white', foreground = '#0058f7',borderwidth=0,focusthickness=0,focuscolor='none')
    ttk.Button(root, text="Select", command=save_start_date).pack()
    root.mainloop()

def get_end_date():
    def save_end_date():
        date_old = L_end_date.cget('text')
        date_new = cal.selection_get()
        if str(date_old) != str(date_new):
            L_end_date.configure(text=date_new)
            M_products.configure(state='disabled')
            M_group_by.configure(state='disabled')
            B_save_as.configure(state='disabled')
        root.withdraw()
        root.quit()     
    root = tk.Toplevel(top)
    root.config(background = "#0058f7")
    cal = Calendar(root,font="TimesNewRoman 12", selectmode='day',
                   background='#0058f7', foreground='white',
                   selectbackground='#0058f7', selectforeground='white',
                   headersbackground='#0058f7', headersforeground='white',
                   normalbackground='white', normalforeground='#0058f7',
                   weekendbackground ='white', weekendforeground='#0058f7',
                   othermonthbackground='white', othermonthforeground='white',
                   othermonthwebackground='white', othermonthweforeground='white',
                   bordercolor='#0058f7',tooltipbackground='#0058f7')
    cal.pack(fill="both", expand=True)
    style = ttk.Style()
    style.theme_use('alt')
    style.configure('TButton', background = 'white', foreground = '#0058f7',borderwidth=0,focusthickness=0,focuscolor='none')
    ttk.Button(root, text="Select",command=save_end_date).pack()
    root.mainloop()
    

top = Tk()
start_date = None
end_date = None
top.title("OzonStatistics")
top.geometry("600x350")
top.config(background = "#0058f7")

df = None
products_id = ['All']
start_date = None
end_date = None

Label(top, text="",background ='#0058f7').grid(row=0,column=0)

L_start_date = Label(top, text=" Select start date ",background ='#0058f7',fg = "white",font='TimesNewRoman 10')
L_start_date.grid(row=1,column=1)
B_start_date = Button(top, text=" Select start date ", command=get_start_date,
                   background ='#0058f7',foreground='white',
                   activebackground='#0058f7',activeforeground='white',
                   borderwidth=5,font='TimesNewRoman 10',width = 20)
B_start_date.grid(row=1, column=0)

Label(top, text="",background ='#0058f7',width=30).grid(row=2,column=0)

L_end_date = Label(top, text=" Select end date ",background ='#0058f7',fg = "white",font='TimesNewRoman 10')
L_end_date.grid(row=3,column=1)
B_end_date = Button(top, text=" Select end date ", command=get_end_date,
                   background ='#0058f7',foreground='white',
                   activebackground='#0058f7',activeforeground='white',
                   borderwidth=5,font='TimesNewRoman 10',width = 20)
B_end_date.grid(row=3, column=0)

Label(top, text="",background ='#0058f7',width=30).grid(row=4,column=0)

B_get_data = Button(top, text = " Get data ", command = preprocess,
                   background ='#0058f7',foreground='white',
                   activebackground='#0058f7',activeforeground='white',
                   borderwidth=5,font='TimesNewRoman 10',width = 20)
B_get_data.grid(row=5, column=1)

Label(top, text="",background ='#0058f7',width=30).grid(row=6,column=0)

L_group_by = Label(top, text=" Group by ",background ='#0058f7',fg = "white",font='TimesNewRoman 10')
L_group_by.grid(row=7,column=0)
choices = ['day', '7 days', '14 days', '28 days', 'week', 'month']
V_group_by = tk.StringVar(top)
V_group_by.set('day')
M_group_by = tk.OptionMenu(top, V_group_by, *choices)
M_group_by.configure(bg="#0058f7", foreground='white', activebackground='#0058f7', 
            activeforeground='white',width=10,font='TimesNewRoman 10',state='disabled')
M_group_by.grid(row=7, column=1)

Label(top, text="",background ='#0058f7',width=30).grid(row=8,column=0)

L_products = Label(top, text=" Products id ",background ='#0058f7',fg = "white",font='TimesNewRoman 10')
L_products.grid(row=9,column=0)
V_products = tk.StringVar(top)
V_products.set('All')
M_products = tk.OptionMenu(top, V_products, *products_id)
M_products.grid(row=9, column=1)
M_products.configure(bg="#0058f7", foreground='white', activebackground='#0058f7', 
            activeforeground='white',width=10,font='TimesNewRoman 10',state='disabled')

Label(top, text="",background ='#0058f7',width=30).grid(row=10,column=0)

L_save_as = Label(top, text = "Filename", width = 50, fg = "white", background ='#0058f7',font='TimesNewRoman 10')
L_save_as.grid(row=13, column=1)
B_save_as = Button(top, text = "Save as", command=save_as,
                   background ='#0058f7',foreground='white',
                   activebackground='#0058f7',activeforeground='white',
                   borderwidth=5,font='TimesNewRoman 10',width = 20,
                   state='disabled')
B_save_as.grid(row=11, column=1)

top.mainloop()
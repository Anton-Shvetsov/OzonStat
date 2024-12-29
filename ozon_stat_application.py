import os
import pandas as pd
import datetime
import plotly.graph_objects as go
from tkinter import Entry, Label, messagebox, Button, Tk, filedialog

def load_preprocess(filename):
    df = pd.read_csv(filename, sep=';')
    df['Принят в обработку'] = df['Принят в обработку'].apply(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))
    df['Принят в обработку - дата'] = df['Принят в обработку'].apply(lambda x: x.date())
    return df

def get_stat(df,start_date=None,end_date=None):
    if start_date is None:
        start_date = df['Принят в обработку - дата'].min()
    if end_date is None:
        end_date = df['Принят в обработку - дата'].max()
    delta = end_date - start_date
    day_ordered = {}
    day_delivered = {}
    day_ordered_pcs = {}
    day_delivered_pcs = {}
    for i in range(delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        df_day_ordered = df[df['Принят в обработку - дата'] == day]
        df_day_delivered = df_day_ordered[df_day_ordered['Статус'] == 'Доставлен']
        day_ordered[day] = df_day_ordered['Итоговая стоимость товара'].sum()
        day_delivered[day] = df_day_delivered['Итоговая стоимость товара'].sum()
        day_ordered_pcs[day] = len(df_day_ordered['Итоговая стоимость товара'])
        day_delivered_pcs[day] = len(df_day_delivered['Итоговая стоимость товара'])
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

def process():
    try:
        document_path = str(L_document_path.cget('text'))
        save_path = str(Entry.get(E_video_path))

        df = load_preprocess(document_path)
        day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs = get_stat(df)
        visualize(day_ordered, day_delivered, day_ordered_pcs, day_delivered_pcs, save_path=save_path)
 
    except Exception as e:
        messagebox.showinfo("Error",str(e))
    
def browse_file():
    document_path = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.csv*"),
                                                       ("all files",
                                                        "*.*")))
    L_document_path.configure(text=document_path)
    filename, _ = os.path.splitext(document_path)
    E_video_path.delete(0,'end')
    E_video_path.insert(0, filename+'.html')

top = Tk()
top.title("OzonStatistics")
top.geometry("700x150")
top.config(background = "teal")

Label(top, text="",background ='teal').grid(row=0,column=0)

L_document_path = Label(top, text = "Select csv file", width = 50, fg = "white", background ='teal')
L_document_path.grid(row=1, column=0)
B_Browse_file = Button(top, text = "Browse File", command = browse_file, background ='white')
B_Browse_file.grid(row=1, column=1)
Label(top, text="",background ='teal',).grid(row=2,column=0)

L_video_path = Label(top, text=" (Optional) path to save plot ",background ='teal',fg = "white")
L_video_path.grid(row=3,column=0)
E_video_path = Entry(top, bd=5, width=50, justify='center',background ='white')
E_video_path.grid(row=3,column=1)
E_video_path.insert(0, 'Select csv file first')
Label(top, text="",background ='teal').grid(row=4,column=0)

B_create_video = Button(top, text = "Create plot", command = process, background ='white')
B_create_video.grid(row=19, column=1)

top.mainloop()
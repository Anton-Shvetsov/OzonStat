import os
import pandas as pd
import datetime
import plotly.graph_objects as go
from tkinter import Entry, Label, messagebox, Button, Tk, filedialog
from ozon_stat import load_preprocess, get_stat, visualize


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
                                          filetypes = (("CSV files",
                                                        "*.csv*"),
                                                        ("XLSX files",
                                                         "*.xlsx*"),
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
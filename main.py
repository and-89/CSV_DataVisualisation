import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

plt.style.use('dark_background')

def load_csv():
    file_path = filedialog.askopenfilename()
    try:
        global data
        data = pd.read_csv(file_path, sep=';')
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        update_column_listbox()
    except Exception as e:
        messagebox.showerror("Error Loading File", e)

def update_column_listbox():
    column_listbox.delete(0, tk.END)
    for column in data.columns:
        if column != 'Timestamp':
            column_listbox.insert(tk.END, column)

def plot_selected_columns():
    selected_indices = column_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("No Selection", "Please select at least one column.")
        return
    selected_columns = [column_listbox.get(i) for i in selected_indices]

    ref_lines = []
    if ref_line_var.get():
        try:
            ref_lines.append(float(ref_line_entry.get()))
        except ValueError:
            messagebox.showerror("Invalid Reference Line Value", "Please enter a valid number for the first reference line.")
            return
    if second_ref_line_var.get():
        try:
            ref_lines.append(float(second_ref_line_entry.get()))
        except ValueError:
            messagebox.showerror("Invalid Second Reference Line Value", "Please enter a valid number for the second reference line.")
            return

    try:
        fig, ax = plt.subplots()
        ax.set_xlabel('Time')
        ax.set_title('Ethereum Data Visualization')

        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        axes = [ax]

        for i, column in enumerate(selected_columns):
            if separate_scales_var.get() and i > 0:  # Create separate Y axes
                ax_new = ax.twinx()
                ax_new.spines["right"].set_position(("outward", 60*i))
                axes.append(ax_new)
            else:
                ax_new = axes[0]
            ax_new.plot(data['Timestamp'], data[column], label=column, color=color_cycle[i % len(color_cycle)])
            ax_new.set_ylabel(column, color=color_cycle[i % len(color_cycle)])
            ax_new.tick_params(axis='y', labelcolor=color_cycle[i % len(color_cycle)])

        for i, ref_line_value in enumerate(ref_lines):
            axes[0].axhline(y=ref_line_value, color='r' if i == 0 else 'g', linestyle='--', label=f'Reference Line {i+1}: {ref_line_value}')

        handles, labels = [], []
        for ax in axes:
            for handle, label in zip(*ax.get_legend_handles_labels()):
                handles.append(handle)
                labels.append(label)
        axes[0].legend(handles, labels, loc='upper left')

        fig.tight_layout()

        # Clear any existing widgets in the plot frame
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Create the canvas and add the plot to the window
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        messagebox.showerror("Error Generating Plot", e)

bg_color = '#2e2e2e'
fg_color = '#ffffff'
button_color = '#5e5e5e'
entry_bg = '#4d4d4d'
entry_fg = '#ffffff'

window = tk.Tk()
window.title("CSV Data Visualization")
window.geometry('800x600')
window.configure(bg=bg_color)

load_button = tk.Button(window, text="Load CSV File", command=load_csv, bg=button_color, fg=fg_color)
load_button.grid(row=0, column=0, sticky='ew', columnspan=6)

column_listbox = tk.Listbox(window, selectmode='multiple', exportselection=0, height=6, bg=entry_bg, fg=entry_fg)
column_listbox.grid(row=1, column=0, sticky='ewns', columnspan=6)

scrollbar = ttk.Scrollbar(window, orient='vertical', command=column_listbox.yview)
scrollbar.grid(row=1, column=6, sticky='ns')
column_listbox.config(yscrollcommand=scrollbar.set)

ref_line_var = tk.BooleanVar()
ref_line_checkbutton = tk.Checkbutton(window, text="Reference Line 1", variable=ref_line_var, bg=bg_color, fg=fg_color, selectcolor=entry_bg)
ref_line_checkbutton.grid(row=2, column=0, sticky='w')
ref_line_entry = tk.Entry(window, bg=entry_bg, fg=entry_fg)
ref_line_entry.grid(row=2, column=1, sticky='we')

second_ref_line_var = tk.BooleanVar()
second_ref_line_checkbutton = tk.Checkbutton(window, text="Reference Line 2", variable=second_ref_line_var, bg=bg_color, fg=fg_color, selectcolor=entry_bg)
second_ref_line_checkbutton.grid(row=2, column=2, sticky='w')
second_ref_line_entry = tk.Entry(window, bg=entry_bg, fg=entry_fg)
second_ref_line_entry.grid(row=2, column=3, sticky='we')

separate_scales_var = tk.BooleanVar()
separate_scales_checkbutton = tk.Checkbutton(window, text="Separate Scales", variable=separate_scales_var, bg=bg_color, fg=fg_color, selectcolor=entry_bg)
separate_scales_checkbutton.grid(row=3, column=0, sticky='w')

plot_button = tk.Button(window, text="Generate Plot", command=plot_selected_columns, bg=button_color, fg=fg_color)
plot_button.grid(row=3, column=4, sticky='ew')

plot_frame = tk.Frame(window)
plot_frame.grid(row=4, column=0, columnspan=7, sticky='nsew')

window.grid_rowconfigure(4, weight=1)
window.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)

window.mainloop()
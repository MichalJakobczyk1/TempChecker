import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CSVViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Temperature Checker")
        self.draw_layout()

    def draw_layout(self):
        frame = ttk.Frame(self.master, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        load_button = ttk.Button(frame, text="Load CSV", command=self.load_csv)
        load_button.grid(row=0, column=0, pady=10, padx=(0, 10))

        self.rows_entry = ttk.Entry(frame)
        self.rows_entry.insert(0, "10")
        self.rows_entry.grid(row=0, column=1, pady=10)

        city_label = ttk.Label(frame, text="City:")
        city_label.grid(row=0, column=2, padx=(10, 0))

        self.city_entry = ttk.Combobox(frame, state="readonly", width=15)
        self.city_entry.grid(row=0, column=3, pady=10)

        country_label = ttk.Label(frame, text="Country:")
        country_label.grid(row=0, column=4, padx=(10, 0))

        self.country_combobox = ttk.Combobox(frame, values=[], state="readonly", postcommand=self.update_cities, width=15)
        self.country_combobox.grid(row=0, column=5, pady=10)
        self.country_combobox.bind("<<ComboboxSelected>>", self.reset_cities)

        display_button = ttk.Button(frame, text="Display", command=self.display_rows)
        display_button.grid(row=0, column=6, pady=10)

        sort_asc_button = ttk.Button(frame, text="Sort Ascending", command=lambda: self.sort_table("AverageTemperature"))
        sort_asc_button.grid(row=0, column=7, pady=10)

        sort_desc_button = ttk.Button(frame, text="Sort Descending", command=lambda: self.sort_table("AverageTemperature", ascending=False))
        sort_desc_button.grid(row=0, column=8, pady=10)

        plot_button = ttk.Button(frame, text="Plot Data", command=self.plot_data)
        plot_button.grid(row=0, column=9, pady=10)

        self.data_treeview = ttk.Treeview(frame, columns=("dt", "AverageTemperature", "AverageTemperatureUncertainty", "City", "Country", "Latitude", "Longitude"), show="headings", height=10)
        self.data_treeview.grid(row=1, column=0, rowspan=3, padx=(0, 10), pady=(0, 10))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.data_treeview.yview)
        scrollbar.grid(row=1, column=1, rowspan=3, sticky=(tk.N, tk.S), pady=(0, 10))
        self.data_treeview.configure(yscrollcommand=scrollbar.set)

        # Frame dla wykresu
        plot_frame = ttk.Frame(self.master, padding="20")
        plot_frame.grid(row=1, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Wykres
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def load_csv(self):
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.load_countries()

    def load_countries(self):
        if hasattr(self, 'file_path'):
            df = pd.read_csv(self.file_path)
            cities = df["City"].unique()
            countries = df["Country"].unique()
            self.city_entry['values'] = tuple(sorted(cities))
            self.country_combobox['values'] = tuple(sorted(countries))

    def update_cities(self):
        selected_country = self.country_combobox.get()
        if hasattr(self, 'file_path') and selected_country:
            df = pd.read_csv(self.file_path)
            cities = df[df["Country"] == selected_country]["City"].unique()
            self.city_entry['values'] = tuple(sorted(cities))
        else:
            self.city_entry.set("")

    def reset_cities(self, event):
        self.city_entry.set("")

    def display_rows(self):
        try:
            rows_to_display = int(self.rows_entry.get())
        except ValueError:
            rows_to_display = 10

        if hasattr(self, 'file_path'):
            df = pd.read_csv(self.file_path)
            df["AverageTemperature"] = df["AverageTemperature"].round(2)
            df["AverageTemperatureUncertainty"] = df["AverageTemperatureUncertainty"].round(2)

            # Konwertuj kolumnę "dt" na datę
            df["dt"] = pd.to_datetime(df["dt"])

            # Filtruj dane od roku 2000 w górę
            df = df[df["dt"].dt.year >= 2000]

            city_filter = self.city_entry.get()
            country_filter = self.country_combobox.get()

            if city_filter:
                df = df[df["City"].str.contains(city_filter, case=False, na=False)]
            if country_filter:
                df = df[df["Country"] == country_filter]

            df = df.head(rows_to_display)
            self.draw_table(df)
            self.update_cities()

    def draw_table(self, df):
        columns = ["dt", "AverageTemperature", "AverageTemperatureUncertainty", "City", "Country", "Latitude", "Longitude"]

        self.data_treeview.delete(*self.data_treeview.get_children())

        for index, row in df.iterrows():
            values = [row[category] for category in columns]
            self.data_treeview.insert("", tk.END, values=values)

    def sort_table(self, column, ascending=True):
        if hasattr(self, 'file_path'):
            current_rows = self.data_treeview.get_children()
            df = pd.read_csv(self.file_path, nrows=len(current_rows))
            df["AverageTemperature"] = df["AverageTemperature"].round(2)
            df["AverageTemperatureUncertainty"] = df["AverageTemperatureUncertainty"].round(2)
            df.sort_values(by=column, ascending=ascending, inplace=True)
            self.draw_table(df)

    def plot_data(self):
        if hasattr(self, 'file_path'):
            current_rows = self.data_treeview.get_children()
            df = pd.read_csv(self.file_path, nrows=len(current_rows))
            df["AverageTemperature"] = df["AverageTemperature"].round(2)
            df["AverageTemperatureUncertainty"] = df["AverageTemperatureUncertainty"].round(2)

            # Wyczyszczenie poprzednich danych na wykresie
            self.ax.clear()

            # Tworzenie nowego wykresu bez oznaczeń na osi X
            self.ax.plot(df["dt"], df["AverageTemperature"], marker='o', linestyle='-', color='b')
            self.ax.set_title("Average Temperature Over Time")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Average Temperature")

            # Zaktualizowanie wykresu
            self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
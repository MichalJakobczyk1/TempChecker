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
        self.master.geometry("1600x1400")  
        self.draw_layout()

    def draw_layout(self):
        # Function to draw the main layout of the application
        frame = ttk.Frame(self.master, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Button to load CSV file
        load_button = ttk.Button(frame, text="Load CSV", command=self.load_csv)
        load_button.grid(row=0, column=0, pady=10, padx=(0, 10))

        # Entry for specifying the number of rows to display
        self.rows_entry = ttk.Entry(frame)
        self.rows_entry.insert(0, "10")
        self.rows_entry.grid(row=0, column=1, pady=10)

        # Label and Combobox for selecting the year
        year_label = ttk.Label(frame, text="Year:")
        year_label.grid(row=0, column=2, padx=(10, 0))
        self.year_combobox = ttk.Combobox(frame, state="readonly", values=[], width=10)
        self.year_combobox.grid(row=0, column=3, pady=10)

        # Label and Combobox for selecting the city
        city_label = ttk.Label(frame, text="City:")
        city_label.grid(row=0, column=4, padx=(10, 0))
        self.city_combobox = ttk.Combobox(frame, state="readonly", values=[], width=15)
        self.city_combobox.grid(row=0, column=5, pady=10)

        # Label and Combobox for selecting the country
        country_label = ttk.Label(frame, text="Country:")
        country_label.grid(row=0, column=6, padx=(10, 0))
        self.country_combobox = ttk.Combobox(frame, values=[], state="readonly", postcommand=self.update_years, width=10)
        self.country_combobox.grid(row=0, column=7, pady=10)
        self.country_combobox.bind("<<ComboboxSelected>>", self.reset_years)

        # Button to display the selected data
        display_button = ttk.Button(frame, text="Display", command=self.display_rows)
        display_button.grid(row=0, column=8, pady=10)

        # Buttons for sorting data
        sort_asc_button = ttk.Button(frame, text="Sort Ascending", command=lambda: self.sort_table("AverageTemperature"))
        sort_asc_button.grid(row=0, column=9, pady=10)
        sort_desc_button = ttk.Button(frame, text="Sort Descending", command=lambda: self.sort_table("AverageTemperature", ascending=False))
        sort_desc_button.grid(row=0, column=10, pady=10)

        # Button to plot data
        plot_button = ttk.Button(frame, text="Plot Data", command=self.plot_data)
        plot_button.grid(row=0, column=11, pady=10)

        # Treeview widget for displaying data
        self.data_treeview = ttk.Treeview(frame, columns=("dt", "AverageTemperature", "City", "Country"), show="headings", height=10)
        self.data_treeview.grid(row=1, column=0, rowspan=3, padx=(0, 10), pady=(0, 10))

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.data_treeview.yview)
        scrollbar.grid(row=1, column=1, rowspan=3, sticky=(tk.N, tk.S), pady=(0, 10))
        self.data_treeview.configure(yscrollcommand=scrollbar.set)

        # Frame for the plot
        plot_frame = ttk.Frame(self.master, padding="20")
        plot_frame.grid(row=1, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Matplotlib figure and canvas for the plot
        self.fig, self.ax = plt.subplots(figsize=(3.5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_years(self):
        # Function to update the available years based on the selected country
        if hasattr(self, 'file_path') and self.country_combobox.get():
            df = pd.read_csv(self.file_path)
            selected_country = self.country_combobox.get()
            df_country = df[df["Country"] == selected_country]
            years = sorted(df_country["dt"].dt.year.unique(), reverse=True)
            self.year_combobox['values'] = tuple(map(str, years))

    def reset_years(self, event):
        # Function to reset the available years and update cities
        self.update_cities()
        self.update_years()

    def update_cities(self):
        # Function to update the available cities based on the selected country
        if hasattr(self, 'file_path') and self.country_combobox.get():
            df = pd.read_csv(self.file_path)
            selected_country = self.country_combobox.get()
            cities = df[df["Country"] == selected_country]["City"].unique()
            self.city_combobox['values'] = tuple(sorted(cities))

    def reset_cities(self, event):
        # Function to reset the available cities
        self.update_cities()

    def load_csv(self):
        # Function to load a CSV file and update the list of countries
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.update_countries()

    def update_countries(self):
        # Function to update the list of available countries
        if hasattr(self, 'file_path'):
            df = pd.read_csv(self.file_path)
            countries = df["Country"].unique()
            self.country_combobox['values'] = tuple(sorted(countries))

    def display_rows(self):
        # Function to display selected rows of data in the Treeview
        try:
            rows_to_display = int(self.rows_entry.get())
        except ValueError:
            rows_to_display = 10

        if hasattr(self, 'file_path'):
            df = pd.read_csv(self.file_path)
            selected_year = int(self.year_combobox.get()) if self.year_combobox.get() else None
            selected_city = self.city_combobox.get() if self.city_combobox.get() else None
            selected_country = self.country_combobox.get() if self.country_combobox.get() else None

            if selected_year:
                df = df[df["dt"].dt.year == selected_year]
            if selected_city:
                df = df[df["City"] == selected_city]
            if selected_country:
                df = df[df["Country"] == selected_country]

            self.draw_table(df.head(rows_to_display))

    def draw_table(self, df):
        # Function to draw the data in the Treeview
        columns = ["dt", "AverageTemperature", "City", "Country"]

        self.data_treeview.delete(*self.data_treeview.get_children())

        for index, row in df.iterrows():
            values = [round(row[category], 2) if category == "AverageTemperature" else row[category] for category in columns]
            self.data_treeview.insert("", tk.END, values=values)

    def sort_table(self, column, ascending=True):
        # Function to sort the data based on a selected column
        if hasattr(self, 'file_path'):
            current_rows = self.data_treeview.get_children()
            df = pd.read_csv(self.file_path)
            selected_year = int(self.year_combobox.get()) if self.year_combobox.get() else None
            selected_city = self.city_combobox.get() if self.city_combobox.get() else None
            selected_country = self.country_combobox.get() if self.country_combobox.get() else None

            if selected_year:
                df = df[df["dt"].dt.year == selected_year]
            if selected_city:
                df = df[df["City"] == selected_city]
            if selected_country:
                df = df[df["Country"] == selected_country]

            df.sort_values(by=column, ascending=ascending, inplace=True)
            self.draw_table(df.head(len(current_rows)))

    def plot_data(self):
        # Function to plot the selected data
        if hasattr(self, 'file_path'):
            current_rows = self.data_treeview.get_children()
            df = pd.read_csv(self.file_path)
            selected_year = int(self.year_combobox.get()) if self.year_combobox.get() else None
            selected_city = self.city_combobox.get() if self.city_combobox.get() else None
            selected_country = self.country_combobox.get() if self.country_combobox.get() else None

            if selected_year:
                df = df[df["dt"].dt.year == selected_year]
            if selected_city:
                df = df[df["City"] == selected_city]
            if selected_country:
                df = df[df["Country"] == selected_country]

            self.ax.clear()

            self.ax.plot(df["dt"][:len(current_rows)], df["AverageTemperature"][:len(current_rows)], marker='o', linestyle='-', color='b')
            self.ax.set_title("Average Temperature Over Time")
            self.ax.set_xlabel("Date")
            self.ax.set_ylabel("Average Temperature")
            self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
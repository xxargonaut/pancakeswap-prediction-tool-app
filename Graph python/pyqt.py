import sys
import psycopg2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import QTimer
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd

# Database connection parameters
db_params = {
    'dbname': 'bcsscandata',
    'user': 'postgres',
    'password': '12345678',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the database and retrieve data
connection = psycopg2.connect(**db_params)

def get_answer_data(connection):
    with connection.cursor() as cursor:
        query = "SELECT startedAt FROM Answer ORDER BY startedAt ASC;"
        cursor.execute(query)
        return cursor.fetchall()

def get_epoch_data_to_update(connection, start_time, end_time):
    with connection.cursor() as cursor:
        query = "SELECT lockTimestamp, lockPrice, closePrice FROM Epoch WHERE lockTimestamp >= %s AND lockTimestamp < %s ORDER BY epoch ASC;"
        cursor.execute(query, (int(start_time.timestamp()) - 20, int(end_time.timestamp()) + 20))
        return cursor.fetchall()

def get_epoch_rsi_data(connection, end_time, length):
    with connection.cursor() as cursor:
        query = "SELECT lockTimestamp, lockPrice, closePrice FROM Epoch WHERE lockTimestamp < %s ORDER BY lockTimestamp DESC LIMIT %s;"
        cursor.execute(query, (int(end_time.timestamp()) + 20, length))
        results = cursor.fetchall()

    sorted_results = sorted(results, key=lambda x: x[0])
    return sorted_results
    
def get_answer_data_to_update(connection, start_time, end_time):
    with connection.cursor() as cursor:
        query = "SELECT answer, startedAt FROM Answer WHERE startedAt >= %s AND startedAt < %s ORDER BY roundId ASC;"
        cursor.execute(query, (int(start_time.timestamp()) - 20, int(end_time.timestamp()) + 20))
        return cursor.fetchall()

def get_answer_rsi_data(connection, end_time, length):
    with connection.cursor() as cursor:
        query = "SELECT answer, startedAt FROM Answer WHERE startedAt < %s ORDER BY startedAt DESC LIMIT %s;"
        cursor.execute(query, (int(end_time.timestamp()) + 20, length))
        results = cursor.fetchall()

    sorted_results = sorted(results, key=lambda x: x[1])
    return sorted_results
    
answer_x_data = get_answer_data(connection)
connection.close()

# Extract data for plotting and convert timestamps to datetime objects
answer_x_flag = [datetime.fromtimestamp(row[0]) for row in answer_x_data]
last_answer_time = datetime.fromtimestamp(answer_x_data[-1][0])
start_time = end_time = last_answer_time

class GraphWidget(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        super().__init__(self.fig)
        self.interval = 30  # Initial interval set to 30 minutes
        self.period = 20  # Initial period set to 20

        # Calculate total pages and start from the last page
        total_minutes = (answer_x_flag[-1] - answer_x_flag[0]).total_seconds() / 60
        self.total_pages = int(total_minutes // self.interval)
        self.current_page = self.total_pages  # Start from the last page

# ---------------------------------------------------
        self.epoch_enabled = True
        self.epoch_ema_enabled = False
        self.epoch_sma_enabled = False
        self.epoch_rsi_enabled = False

        self.answer_enabled = True
        self.answer_ema_enabled = False
        self.answer_sma_enabled = False
        self.answer_rsi_enabled = False
# ####################################################

        self.plot_page(self.current_page)

    def plot_page(self, page):
        self.ax.clear()  # Clear the figure before plotting a new page

        # Calculate start and end times for the current page
        start_time = last_answer_time - timedelta(minutes=(self.total_pages - page + 1) * self.interval)
        end_time = start_time + timedelta(minutes=self.interval)

        connection = psycopg2.connect(**db_params)
        epoch_data = get_epoch_data_to_update(connection, start_time, end_time)
        answer_data = get_answer_data_to_update(connection, start_time, end_time)
        connection.close()

        epoch_x = epoch_y = []
        epoch_x = [datetime.fromtimestamp(row[0]) for row in epoch_data]  # Convert epoch to datetime
        epoch_y = [round(row[1] / (10 ** 8), 2) for row in epoch_data]
            
        answer_x = [datetime.fromtimestamp(row[1]) for row in answer_data]  # Convert answer to datetime
        answer_y = [round(row[0] / (10 ** 8), 2) for row in answer_data]
        
        if page == self.total_pages:
            epoch_x.append(datetime.fromtimestamp(epoch_data[-1][0] + 306))
            epoch_y.append(round(epoch_data[-1][2] / (10 ** 8), 2))

            self.ax.vlines(x=datetime.fromtimestamp(epoch_data[-1][0] + 306 * 2 - 30), ymin=min(answer_y), ymax=max(answer_y), color='r', linestyle='-.', linewidth=1)
            self.ax.hlines(y=answer_y[-1], xmin=answer_x[-1], xmax=datetime.fromtimestamp(epoch_data[-1][0] + 306 * 3), color='r', linestyle=':', linewidth=1)
            self.ax.axvline(x=datetime.fromtimestamp(epoch_data[-1][0] + 306 * 2), color='r', linestyle=':', linewidth=1)
            self.ax.plot(datetime.fromtimestamp(epoch_data[-1][0] + 306 * 2), answer_y[-1], marker='o', color='red', markersize=3)
            self.ax.axvline(x=datetime.fromtimestamp(epoch_data[-1][0] + 306 * 3), color='g', linestyle='-', linewidth=1, label='Prediction Line')

        # Plot the data within the current time interval
        if self.epoch_enabled:
            self.ax.plot(epoch_x, epoch_y, marker='o', linestyle='-', color='g', markersize=6, linewidth=1, label='Epoch Data')
        if self.answer_enabled:
            self.ax.plot(answer_x, answer_y, marker='.', linestyle='-', color='b', markersize=6, linewidth=1, label='Answer Data')

# ---------------------------------------------------
        # Setting Epoch_Data if enabled
        if self.epoch_ema_enabled or self.epoch_sma_enabled or self.epoch_rsi_enabled:
            connection = psycopg2.connect(**db_params)
            epoch_rsi_data = get_epoch_rsi_data(connection, end_time, len(epoch_data) + 30)
            connection.close()
            epoch_rsi_data_x = [datetime.fromtimestamp(row[0]) for row in epoch_rsi_data]  # Convert epoch to datetime
            epoch_rsi_data_y = [round(row[1] / (10 ** 8), 2) for row in epoch_rsi_data]
            epoch_rsi_data_x.append(datetime.fromtimestamp(epoch_rsi_data[-1][0] + 306))
            epoch_rsi_data_y.append(round(epoch_rsi_data[-1][2] / (10 ** 8), 2))
            epoch_data_series = pd.Series(epoch_rsi_data_y)

        # Plot Epoch_EMA if enabled
        if self.epoch_ema_enabled:
            epoch_ema = epoch_data_series.ewm(span=self.period, adjust=False).mean()  # Epoch_EMA with a span of 20
            self.ax.plot(epoch_rsi_data_x[-(len(epoch_data) + 1):], epoch_ema[-(len(epoch_data) + 1):], color='g', linestyle='-', linewidth=1, label='Epoch_EMA (' + str(self.period) + ')')
        # Plot Epoch_SMA if enabled
        if self.epoch_sma_enabled:
            epoch_sma = epoch_data_series.rolling(window=self.period).mean()  # SMA with a window of 20
            self.ax.plot(epoch_rsi_data_x[-(len(epoch_data) + 1):], epoch_sma[-(len(epoch_data) + 1):], color='b', linestyle='-', linewidth=1, label='Epoch_SMA (' + str(self.period) + ')')
        # Plot Epoch_RSI if enabled
        if self.epoch_rsi_enabled:
            epoch_rsi = self.calculate_stoch_rsi(epoch_rsi_data_y)
            if epoch_rsi is not None:
                generated_epoch_rsi = self.generator_stoch_rsi(epoch_rsi, epoch_rsi_data_y)
                # Use the same x-axis and overlay Stochastic RSI on the primary y-axis
                self.ax.plot(epoch_rsi_data_x[-(len(epoch_data) + 1):], generated_epoch_rsi[-(len(epoch_data) + 1):], color='r', linestyle='-', linewidth=1, label='Epoch_RSI', alpha=0.7)
                self.ax.hlines(y=max(generated_epoch_rsi[-(len(epoch_data) + 1):]), xmin=epoch_rsi_data_x[-(len(epoch_data) + 1)], xmax=epoch_rsi_data_x[-1], color='r', linestyle=':', linewidth=1, alpha=0.7)
                self.ax.hlines(y=min(generated_epoch_rsi[-(len(epoch_data) + 1):]), xmin=epoch_rsi_data_x[-(len(epoch_data) + 1)], xmax=epoch_rsi_data_x[-1], color='r', linestyle=':', linewidth=1, alpha=0.7)

        # Setting Answer_Data if enabled
        if self.answer_ema_enabled or self.answer_sma_enabled or self.answer_rsi_enabled:
            connection = psycopg2.connect(**db_params)
            answer_rsi_data = get_answer_rsi_data(connection, end_time, len(answer_data) + 30)
            connection.close()
            answer_rsi_data_x = [datetime.fromtimestamp(row[1]) for row in answer_rsi_data]  # Convert answer to datetime
            answer_rsi_data_y = [round(row[0] / (10 ** 8), 2) for row in answer_rsi_data]
            answer_data_series = pd.Series(answer_rsi_data_y)
        # Plot Answer_EMA if enabled
        if self.answer_ema_enabled:
            answer_ema = answer_data_series.ewm(span=self.period, adjust=False).mean()  # Answer_EMA with a span of 20
            self.ax.plot(answer_rsi_data_x[-(len(answer_data) + 1):], answer_ema[-(len(answer_data) + 1):], color='g', linestyle='-', linewidth=1, label='Answer_EMA (' + str(self.period) + ')')
        # Plot Answer_SMA if enabled
        if self.answer_sma_enabled:
            answer_sma = answer_data_series.rolling(window=self.period).mean()  # Answer_SMA with a window of 20
            self.ax.plot(answer_rsi_data_x[-(len(answer_data) + 1):], answer_sma[-(len(answer_data) + 1):], color='b', linestyle='-', linewidth=1, label='Answer_SMA (' + str(self.period) + ')')
        # Plot Answer_RSI if enabled
        if self.answer_rsi_enabled:
            answer_rsi = self.calculate_stoch_rsi(answer_rsi_data_y)
            if answer_rsi is not None:
                generated_answer_rsi = self.generator_stoch_rsi(answer_rsi, answer_rsi_data_y)
                # Use the same x-axis and overlay Stochastic RSI on the primary y-axis
                self.ax.plot(answer_rsi_data_x[-(len(answer_data) + 1):], generated_answer_rsi[-(len(answer_data) + 1):], color='r', linestyle='-', linewidth=1, label='Answer_RSI', alpha=0.7)
                self.ax.hlines(y=max(generated_answer_rsi[-(len(answer_data) + 1):]), xmin=answer_rsi_data_x[-(len(answer_data) + 1)], xmax=answer_rsi_data_x[-1], color='r', linestyle=':', linewidth=1, alpha=0.7)
                self.ax.hlines(y=min(generated_answer_rsi[-(len(answer_data) + 1):]), xmin=answer_rsi_data_x[-(len(answer_data) + 1)], xmax=answer_rsi_data_x[-1], color='r', linestyle=':', linewidth=1, alpha=0.7)
# ####################################################

        # Set date format for x-axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m:%d-%H:%M'))

        # Add labels and title
        self.ax.set_xlabel('Timestamp')
        self.ax.set_ylabel('Value')
        self.ax.set_title(f'Combined Plot of Epoch Data and Answer Data (Page {page + 1})')
        self.ax.legend()
        self.ax.grid(visible=True, linestyle='--', alpha=0.5)
        plt.setp(self.ax.get_xticklabels(), rotation=25)  # Rotate x-axis labels for better readability
        self.draw()  # Draw the updated plot

# ---------------------------------------------------
    def calculate_stoch_rsi(self, data, window=14):
        if len(data) < window:
            return None

        # Convert data to pandas Series for calculations
        data_series = pd.Series(data)

        # Calculate RSI
        delta = data_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Calculate Stochastic RSI
        stoch_rsi = ((rsi - rsi.rolling(window=window).min()) /
                     (rsi.rolling(window=window).max() - rsi.rolling(window=window).min()))

        return stoch_rsi.dropna().values  # Drop NaN values and return
    def generator_stoch_rsi(self, data_rsi, data_y):
        height = float(max(data_y[30:]) - min(data_y[30:]))
        stoch_rsi = [float(row)*height/5 + float(min(data_y[30:])) - height*6/25 for row in data_rsi]
        return stoch_rsi
# ####################################################

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.plot_page(self.current_page)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.plot_page(self.current_page)

    def update_interval(self, interval):
        try:
            self.interval = int(interval)

            # Recalculate total pages and reset to the last page
            total_minutes = (answer_x_flag[-1] - answer_x_flag[0]).total_seconds() / 60
            self.total_pages = int(total_minutes // self.interval)
            self.current_page = self.total_pages

            self.plot_page(self.current_page)
        except ValueError:
            print("Please enter a valid integer for the interval.")

    def update_period(self, period):
        try:
            self.period = int(period)
            self.plot_page(self.current_page)
        except ValueError:
            print("Please enter a valid integer for the period.")

    def update_data(self):
        """Fetch the latest data from the database and re-plot the current page."""
        # Re-fetch the answer data to update answer_x_flag
        connection = psycopg2.connect(**db_params)
        answer_x_data = get_answer_data(connection)
        connection.close()
        
        # Update answer_x_flag and last_answer_time
        global answer_x_flag, last_answer_time
        answer_x_flag = [datetime.fromtimestamp(row[0]) for row in answer_x_data]
        last_answer_time = datetime.fromtimestamp(answer_x_data[-1][0])

        # Recalculate total pages based on updated data and interval
        total_minutes = (answer_x_flag[-1] - answer_x_flag[0]).total_seconds() / 60
        self.total_pages = int(total_minutes // self.interval)

        # Re-plot the current page with the updated data
        self.plot_page(self.current_page)

# ---------------------------------------------------
    def set_epoch_enabled(self, enabled):
        self.epoch_enabled = enabled
        self.plot_page(self.current_page)

    def set_epoch_ema_enabled(self, enabled):
        self.epoch_ema_enabled = enabled
        self.plot_page(self.current_page)

    def set_epoch_sma_enabled(self, enabled):
        self.epoch_sma_enabled = enabled
        self.plot_page(self.current_page)

    def set_epoch_rsi_enabled(self, enabled):
        self.epoch_rsi_enabled = enabled
        self.plot_page(self.current_page)


    def set_answer_enabled(self, enabled):
        self.answer_enabled = enabled
        self.plot_page(self.current_page)

    def set_answer_ema_enabled(self, enabled):
        self.answer_ema_enabled = enabled
        self.plot_page(self.current_page)

    def set_answer_sma_enabled(self, enabled):
        self.answer_sma_enabled = enabled
        self.plot_page(self.current_page)

    def set_answer_rsi_enabled(self, enabled):
        self.answer_rsi_enabled = enabled
        self.plot_page(self.current_page)
# ####################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Graph display on the left with toolbar
        self.graph_widget = GraphWidget()
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.graph_widget)

        # Add Matplotlib's navigation toolbar for interactive features
        self.toolbar = NavigationToolbar(self.graph_widget, self)
        graph_layout.addWidget(self.toolbar)  # Add toolbar under the graph
        main_layout.addLayout(graph_layout)

        # Control panel on the right
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout()
        control_panel.setLayout(control_panel_layout)
        control_panel.setFixedWidth(250)  # Set fixed width to 250px

        # Interval input
        self.interval_label = QLabel("Interval (min):")
        self.interval_input = QLineEdit()
        self.interval_input.setText(str(self.graph_widget.interval))
        self.interval_input.returnPressed.connect(self.update_interval)
        control_panel_layout.addWidget(self.interval_label)
        control_panel_layout.addWidget(self.interval_input)
# ---------------------------------------------------
        # Periods input
        self.period_label = QLabel("Number of periods:")
        self.period_input = QLineEdit()
        self.period_input.setText(str(self.graph_widget.period))
        self.period_input.returnPressed.connect(self.update_period)
        control_panel_layout.addWidget(self.period_label)
        control_panel_layout.addWidget(self.period_input)

        # Checkboxes for Epoch EMA, SMA, and Stoch RSI
        self.epoch_checkbox = QCheckBox("Epoch")
        self.epoch_checkbox.setChecked(True)
        self.epoch_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_epoch_enabled(state == 2))
        control_panel_layout.addWidget(self.epoch_checkbox)

        self.epoch_ema_checkbox = QCheckBox("Epoch EMA")
        self.epoch_ema_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_epoch_ema_enabled(state == 2))
        control_panel_layout.addWidget(self.epoch_ema_checkbox)

        self.epoch_sma_checkbox = QCheckBox("Epoch SMA")
        self.epoch_sma_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_epoch_sma_enabled(state == 2))
        control_panel_layout.addWidget(self.epoch_sma_checkbox)

        self.epoch_rsi_checkbox = QCheckBox("Epoch RSI")
        self.epoch_rsi_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_epoch_rsi_enabled(state == 2))
        control_panel_layout.addWidget(self.epoch_rsi_checkbox)
        

        # Checkboxes for Answer EMA, SMA, and Stoch RSI
        self.answer_checkbox = QCheckBox("Answer")
        self.answer_checkbox.setChecked(True)
        self.answer_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_answer_enabled(state == 2))
        control_panel_layout.addWidget(self.answer_checkbox)

        self.answer_ema_checkbox = QCheckBox("Answer EMA")
        self.answer_ema_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_answer_ema_enabled(state == 2))
        control_panel_layout.addWidget(self.answer_ema_checkbox)

        self.answer_sma_checkbox = QCheckBox("Answer SMA")
        self.answer_sma_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_answer_sma_enabled(state == 2))
        control_panel_layout.addWidget(self.answer_sma_checkbox)

        self.answer_rsi_checkbox = QCheckBox("Answer RSI")
        self.answer_rsi_checkbox.stateChanged.connect(lambda state: self.graph_widget.set_answer_rsi_enabled(state == 2))
        control_panel_layout.addWidget(self.answer_rsi_checkbox)

# ####################################################
        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.graph_widget.prev_page)
        control_panel_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.graph_widget.next_page)
        control_panel_layout.addWidget(self.next_button)

        control_panel_layout.addStretch()  # Add space below the buttons

        main_layout.addWidget(control_panel)

        # Timer to update the graph every 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.graph_widget.update_data)
        self.timer.start(10000)  # 10000 ms = 10 seconds

    def update_interval(self):
        interval = self.interval_input.text()
        self.graph_widget.update_interval(interval)

    def update_period(self):
        period = self.period_input.text()
        self.graph_widget.update_period(period)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle("Data Plot Viewer")
    main_window.resize(1400, 980)
    main_window.show()
    sys.exit(app.exec_())
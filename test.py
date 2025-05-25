import plotext as plt
from datetime import datetime, timedelta
import random

day_format = "%d/%m/%Y"
today = datetime.today()
start_date = today - timedelta(days=365)

# Simuliere zufällige Commits für jeden Tag
day_commits = {}
current_day = start_date
while current_day <= today:
    date_str = current_day.strftime(day_format)
    day_commits[date_str] = random.choices(
        [0, 1, 2, 3, 4, 5, 6],
        weights=[60, 10, 10, 8, 6, 4, 2]
    )[0]
    current_day += timedelta(days=1)

# Bereite Daten für Heatmap vor (53 Wochen x 7 Tage)
heatmap_data = [[0 for _ in range(53)] for _ in range(7)]  # 7 Tage, 53 Wochen

for date_str, count in day_commits.items():
    dt = datetime.strptime(date_str, day_format)
    week = dt.isocalendar()[1] - 1  # Woche (0-basiert)
    day = dt.weekday()              # 0 = Montag … 6 = Sonntag
    if 0 <= week < 53:
        heatmap_data[day][week] = count

# Transponiere für plotext
heatmap_transposed = list(map(list, zip(*heatmap_data)))

# Achsenbeschriftungen
x_labels = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
y_labels = [f"W{w+1}" for w in range(53)]

# Plot
plt.clear_data()
plt.heatmap(heatmap_transposed, )
plt.title("Git Commit Heatmap (simuliert)")
plt.show()
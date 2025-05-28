from textual_plotext import PlotextPlot


def setup_plot_names(plot: PlotextPlot, title: str, xlabel: str, ylabel: str, type) -> None:
    """Set the plot names and configs.

    Set title, xlabel, ylable, grid and empty data
    Refreshes Plot after configuring

    Args:
        plot: Plot object
        title: The plot title
        xlabel: Lable for X-Axis
        ylabel: Label for Y-Axis
        type: Bar or Plot (line)

    """
    plot.plt.title(title)
    plot.plt.xlabel(xlabel)
    plot.plt.ylabel(ylabel)
    plot.plt.grid(True)
    if type == "bar":
        plot.plt.bar([], [])  # Initial empty bar chart
    elif type == "plot":
        plot.plt.plot([])  # Initial line chart
    plot.refresh()


def refresh_time_series_plot(plot: PlotextPlot, labels: list[str], values: list[int]) -> None:
    """Erzeugt oder aktualisiert das Balkendiagramm mit neuen Daten."""
    plt = plot.plt
    plt.clear_data()

    num_points = len(values)
    if num_points == 0:
        plot.refresh()
        return

    x = list(
        range(num_points),
    )  # Can't use labels directly due to an issue in the textualize package
    plt.plot(x, values, color="cyan")

    # Set only 10 labels. Textual scales it itself. Somehow scaling doesn't work with too many
    ticks = min(10, num_points)
    positions = [int(i * (num_points - 1) / (ticks - 1)) for i in range(ticks)]
    tick_labels = [labels[i] for i in positions]
    plt.xticks(positions, tick_labels)

    plot.refresh()


def refresh_user_commit_plot(plot: PlotextPlot, labels: list[str], values: list[int]) -> None:
    """Erzeugt oder aktualisiert das Balkendiagramm mit neuen Daten."""

    plt = plot.plt
    plt.clear_data()
    plt.bar(labels, values, color="cyan")  # setzt neue Balken
    plot.refresh()

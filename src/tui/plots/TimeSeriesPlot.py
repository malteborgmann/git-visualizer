from textual_plotext import PlotextPlot


class TimeSeriesPlot(PlotextPlot):
    """
    A custom Textual widget for plotting the number of Git commits in the Repository.

    This widget extends `PlotextPlot` and renders a line chart with dates on the x-axis
    and commit counts on the y-axis. It uses Plotext for terminal plotting.

    Args:
        name (str | None): Optional internal name for the widget.
        id (str | None): Optional DOM ID for styling or referencing.
        classes (str | None): Optional space-separated list of CSS class names.
        disabled (bool): Whether the widget is disabled on mount.
        color (str): The line color for the plot. Default is "cyan".

    """

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,  # pylint:disable=redefined-builtin
        classes: str | None = None,
        disabled: bool = False,
        color: str = "cyan",
    ) -> None:

        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._label: list[str] = []
        self._value: list[int] = []
        self._color = color

    def on_mount(self) -> None:
        """Plot the data using Plotext."""
        self.plt.date_form("Y-m-d H:M")
        self.plt.title("Commits over Time")
        self.plt.xlabel("Time")
        self.plt.ylabel("Number of Commits")
        self.plt.grid(True)

    def __replot(self) -> None:
        """
        Clear and redraw the plot using the current data.

        Internally used after updating the labels and values via `update`.
        """
        self.plt.clear_data()

        num_points = len(self._value)
        if num_points == 0:
            self.refresh()
            return

        x = list(
            range(num_points),
        )  # Can't use labels directly due to an issue in the textualize package
        self.plt.plot(x, self._value, color="cyan")

        ticks = min(10, num_points)
        positions = [int(i * (num_points - 1) / (ticks - 1)) for i in range(ticks)]
        tick_labels = [self._label[i] for i in positions]
        self.plt.xticks(positions, tick_labels)

        self.refresh()

    def update(self, label: list[str], value: list[int]) -> None:
        """
        Update the internal data and trigger a replot.

        Args:
            label (list[str]): Labels for the x-axis (usernames).
            value (list[int]): Corresponding number of commits for each user.

        """
        self._label = label
        self._value = value
        self.__replot()

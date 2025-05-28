from textual_plotext import PlotextPlot


class UserCommitPlot(PlotextPlot):
    """
    A custom Textual widget for plotting the number of Git commits per user.

    This widget extends `PlotextPlot` and renders a bar chart with user names on the x-axis
    and commit counts on the y-axis. It uses Plotext for terminal plotting.

    Args:
        name (str | None): Optional internal name for the widget.
        id (str | None): Optional DOM ID for styling or referencing.
        classes (str | None): Optional space-separated list of CSS class names.
        disabled (bool): Whether the widget is disabled on mount.
        color (str): The bar color for the plot. Default is "cyan".

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
        """
        Configure the base plot on mount.

        This sets plot titles, axis labels, and grid styling
        for better readability of the commit bar chart.
        """
        self.plt.title("Commits per User")
        self.plt.xlabel("User")
        self.plt.ylabel("Number of Commits")
        self.plt.grid(True)

    def __replot(self) -> None:
        """
        Clear and redraw the plot using the current data.

        Internally used after updating the labels and values via `update`.
        """
        self.plt.clear_data()

        self.plt.bar(self._label, self._value, color=self._color)
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

"""
Defines a modal dialog for exporting Git visualizations to a PDF file.

This module provides the ExportDialog class, which displays a filename input modal
and emits an ExportRequestMessage message upon confirmation. It uses Textual's UI components.
"""

from pathlib import Path

from textual.containers import Container
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


class ExportRequestMessage(Message):
    """
    The message we use for the export action.

    Extends Message to the filename, which is required for saving.

    Attributes:
        filename (str): The full path to the export file, including the .pdf suffix.

    """

    def __init__(self, filename: str) -> None:
        self.filename = filename
        super().__init__()


class ExportDialog(ModalScreen):
    """ModalScreen for entering the Filename for the new PDF."""

    def compose(self):  # noqa: ANN201
        """Create the Widgets on the ModelScreen."""
        with Container(id="export_modal"):
            yield Static("Enter export filename:", id="export_prompt")
            yield Input(placeholder="branches_report.pdf", id="export_filename")

            with Container(id="export_buttons"):
                yield Button("OK", id="export_ok")
                yield Button("Cancel", id="export_cancel")

    def on_mount(self) -> None:
        """Set focus the input field on mount."""
        input_field = self.query_one("#export_filename", Input)
        self.set_focus(input_field)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Action when OK Button is pressed."""  # noqa: D401
        if event.button.id == "export_ok":
            raw_input = (
                self.query_one("#export_filename", Input).value.strip() or "branches_report.pdf"
            )

            export_path = Path.cwd() / raw_input
            if export_path.suffix != ".pdf":
                export_path = export_path.with_suffix(".pdf")

            self.app.on_export_requested(ExportRequestMessage(export_path))
        self.dismiss()

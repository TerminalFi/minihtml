from typing import Optional

import mdpopups
import sublime

from .tag import tag
from .types import ContextBase


class Vision(tag):
    """
    Vision is a class that allows
    for the creation of minihtml content
    that can be rendered to a new sheet
    in Sublime Text or return the generated HTML.
    """

    def __init__(self, ctx: ContextBase):
        super().__init__(ctx, "html")
        self.sheet_name: str = ""
        self.sheet: Optional[sublime.Sheet] = None

    def reset(self) -> "Vision":
        """
        Resets the Vision object to its initial state. Clearing all the content, including head, body, css, and sheet.
        """
        self._children = []
        return self

    def render_to_sheet(self, sheet_name: str):
        if sheet_name == "":
            raise ValueError("Sheet name cannot be empty")
        # Render the full HTML document to a new sheet
        self.sheet_name = sheet_name
        if self.sheet is None or self.sheet.window() is None:
            self.sheet = mdpopups.new_html_sheet(
                window=sublime.active_window(),
                name=self.sheet_name,
                contents=self.render(),
                md=False,
            )
        else:
            mdpopups.update_html_sheet(self.sheet, self.render(), md=False)

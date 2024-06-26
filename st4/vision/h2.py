from typing import Optional

from .tag import tag
from .types import ContextBase


class h2(tag):
    """
    Represents the 'h2' HTML tag, used for secondary headings on a web page. This tag is typically used to denote
    subheadings or section titles under the main 'h1' heading, helping to organize content hierarchically and improve
    readability and SEO structure.

    Example usage:
        h2(content="Section Title: Introduction to the Topic")
    """

    def __init__(self, ctx: ContextBase, content: Optional[str] = None, *args, **kwargs):
        super().__init__(ctx, self.__class__.__name__, *args, **kwargs)
        if content:
            self.content(content)

import html
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from .supported import attribute_validator, css_validator
from .types import ContextBase


class base(type):
    """
    A metaclass for handling automatic parent-child relationships and instance creation within a
    nested context managed environment. This metaclass ensures that every new instance of a class
    using this metaclass is properly linked to its parent in the current context and that all children
    are automatically added to their respective parent's children List if applicable.

    The locking mechanism (_lock) is used to ensure that instance creation and parent-child linkage
    are thread-safe operations, preventing race conditions in a multi-threaded environment.
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        # test
        if instance.ctx is None:
            return instance

        with instance.ctx._lock:  # Use the global lock
            instance.parent = instance.ctx.current
            if instance.ctx.current is not None:
                instance.ctx.current._children.append(instance)
        return instance


class BaseTag(metaclass=base):
    """
    Base class for HTML elements, supporting dynamic attributes, styles, and nested structuring using context managers.
    This class is designed to be extended by other specific element classes to utilize HTML tags effectively in a Pythonic way with style and attribute management.

    Attributes:
        tag (str): The type of HTML tag (e.g., 'div', 'span', 'img').
        id (Optional[str]): The HTML 'id' attribute for the element (default None).
        classes (Optional[List[str]]): CSS classes to apply to the element.

    Note:
        - Use the __enter__ and __exit__ methods to manage context and enable nesting.
        - This class uses a metaclass for instance creation control and parent-child relationship management.
    """

    def __init__(
        self,
        ctx: Optional[ContextBase] = None,
        tag: str = "",
        id: Optional[str] = None,
        classes: Union[List[str], None] = None,
    ) -> None:
        self.ctx = ctx
        self.tag: str = tag
        self.id: Optional[str] = id
        self._classes: List[str] = classes if classes is not None else []
        self._styles: Dict[Any, Any] = {}
        self._attributes: Dict[str, str] = {}
        self._should_render: bool = True
        self.parent = None

    # Ensure all chaining methods return 'self' and are available in all relevant classes
    def __enter__(self) -> "BaseTag":
        # This might be a stub if BaseTag should not directly handle content
        raise NotImplementedError("This method should be overridden in subclasses")

    # Ensure all chaining methods return 'self' and are available in all relevant classes
    def __exit__(self, exc_type, exc_val, exc_tb) -> "BaseTag":
        # This might be a stub if BaseTag should not directly handle content
        raise NotImplementedError("This method should be overridden in subclasses")

    # Ensure all chaining methods return 'self' and are available in all relevant classes
    def content(self, text: str, escape: bool = False) -> "BaseTag":
        # This might be a stub if BaseTag should not directly handle content
        raise NotImplementedError("This method should be overridden in subclasses")

    def render(self) -> str:
        # This might be a stub if BaseTag should not directly handle content
        raise NotImplementedError("This method should be overridden in subclasses")

    # Style Management
    @property
    def styles(self) -> dict:
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                return dict(self._styles)
        else:
            return dict(self._styles)

    @styles.setter
    def styles(self, style_dict: dict):
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                self._styles.update(style_dict)
        else:
            self._styles.update(style_dict)

    def set_style(self, key: str, value: str) -> "BaseTag | ValueError":
        css_validator.validate(key, value)
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                self._styles[key] = value
        else:
            self._styles[key] = value
        return self

    # Class Management
    @property
    def classes(self) -> List[str]:
        with self.ctx._lock:  # type: ignore
            return list(self._classes)

    @classes.setter
    def classes(self, value: str):
        with self.ctx._lock:  # type: ignore
            self._classes.append(value)

    def set_classes(self, mode: Literal["append", "override"], value: str) -> "BaseTag":
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                if mode == "append":
                    self._classes.append(value)
                elif mode == "override":
                    self._classes = [value]
        else:
            if mode == "append":
                self._classes.append(value)
            elif mode == "override":
                self._classes = [value]
        return self

    # Attribute Management
    @property
    def attributes(self) -> dict:
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                return dict(self._attributes)
        else:
            return dict(self._attributes)

    @attributes.setter
    def attributes(self, value: dict):
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                self._attributes.update(value)
        else:
            self._attributes.update(value)

    def set_attribute(self, key: str, value: str) -> "BaseTag":
        attribute_validator.validate(key, value)
        if self.ctx:
            with self.ctx._lock:  # type: ignore
                if not value.startswith("subl:"):
                    value = html.escape(value)
                self._attributes[key] = value
        else:
            if not value.startswith("subl:"):
                value = html.escape(value)
            self._attributes[key] = value
        return self

    def href(self, value: str) -> "BaseTag":
        if self.tag != "a":
            raise ValueError("href is only available for <a> tags")
        self.set_attribute("href", value)
        return self

    # Dimension Attributes
    def width(self, value: str) -> "BaseTag":
        self.set_style("width", value)
        return self

    def height(self, value: str) -> "BaseTag":
        self.set_style("height", value)
        return self

    # Color and Spacing
    def bg_color(self, color: str) -> "BaseTag | ValueError":
        return self.set_style("background-color", color)

    def white_space(self, whitespace_type: str) -> "BaseTag | ValueError":
        return self.set_style("white-space", whitespace_type)

    def white_space_normal(self) -> "BaseTag | ValueError":
        return self.set_style("white-space", "normal")

    def white_space_no_wrap(self) -> "BaseTag | ValueError":
        return self.set_style("white-space", "nowrap")

    def white_space_pre(self) -> "BaseTag | ValueError":
        return self.set_style("white-space", "pre")

    def white_space_pre_wrap(self) -> "BaseTag | ValueError":
        return self.set_style("white-space", "pre-wrap")

    # Display Properties
    def display(self, display_type) -> "BaseTag | ValueError":
        return self.set_style("display", display_type)

    def display_none(self) -> "BaseTag | ValueError":
        return self.set_style("display", "none")

    def display_inline(self) -> "BaseTag | ValueError":
        return self.set_style("display", "inline")

    def display_block(self) -> "BaseTag | ValueError":
        return self.set_style("display", "block")

    def display_List_item(self) -> "BaseTag | ValueError":
        return self.set_style("display", "List-item")

    def display_inline_block(self) -> "BaseTag | ValueError":
        return self.set_style("display", "inline-block")

    # Positioning

    def position(self, position_type: str) -> "BaseTag | ValueError":
        return self.set_style("position", position_type)

    def position_static(self) -> "BaseTag | ValueError":
        return self.set_style("position", "static")

    def position_relative(self) -> "BaseTag | ValueError":
        return self.set_style("position", "relative")

    def top(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("top", value)

    def right(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("right", value)

    def bottom(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("bottom", value)

    def left(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("left", value)

    # Margin and Padding
    def m(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("margin", value)

    def ml(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("margin-left", value)

    def mr(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("margin-right", value)

    def mt(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("margin-top", value)

    def mb(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("margin-bottom", value)

    def p(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("padding", value)

    def pl(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("padding-left", value)

    def pr(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("padding-right", value)

    def pt(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("padding-top", value)

    def pb(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("padding-bottom", value)

    def px(self, value: str) -> "BaseTag | ValueError":
        pl = self.pl(value)
        if isinstance(pl, ValueError):
            return pl
        return self.pr(value)

    def py(self, value: str) -> "BaseTag | ValueError":
        pt = self.pt(value)
        if isinstance(pt, ValueError):
            return pt
        return self.pb(value)

    # Borders and Radius
    def border(self, width="1px", style="solid", color="black") -> "BaseTag | ValueError":
        return self.set_style("border", f"{width} {style} {color}")

    def border_left(self, width="1px", style="solid", color="black") -> "BaseTag | ValueError":
        return self.set_style("border-left", f"{width} {style} {color}")

    def border_right(self, width="1px", style="solid", color="black") -> "BaseTag | ValueError":
        return self.set_style("border-right", f"{width} {style} {color}")

    def border_top(self, width="1px", style="solid", color="black") -> "BaseTag | ValueError":
        return self.set_style("border-top", f"{width} {style} {color}")

    def border_bottom(self, width="1px", style="solid", color="black") -> "BaseTag | ValueError":
        return self.set_style("border-bottom", f"{width} {style} {color}")

    def border_radius(self, radius: str) -> "BaseTag | ValueError":
        return self.set_style("border-radius", radius)

    def border_top_left_radius(self, radius: str) -> "BaseTag | ValueError":
        return self.set_style("border-top-left-radius", radius)

    def border_top_right_radius(self, radius: str) -> "BaseTag | ValueError":
        return self.set_style("border-top-right-radius", radius)

    def border_bottom_right_radius(self, radius: str) -> "BaseTag | ValueError":
        return self.set_style("border-bottom-right-radius", radius)

    def border_bottom_left_radius(self, radius: str) -> "BaseTag | ValueError":
        return self.set_style("border-bottom-left-radius", radius)

    # Text and Font Styling
    def font_family(self, *family: str) -> "BaseTag | ValueError":
        return self.set_style("font-family", ", ".join(family))

    def font_normal(self) -> "BaseTag | ValueError":
        return self.set_style("font-weight", "normal")

    def font_bold(self) -> "BaseTag | ValueError":
        return self.set_style("font-weight", "bold")

    def text_align(self, align: str) -> "BaseTag | ValueError":
        return self.set_style("text-align", align)

    def text_decoration(self, value: str) -> "BaseTag | ValueError":
        return self.set_style("text-decoration", value)

    def text_decoration_none(self) -> "BaseTag | ValueError":
        return self.set_style("text-decoration", "none")

    def text_decoration_underline(self) -> "BaseTag | ValueError":
        return self.set_style("text-decoration", "underline")

    def color(self, color: str) -> "BaseTag | ValueError":
        return self.set_style("color", color)

    # Conditional Rendering
    def when(self, condition: Any) -> Any:
        """
        Return self if the condition is True, otherwise set the _should_render flag to False and return self.
        """
        if condition:
            return self
        else:
            self._should_render = False
            return self

    def when_or_else(
        self,
        condition: Any,
        func: Callable[[], Any],
        func_else: Callable[[], Any],
    ) -> List[Any]:
        """
        Return the result of func if the condition is True, otherwise return the result of func_else.
        Useful for adding multiple elements based on a condition.
        """
        if condition:
            return func()
        else:
            return func_else()

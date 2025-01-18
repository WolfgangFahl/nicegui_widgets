from nicegui import ui
from nicegui.testing import Screen

from ngwidgets.dict_edit import DictEdit


def test_dict_edit_s(screen: Screen) -> None:
    """Test the dict edit"""

    initial_dict = {"name": "John Doe", "age": 30, "is_student": False}

    @ui.page("/")
    def page():
        ui.label("DictEdit Test")
        dict_edit = DictEdit(initial_dict)
        dict_edit.open()

    screen.open("/")
    screen.shot("dict_edit")
    screen.should_contain_input("John Doe")
    screen.should_contain_input("30")
    screen.should_contain("is_student")

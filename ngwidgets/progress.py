from dataclasses import dataclass

from nicegui import ui
from tqdm import tqdm

from ngwidgets.color_schema import ColorSchema


@dataclass
class Progressbar:
    """
    Generic progress bar
    """

    _total: int
    value: int
    desc: str
    unit: str

    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, total: int):
        self._total = total
        self.update_total()

    def update_total(self):
        """
        Update the total value in the progress bar.
        """
        pass


class NiceguiProgressbar(Progressbar):
    """
    Nicegui progress bar wrapper.
    """

    def __init__(self, total, desc: str, unit: str, label_color="#8D92C4 "):
        """
        Initialize the NiceguiProgressbar instance.

        Args:
            total (int): The total value (maximum) of the progress bar.
            desc (str): A short description of the task for which the progress is being shown.
            unit (str): The unit of measurement for the progress (e.g., 'step', 'item').
            label_color(str): the color to use for the label
        The progress bar is initially set to invisible and its value to 0.
        """
        super().__init__(total, 0, desc, unit)
        self.progress = ui.linear_progress(
            value=0, size="20px", show_value=False
        ).props("instant-feedback")
        # Set the label color based on the provided color schema
        self.label_style = f"color: {label_color};"

        with self.progress:
            self.label = (
                ui.label().classes("text-lg absolute-center").style(self.label_style)
            )
            self.label.bind_text_from(
                self, "value", backward=lambda v: f"{self.desc} {v}/{self.total}"
            )
        self.progress.visible = False

    def reset(self):
        """
        reset
        """
        self.value = 0
        self.progress.value = 0

    def set_description(self, desc: str):
        """
        set my description
        """
        self.desc = desc
        self.progress.visible = True

    def update_value(self, new_value):
        self.value = new_value
        self.progress.visible = True
        percent = round(self.value / self.total, 2)
        self.progress.value = percent

    def update(self, step):
        self.update_value(self.value + step)


class TqdmProgressbar(Progressbar):
    """
    Tqdm progress bar wrapper.
    """

    def __init__(self, total, desc, unit):
        super().__init__(total, 0, desc, unit)
        self.reset()

    def reset(self):
        self.progress = tqdm(total=self.total, desc=self.desc, unit=self.unit)
        self.value = 0

    def set_description(self, desc: str):
        self.progress.set_description(desc)

    def update(self, step):
        self.update_value(self.value + step)

    def update_value(self, new_value):
        increment = new_value - self.value
        self.value = new_value
        self.progress.update(increment)

    def update_total(self):
        self.progress.total = self.total
        self.progress.refresh()

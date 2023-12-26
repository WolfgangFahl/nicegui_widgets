from dataclasses import dataclass

from nicegui import ui
from tqdm import tqdm


@dataclass
class Progressbar:
    """
    Generic progress bar
    """

    _total: int
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

    def __init__(self, total, desc: str, unit: str):
        super().__init__(total, desc, unit)
        self.value = 0
        self.progress = ui.linear_progress(value=0).props("instant-feedback")
        with self.progress:
            self.label = ui.label().classes("text-lg text-white absolute-center")
            self.label.bind_text_from(
                self, "value", backward=lambda v: f"{self.desc} {v}/{self.total}"
            )
        self.progress.visible = False

    def reset(self):
        self.value = 0
        self.progress.value = 0

    def set_description(self, desc: str):
        self.desc = desc
        self.progress.visible = True

    def update(self, step):
        self.value += step
        self.progress.visible = True
        percent = round(self.value / self.total, 2)
        self.progress.value = percent


class TqdmProgressbar(Progressbar):
    """
    Tqdm progress bar wrapper.
    """

    def __init__(self, total, desc, unit):
        super().__init__(total, desc, unit)
        self.reset()

    def reset(self):
        self.progress = tqdm(total=self.total, desc=self.desc, unit=self.unit)

    def set_description(self, desc: str):
        self.progress.set_description(desc)

    def update(self, step):
        self.progress.update(step)

    def update_total(self):
        self.progress.total = self.total
        self.progress.refresh()

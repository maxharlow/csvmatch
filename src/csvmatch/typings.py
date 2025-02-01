from typing import Protocol, Callable, Optional
import pyarrow
import polars

type ArrowDataframe = pyarrow.Table
type PolarsDataframe = polars.DataFrame

class Finalise(Protocol):
    def __call__(self, mode: str, message: Optional[str] = None) -> None: ...

type Progress = Callable[[str, int], Callable[[], None]]

class Alert(Protocol):
    def __call__(self, message: str, *, importance: Optional[str] = None) -> None: ...

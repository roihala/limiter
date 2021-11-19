from typing import List

from pydantic import BaseModel


class Positions(BaseModel):
    sell_buttons: List[int]
    presale_values: List[int]


class Screener(BaseModel):
    pass


class Schema(BaseModel):
    positions: Positions
    screener: Screener

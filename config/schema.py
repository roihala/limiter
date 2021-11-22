from typing import List

from pydantic import BaseModel


class SellButtons(BaseModel):
    values: List[int]
    limit_gap: int


class PresaleComboBox(BaseModel):
    values: List[int]
    quantity_precents: int


class Positions(BaseModel):
    sell_buttons: SellButtons
    presale_combobox: PresaleComboBox


class Screener(BaseModel):
    limit_gap: int
    position_size_usd: int


class Schema(BaseModel):
    positions: Positions
    screener: Screener

from typing import List

from pydantic import BaseModel


class SellButtons(BaseModel):
    values: List[int]
    limit: int

class AutoStopLoss(BaseModel):
    limit: int
    stop_percents: int


class ScreenerBuy(BaseModel):
    limit: int
    position_size_usd: int


class Buttons(BaseModel):
    sell_buttons: SellButtons
    screener_buy: ScreenerBuy


class Screener(BaseModel):
    above_price: int
    below_price: int
    change_percents: int
    above_volume: int


class Schema(BaseModel):
    buttons: Buttons
    screener: Screener
    auto_stop_loss: AutoStopLoss

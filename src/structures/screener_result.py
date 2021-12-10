from pydantic import BaseModel, validator


class ScreenerResult(BaseModel):
    ticker: str
    last_value: float
    # Volume rounded to millions
    volume: float
    change_percents: float

    @validator('last_value', 'change_percents', 'volume')
    def result_check(cls, v):
        ...
        return round(v, 2)

from datetime import date

def is_weekday(year, month, day):
    d = date(year, month, day)
    return d.weekday() < 5 # Monday is 0, Sunday is 6

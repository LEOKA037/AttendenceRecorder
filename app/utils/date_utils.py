from datetime import date, timedelta

def get_previous_working_days(num_days):
    today = date.today()
    working_days = []
    current_date = today

    while len(working_days) < num_days:
        # Check if the current_date is a weekday (Monday=0, Sunday=6)
        if current_date.weekday() < 5:
            working_days.append(current_date)
        current_date -= timedelta(days=1)
    
    working_days.reverse() # Oldest to newest
    return working_days

def is_weekday(d: date):
    return d.weekday() < 5

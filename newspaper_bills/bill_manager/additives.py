from datetime import datetime


class Counter:
    def __init__(self, value):
        self.value = value

    def increment(self):
        self.value += 1
        return ''

    def decrement(self):
        self.value -= 1
        return ''

    def __repr__(self):
        s = str(self.value)
        return s

    def value(self):
        return self.value


def month_name(month):
    return {1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
            }[month]


def days_count(year, month):
    solution = {}
    leap_year = None

    if year % 4 != 0:
        leap_year = False
    else:
        if year % 100 != 0:
            leap_year = True

        else:
            if year % 400 == 0:
                leap_year = True

    solution[1] = 31
    if leap_year:
        solution[2] = 29
    else:
        solution[2] = 28
    solution[3] = 31
    solution[4] = 30
    solution[5] = 31
    solution[6] = 30
    solution[7] = 31
    solution[8] = 31
    solution[9] = 30
    solution[10] = 31
    solution[11] = 30
    solution[12] = 31

    return solution[month]


def generate_calendar(day, month, year):
    first_date_of_month = '01 ' + str(month) + ' ' + str(year)[2:]

    # sun: day 1, mon: day 2 and so on.
    first_day_of_month = datetime.strptime(first_date_of_month, '%d %m %y').weekday()
    first_day_of_month = (first_day_of_month + 2) % 7

    if first_day_of_month == 0:
        first_day_of_month = 7

    if first_day_of_month > 4:
        calendar_rows = 6
    else:
        calendar_rows = 5

    counter = Counter(2 - first_day_of_month)

    calendar = {
                'day': day,
                'days': days_count(year, month),
                'calendar_rows': range(0, calendar_rows),
                'counter': counter,
                'month_name': month_name(month),
                'year': year,
                }

    return calendar

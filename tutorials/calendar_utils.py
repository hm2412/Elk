from datetime import datetime, timedelta
import calendar

class TutorCalendar:
    def __init__(self, year=None, month=None):
        self.year = year or datetime.now().year
        self.month = month or datetime.now().month
        
    def get_calendar_data(self, availability_slots):
        # Get the calendar for current month
        cal = calendar.monthcalendar(self.year, self.month)
        month_name = calendar.month_name[self.month]

        today = datetime.now()
        
        # Convert availability slots to a more usable format
        availability_dict = {}
        for slot in availability_slots:
            if slot.day not in availability_dict:
                availability_dict[slot.day] = []
            availability_dict[slot.day].append({
                'start': slot.start_time,
                'end': slot.end_time
            })
        
        # Process calendar weeks
        processed_calendar = []
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({
                        'day': '',
                        'is_current_month': False,
                        'slots': []
                    })
                else:
                    # Get the weekday name for this date
                    date = datetime(self.year, self.month, day)
                    weekday = date.strftime('%A')
                    
                    # Get availability slots for this weekday
                    slots = availability_dict.get(weekday, [])
                    
                    week_data.append({
                        'day': day,
                        'is_current_month': True,
                        'is_today': datetime.now().date() == date.date(),
                        'slots': slots,
                        'weekday': weekday
                    })
            processed_calendar.append(week_data)
            
        return {
            'weeks': processed_calendar,
            'month_name': month_name,
            'year': self.year,
            'prev_month': {
                'month': (self.month - 1) if self.month > 1 else 12,
                'year': self.year if self.month > 1 else self.year - 1
            },
            'next_month': {
                'month': (self.month + 1) if self.month < 12 else 1,
                'year': self.year if self.month < 12 else self.year + 1
            },
            'today': {
                'day': today.day,
                'month': today.month,
                'year': today.year
            }
        }

from datetime import datetime, timedelta
import calendar

class TutorCalendar:
    def __init__(self, year=None, month=None):
        self.year = year or datetime.now().year
        self.month = month or datetime.now().month
        
    def get_calendar_data(self, availability_slots, meetings):
        # Get the calendar for current month
        cal = calendar.monthcalendar(self.year, self.month)
        month_name = calendar.month_name[self.month]
        today = datetime.now()
        
        meetings = meetings or []
        meetings_dict = {}
        for meeting in meetings:
            date_key = meeting.date.day
            if date_key not in meetings_dict:
                meetings_dict[date_key] = []

            meetings_dict[date_key].append({
                'start': meeting.start_time.strftime('%H:%M'),
                'end': meeting.end_time.strftime('%H:%M'),
                'topic': meeting.topic,
                'student_name': f"{meeting.student.first_name} {meeting.student.last_name}",
                'status': meeting.status,
                'type': 'meeting'
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
                        'slots': [],
                        'meetings': []
                    })
                else:
                    date = datetime(self.year, self.month, day)
                    weekday = date.strftime('%A')
                    
                    # Prioritize meetings over availability slots
                    day_meetings = meetings_dict.get(day, [])
                    # day_slots = [] if day in meetings_dict else availability_dict.get(day, [])
                    
                    week_data.append({
                        'day': day,
                        'is_current_month': True,
                        'is_today': datetime.now().date() == date.date(),
                        'slots': [],
                        'meetings': day_meetings,
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
    
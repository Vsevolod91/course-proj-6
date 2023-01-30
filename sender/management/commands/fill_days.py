from django.core.management import BaseCommand
from sender.models import WeekDay, MonthDate, Hour, Minute
from sender.auxfunc import translit

class Command(BaseCommand):
    MonthDate.objects.all().delete()
    WeekDay.objects.all().delete()
    Hour.objects.all().delete()
    Minute.objects.all().delete()

    def handle(self, *args, **options):
        month_dates = []
        for num in range(1, 32):
            month_dates.append(MonthDate(number=num))

        MonthDate.objects.bulk_create(month_dates)

        days_dump = [
            {'value': 'Понедельник', 'id': 0},
            {'value': 'Вторник', 'id': 1},
            {'value': 'Среда', 'id': 2},
            {'value': 'Четверг', 'id': 3},
            {'value': 'Пятница', 'id': 4},
            {'value': 'Суббота', 'id': 5},
            {'value': 'Воскресенье', 'id': 6}
        ]

        days = []
        for item in days_dump:
            days.append(WeekDay(day=item['value'], day_id=item['id']))

        WeekDay.objects.bulk_create(days)

        hours = []
        for num in range(1, 24):
            hours.append(Hour(num=num))

        Hour.objects.bulk_create(hours)

        minutes = []
        count = 0
        for num in range(0, 60):
            count += 1
            if count == 1:
                minutes.append(Minute(num='00'))
                continue
            minutes.append(Minute(num=f'0{num}' if num < 10 else num))

        Minute.objects.bulk_create(minutes)



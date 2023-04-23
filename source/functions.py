from datetime import datetime
import time

def time_to_epoch(hour, minute, second):
    today = datetime.today()
    random_time = datetime(
        today.year, today.month, today.day, hour, minute, second, second)
    return round(time.mktime(random_time.timetuple()))

def epoch_to_time(epoch):
    return time.strftime('%H:%M:%S', time.localtime(int(epoch)))
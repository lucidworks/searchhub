from datetime import datetime, date, time
import random
from server import app

def create_schedule(details, id):
  active = app.config.get("ENABLE_SCHEDULES", False)
  today = date.today()
  the_time = time(random.randint(0,23), random.randint(0, 59), 0, 1) # Stagger our schedules for sanity sake
  the_date_time = datetime.combine(today, the_time)
  schedule = {
    "id": "schedule-{0}".format(id),
    "creatorType": "bootstrap",
    "repeatUnit": details["repeatUnit"],
    "interval": details["interval"],
    "startTime": the_date_time.isoformat() + "Z",
    "active": active,
    "callParams": {
      "uri": "service://connectors/jobs/{0}".format(id),
      "method": "POST",
      "queryParams": {},
      "headers": {}
    }
  }
  return schedule

from instances import *

last_notification = None
while True:
    notifications = insta.get_notifications()
    if not last_notification:
        last_notification = notifications[0]
        continue
    for notification in notifications:
        if last_notification.at < notification.at:
            print(notification.type.value, notification)
    if last_notification.at < notifications[0].at:
        last_notification = notifications[0]
    insta.mark_notifications()

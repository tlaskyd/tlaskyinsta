from schedule import Scheduler

scheduler = Scheduler()
scheduler.every(1).second.do(lambda: print('Executed'))

try:
    while True:
        scheduler.run_pending()
except KeyboardInterrupt:
    pass

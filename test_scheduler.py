from schedule import Scheduler

scheduler = Scheduler()
scheduler.every(1).second.do(lambda: print('_'))

try:
    while True:
        #print('-')
        scheduler.run_pending()
except KeyboardInterrupt:
    pass

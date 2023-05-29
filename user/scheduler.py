from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from user.models import User


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(task, "cron", hour="0")  # 서비스용 코드 - 매일 자정에 실행
    # scheduler.add_job(
    #     task, max_instances=1, trigger=IntervalTrigger(seconds=30)
    # )  # 테스트용 코드 - 30초마다 실행
    scheduler.start()


# 출석체크 초기화
def task():
    users = User.objects.all()
    for user in users:
        user.daily_check = True
        user.save()
    print("출석체크 초기화 완료")

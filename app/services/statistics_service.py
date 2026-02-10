from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.repositories import todo_repo, planner_repo
from app.models import User, Todo, Planner, Pomo, Concentration
from sqlalchemy import func, cast, Date

class StatisticsService:
    def get_planner_daily_statistics(self, db: Session, user: User, target_date: date):
        planner = planner_repo.get_by_user_and_date(db, user.id, target_date)
        if not planner:
             return {
                "date": target_date,
                "total_todos": 0,
                "completed_todos": 0,
                "completion_rate": 0.0,
                "by_priority": {
                    "high": {"total": 0, "completed": 0},
                    "medium": {"total": 0, "completed": 0},
                    "low": {"total": 0, "completed": 0}
                }
            }

        todos = todo_repo.get_all_by_planner(db, planner.planner_id)

        stats = {
            "date": target_date,
            "total_todos": len(todos),
            "completed_todos": len([t for t in todos if t.status == "completed"]),
            "completion_rate": 0.0,
            "by_priority": {
                "high": {"total": 0, "completed": 0},
                "medium": {"total": 0, "completed": 0},
                "low": {"total": 0, "completed": 0}
            }
        }

        if stats["total_todos"] > 0:
            stats["completion_rate"] = round((stats["completed_todos"] / stats["total_todos"]) * 100, 2)

        for todo in todos:
            p = todo.priority.name if hasattr(todo.priority, 'name') else str(todo.priority)
            if p in stats["by_priority"]:
                stats["by_priority"][p]["total"] += 1
                if todo.status == "completed":
                    stats["by_priority"][p]["completed"] += 1

        return stats

    def get_planner_weekly_statistics(self, db: Session, user: User, start_date: date):
        end_date = start_date + timedelta(days=6)


        results = db.query(Todo, Planner.plan_date).join(Planner).filter(
            Planner.user_id == user.id,
            Planner.plan_date >= start_date,
            Planner.plan_date <= end_date
        ).all()

        total_todos = len(results)
        completed_todos = len([t for t, d in results if t.status == "completed"])
        completion_rate = round((completed_todos / total_todos) * 100, 2) if total_todos > 0 else 0.0

        breakdown_dict = { (start_date + timedelta(days=i)): {"total": 0, "completed": 0} for i in range(7) }

        for todo, plan_date in results:
            if plan_date in breakdown_dict:
                breakdown_dict[plan_date]["total"] += 1
                if todo.status == "completed":
                    breakdown_dict[plan_date]["completed"] += 1

        daily_breakdown = [
            {
                "date": d,
                "total": stats["total"],
                "completed": stats["completed"],
                "completion_rate": round((stats["completed"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0.0
            }
            for d, stats in sorted(breakdown_dict.items())
        ]

        return {
            "week_start": start_date,
            "week_end": end_date,
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "completion_rate": completion_rate,
            "daily_breakdown": daily_breakdown
        }

    def get_pomo_daily_statistics(self, db: Session, user: User, target_date: date):
        pomo_results = db.query(
            func.count(Pomo.id).label("count"),
            func.sum(
                func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time)
            ).label("total_seconds")
        ).filter(
            Pomo.user_id == user.id,
            cast(Pomo.real_start_time, Date) == target_date
        ).first()

        pomo_count = pomo_results.count or 0
        total_minutes = int((pomo_results.total_seconds or 0) / 60)

        completed_todos = db.query(func.count(Todo.todo_id)).join(Planner).filter(
            Planner.user_id == user.id,
            Todo.status == "completed",
            cast(Todo.completed_at, Date) == target_date
        ).scalar() or 0

        total_distractions = db.query(func.count(Concentration.id)).join(Pomo).filter(
            Pomo.user_id == user.id,
            cast(Pomo.real_start_time, Date) == target_date,
            Concentration.event_type == "PICK_UP"
        ).scalar() or 0

        return {
            "date": target_date,
            "total_study_time_minutes": total_minutes,
            "pomo_count": pomo_count,
            "completed_todos": completed_todos,
            "total_distraction_count": total_distractions
        }

    def get_pomo_me_statistics(self, db: Session, user: User):
        results = db.query(
            func.count(Pomo.id).label("total_count"),
            func.sum(
                func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time)
            ).label("total_seconds"),
            func.count(func.distinct(cast(Pomo.real_start_time, Date))).label("days_count")
        ).filter(
            Pomo.user_id == user.id
        ).first()

        total_pomo_count = results.total_count or 0
        total_minutes = int((results.total_seconds or 0) / 60)
        days_count = results.days_count or 1
        average_minutes = int(total_minutes / days_count) if days_count > 0 else 0

        best_day_result = db.query(
            cast(Pomo.real_start_time, Date).label("study_date"),
            func.sum(
                func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time)
            ).label("daily_seconds")
        ).filter(
            Pomo.user_id == user.id
        ).group_by(
            "study_date"
        ).order_by(
            func.sum(func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time)).desc()
        ).first()

        best_day = best_day_result.study_date if best_day_result else None

        total_distractions = db.query(func.count(Concentration.id)).join(Pomo).filter(
            Pomo.user_id == user.id,
            Concentration.event_type == "PICK_UP"
        ).scalar() or 0

        return {
            "total_study_time_minutes": total_minutes,
            "average_daily_minutes": average_minutes,
            "total_pomo_count": total_pomo_count,
            "total_distraction_count": total_distractions,
            "best_day": best_day
        }

statistics_service = StatisticsService()

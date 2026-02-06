from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.repositories import todo_repo, planner_repo
from app.models import User, Todo, Planner

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
            {"date": d, "total": s["total"], "completed": s["completed"]}
            for d, s in sorted(breakdown_dict.items())
        ]

        return {
            "week_start": start_date,
            "week_end": end_date,
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "completion_rate": completion_rate,
            "daily_breakdown": daily_breakdown
        }

statistics_service = StatisticsService()

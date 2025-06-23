import aiosqlite
from datetime import datetime, timezone
from datetime import date
from typing import List, Dict

class DatabaseConn:
    def __init__(self, db_path="nutrition.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_type TEXT,
                    amount REAL,
                    unit TEXT,
                    meal_type TEXT,
                    calories REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def add_meal(self, food_type: str, amount: float, unit: str, meal_type: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO meals (food_type, amount, unit, meal_type)
                VALUES (?, ?, ?, ?)
            """, (food_type, amount, unit, meal_type))
            await db.commit()

    async def get_recent_meals(self) -> List[str]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT food_type, amount, unit, meal_type
                FROM meals
                ORDER BY timestamp DESC
                LIMIT 10
            """) as cursor:
                rows = await cursor.fetchall()
                return [f"{amount}{unit} {food_type} ({meal_type})" for food_type, amount, unit, meal_type in rows]

    async def add_meal_and_update_calories(
        self, food_type: str, amount: float, unit: str, meal_type: str, calories: float
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO meals (food_type, amount, unit, meal_type, calories)
                VALUES (?, ?, ?, ?, ?)
            """, (food_type, amount, unit, meal_type, calories))
            await db.commit()
    
    async def get_daily_summary(self) -> Dict:
        today_utc = datetime.now(timezone.utc).date().isoformat()
        summary = {
            "date": today_utc,
            "total_calories": 0,
            "by_meal": {}
        }

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT meal_type, SUM(calories)
                FROM meals
                WHERE DATE(timestamp) = DATE('now')
                GROUP BY meal_type
            """) as cursor:
                rows = await cursor.fetchall()

        total = 0
        for meal_type, cals in rows:
            summary["by_meal"][meal_type] = cals
            total += cals

        summary["total_calories"] = total
        return summary

    async def get_meals_by_date(self, target_date: date) -> List[Dict]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT food_type, amount, unit, meal_type, calories
                FROM meals
                WHERE DATE(timestamp) = ?
                ORDER BY meal_type
            """, (target_date.isoformat(),)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "food_type": row[0],
                        "amount": row[1],
                        "unit": row[2],
                        "meal_type": row[3],
                        "calories": row[4],
                    }
                    for row in rows
                ]
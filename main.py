from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
from nutrition_db import DatabaseConn

from contextlib import asynccontextmanager
from calorie_agent import calorie_agent, CalorieContext
from datetime import date

from summary_agent import DaySummaryContext, summary_agent

db = DatabaseConn("nutrition.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    yield


app = FastAPI(lifespan=lifespan)


class MealInput(BaseModel):
    food_type: str = Field(..., example="idly")
    amount: float = Field(..., example=1)
    unit: Literal[
        "g", "ml", "cup", "bowl", "piece", "item", "count"
    ] = Field(..., example="piece")
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"] = Field(..., example="breakfast")

@app.post("/log_meal")
async def log_meal(input: MealInput):
    deps = CalorieContext(
        food_type=input.food_type,
        amount=input.amount,
        unit=input.unit,
    )
    result = await calorie_agent.run("Estimate calories", deps=deps)
    calories = result.output.calories

    await db.add_meal_and_update_calories(
        food_type=input.food_type,
        amount=input.amount,
        unit=input.unit,
        meal_type=input.meal_type,
        calories=calories
    )

    return {"status": "saved", "calories_estimated": calories}


@app.get("/meals")
async def get_meals():
    return await db.get_recent_meals()

@app.get("/summary/{summary_date}")
async def get_summary(summary_date: date):
    meals = await db.get_meals_by_date(summary_date)

    print(f"Meals for {summary_date}: {meals}")

    deps = DaySummaryContext(
        date=summary_date.isoformat(),
        meals=meals
    )

    result = await summary_agent.run("Summarize calorie intake", deps=deps)
    return {
        "date": summary_date.isoformat(),
        "summary": result.output.summary,
    }
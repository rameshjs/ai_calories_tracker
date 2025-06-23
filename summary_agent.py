from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from typing import List
from pydantic import BaseModel, Field

@dataclass
class DaySummaryContext:
    date: str  
    meals: List[dict]  

class DaySummaryOutput(BaseModel):
    summary: str = Field(..., description="Natural language summary of the day's meals and calorie intake.")


summary_agent = Agent(
    model="openai:o3-mini",
    output_type=DaySummaryOutput,
    system_prompt=(
        "You are a helpful assistant that summarizes a person's meals and total calories for a given date.\n"
        "The user will provide a list of meals they ate during the day, each with:\n"
        "- food_type (e.g., idly)\n"
        "- amount\n"
        "- unit (e.g., piece, gram)\n"
        "- meal_type (e.g., breakfast, lunch)\n"
        "- calories\n"
        "Group the meals by meal_type, and total the calories.\n"
        "If the list is empty, respond with a polite message saying no data is available."
    ),
    model_kwargs={"temperature": 0.3}
)

@summary_agent.system_prompt
def enrich_summary_prompt(ctx: RunContext[DaySummaryContext]) -> str:
    if not ctx.deps.meals:
        return f"No meals were logged on {ctx.deps.date}."

    grouped_meals = {}
    for meal in ctx.deps.meals:
        meal_type = meal.get("meal_type", "unknown")
        grouped_meals.setdefault(meal_type, []).append(
            f"{meal['amount']} {meal['unit']} {meal['food_type']} ({meal['calories']} cal)"
        )

    meal_lines = "\n".join(
        f"{meal_type.capitalize()}:\n  - " + "\n  - ".join(items)
        for meal_type, items in grouped_meals.items()
    )

    return (
        f"Date: {ctx.deps.date}\n"
        f"The following meals were logged:\n\n{meal_lines}\n\n"
        f"Please summarize the calorie intake grouped by meal_type and give total calories."
    )

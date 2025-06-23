from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool


@dataclass
class CalorieContext:
    food_type: str
    amount: float
    unit: str


class CalorieOutput(BaseModel):
    calories: float = Field(..., ge=0, description="Estimated total calories")


calorie_agent = Agent(
    "openai:o3-mini",
    output_type=CalorieOutput,
    system_prompt=(
        "You are a calorie estimation assistant.\n"
        "Use the `duckduckgo_search_tool` to find real-world calorie values.\n"
        "Support both weight/volume inputs (e.g., 100g chicken) and count-based inputs (e.g., 2 idlis).\n"
        "Estimate the total calories based on amount and unit.\n"
        "If no data is found, return 0."
    ),
    tools=[duckduckgo_search_tool()],
    model_kwargs={"temperature": 0}
)


@calorie_agent.system_prompt
def enrich_prompt(ctx: RunContext[CalorieContext]) -> str:
    unit = ctx.deps.unit
    amount = ctx.deps.amount
    food = ctx.deps.food_type

    plural_unit = unit if amount == 1 else unit + "s"
    plural_food = food if amount == 1 else food + "s"

    return (
        f"The user ate {int(amount)} {plural_unit} of {plural_food}. "
        "Search DuckDuckGo for real-world calorie values and estimate the total calories."
    )

> ⚠️ **Note**: This README is generated by using AI.

# 🍱 Calorie Tracker with Pydantic AI

This project is a lightweight FastAPI-based calorie tracking app that explores the capabilities of [Pydantic AI](https://ai.pydantic.dev/).

## 🧠 Purpose

This is an experimental project to learn and demonstrate how to use **Pydantic AI Agents** to:

- Estimate calories based on user-entered food items using AI + search tools
- Summarize daily meals with natural language output
- Integrate structured data input/output with AI models via Pydantic

## 🛠️ Tech Stack

- **FastAPI** – backend API
- **Pydantic AI** – AI agent framework for structured input/output
- **SQLite** – lightweight local database
- **DuckDuckGo Search** – external search tool to find calorie info
- **Async I/O** – for all DB and network operations

## ✨ Features

- Log meals with food type, quantity, and meal type
- Auto-estimate calories using AI-powered tools
- Summarize meals for any date with AI-generated summaries
- Local database stores all logs

## 📦 Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI app
uvicorn main:app --reload

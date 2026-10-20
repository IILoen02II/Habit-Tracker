# Habit Tracker

A personal habit-tracking web app built with **Python, Streamlit and PostgreSQL**. It logs daily quantities (water, sleep, study time) and weekly goals (workouts per week), then turns them into streaks, compliance rates and charts using SQL views and pandas.

**Live app:** _add your Streamlit link here_

![Dashboard](docs/dashboard_app.png)
![Dashboard](docs/dashboard_register.png)

## Why I built it

I wanted to track my own habits, and I wanted the data model and analysis to be solid enough to answer real questions with SQL:

- Which habits do I keep consistently, and which ones break my streaks?
- What day of the week do I fail most often?
- How does my compliance change over 30, 90 and 365 days?

## Features

- **Quantity-based logging**: record a daily total per habit (liters, hours, minutes) instead of a plain yes/no.
- **Daily and weekly habits**: weekly goals such as "exercise 3 times per week" are evaluated per week (Monday to Sunday).
- **Minimum and maximum goals**: "at least 7 hours of sleep" and "at most 2 hours of gaming" are both supported.
- **Goal history**: changing a goal never rewrites the past; each day is evaluated against the goal that was active on that day.
- **Streaks**: current and best streak, in days for daily habits and in weeks for weekly habits.
- **Statistics**: compliance over 30/90/365 days, calendar heatmap, daily value vs. goal, and compliance by day of the week.
- **Soft deactivation**: habits are deactivated, never deleted, so the history stays intact.
- **Backfilling**: log any past date; sleep is assigned to the day you wake up.

## Tech stack

| Layer | Tools |
|---|---|
| App / UI | Streamlit |
| Database | PostgreSQL (Neon) |
| Data access | SQLAlchemy, psycopg |
| Analysis | pandas |
| Charts | Plotly |
| Tests | pytest |

## Data model

```
habits        (id, name, unit, frequency, direction, active, created_at)
habit_goals   (id, habit_id, target, valid_from, valid_to)
daily_logs    (id, habit_id, log_date, value, created_at)   UNIQUE (habit_id, log_date)

v_daily_status    daily habits  -> value, goal in effect that day, met (boolean)
v_weekly_status   weekly habits -> weekly total, goal, met (boolean)
```

Design decisions:

- **Store records, not totals.** Streaks and percentages are computed from the logs, so they can never go stale.
- **Goals have validity ranges.** `habit_goals` uses an `EXCLUDE` constraint (`btree_gist`) so two goals for the same habit can never overlap.
- **One row per habit and day.** `UNIQUE (habit_id, log_date)` plus an upsert makes re-saving a day safe.
- **Weeks start on Monday**, matching PostgreSQL's `date_trunc('week', ...)`.
- **Missing days count as not met** in compliance percentages, so unlogged days do not inflate the numbers.

## Project structure

```
habit-tracker/
├── app.py                  # Home: today's status and streaks
├── pages/
│   ├── 1_Registro.py       # Log habits for a day
│   ├── 2_Estadisticas.py   # Streaks, compliance, charts
│   └── 3_Habitos.py        # Create habits, change goals, deactivate
├── src/
│   ├── db.py               # Database connection
│   ├── repository.py       # All SQL reads and writes
│   ├── metrics.py          # Streaks and compliance (pure functions)
│   └── charts.py           # Plotly figures
├── sql/
│   ├── schema.sql          # Tables, views and seed data
│   └── migrations/
├── tests/
│   └── test_metrics.py
├── requirements.txt
└── .env.example
```

## Getting started

**Requirements:** Python 3.11+ and a PostgreSQL database (a free [Neon](https://neon.tech) project works well).

```bash
git clone https://github.com/IILoen02II/Habit-Tracker.git
cd habit-tracker

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt
```

**1. Create the database objects.** In your database's SQL editor, run, in this order:

1. `sql/schema.sql`
2. `sql/migrations/001_weekly_view.sql`

The seed data in `schema.sql` contains example habits and goals; edit them before running.

**2. Configure the connection.** Copy `.env.example` to `.env` and set your connection string:

```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB_NAME?sslmode=require
```

**3. Run the app.**

```bash
streamlit run app.py
```

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (`.env` is git-ignored).
2. Create a new app on [share.streamlit.io](https://share.streamlit.io) pointing to `app.py`.
3. In **Advanced settings → Secrets**, add:

   ```toml
   DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST/DB_NAME?sslmode=require"
   ```

## Tests

```bash
pip install pytest
pytest
```

The tests cover the streak and compliance logic in `src/metrics.py`.

## Roadmap

- [ ] Analysis notebook with findings from several weeks of real data
- [ ] Correlations between habits (e.g. sleep vs. study time)
- [ ] Export of the log to CSV

## Author

**Jeremy** · [(https://github.com/IILoen02II)]

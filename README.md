# Team Priority Planner — Streamlit App

A full-featured priority planner for small teams, built with Streamlit.

## Features

- **9-column tracker**: Priority (P0–P3), Project, Owner, Status, Due date, Impact area, Effort, Blocker, Next step, Business outcome
- **Live stats bar**: Total items, P0 count, blocked, overdue, in-progress, completed
- **Filters**: By priority, status, owner, and impact area
- **Add / edit / delete** items via sidebar forms
- **Impact vs effort matrix** view (Quick wins / Strategic / Fill-ins / Avoid)
- **CSV export** for sharing with stakeholders
- Overdue items flagged automatically in red

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens automatically at http://localhost:8501

## Deploying to Streamlit Community Cloud

1. Push this folder to a GitHub repository (public or private)
2. Go to https://share.streamlit.io
3. Click **New app** → connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — live in ~60 seconds

## File structure

```
priority_planner/
├── app.py            # Main Streamlit app
├── requirements.txt  # Python dependencies
└── README.md
```

## Priority guide

| Level | Meaning |
|-------|---------|
| P0 | Critical / urgent / leadership visibility |
| P1 | Important strategic work |
| P2 | Important but can wait |
| P3 | Nice to have / backlog |

## Effort scale

| Code | Meaning |
|------|---------|
| S | Small — less than 1 day |
| M | Medium |
| L | Large |
| XL | Multi-week |

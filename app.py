import streamlit as st
import pandas as pd
from datetime import date, datetime
import io

st.set_page_config(
    page_title="Team Priority Planner",
    page_icon="📋",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f7f6f2; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8e5de; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.planner-title { font-size: 22px; font-weight: 600; color: #1a1a18; letter-spacing: -0.3px; margin: 0; }
.planner-sub { font-size: 13px; color: #5f5e5a; margin: 2px 0 0; }

.stat-card { background: #ffffff; border: 1px solid #e0ddd6; border-radius: 10px; padding: 14px 18px; }
.stat-num { font-size: 24px; font-weight: 600; color: #1a1a18; line-height: 1; }
.stat-label { font-size: 11px; color: #9b9991; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.stat-overdue .stat-num { color: #A32D2D; }
.stat-blocked .stat-num { color: #854F0B; }

.badge { display: inline-block; border-radius: 5px; padding: 2px 8px; font-size: 11px; font-weight: 600; }
.p0 { background: #FCEBEB; color: #791F1F; }
.p1 { background: #FAEEDA; color: #633806; }
.p2 { background: #E6F1FB; color: #0C447C; }
.p3 { background: #F1EFE8; color: #444441; }

.status-blocked { color: #A32D2D; font-weight: 500; }
.status-inprogress { color: #0C447C; font-weight: 500; }
.status-waiting { color: #854F0B; font-weight: 500; }
.status-completed { color: #3B6D11; font-weight: 500; }
.status-review { color: #3C3489; font-weight: 500; }

.overdue { color: #A32D2D !important; font-weight: 500; }
.blocker-text { color: #854F0B; }

.q-card { border-radius: 10px; padding: 16px; margin-bottom: 8px; border: 1px solid; }
.q-win { background: #EAF3DE; border-color: #C0DD97; }
.q-strat { background: #E6F1FB; border-color: #B5D4F4; }
.q-fill { background: #FAEEDA; border-color: #FAC775; }
.q-avoid { background: #F1EFE8; border-color: #D3D1C7; }
.q-tag { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; }
.q-title { font-size: 14px; font-weight: 600; margin: 2px 0 10px; }
.q-win .q-tag { color: #3B6D11; } .q-win .q-title { color: #27500A; }
.q-strat .q-tag { color: #185FA5; } .q-strat .q-title { color: #0C447C; }
.q-fill .q-tag { color: #854F0B; } .q-fill .q-title { color: #633806; }
.q-avoid .q-tag { color: #5F5E5A; } .q-avoid .q-title { color: #444441; }

.q-item { background: white; border: 1px solid rgba(0,0,0,0.08); border-radius: 6px; padding: 8px 10px; margin-bottom: 6px; }
.q-item-name { font-size: 12px; font-weight: 500; color: #1a1a18; }
.q-item-meta { font-size: 11px; color: #5f5e5a; margin-top: 2px; }

div[data-testid="stDataFrame"] table { font-size: 13px; }
div[data-testid="stDataFrame"] thead th { background: #f0ede6 !important; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: #5f5e5a !important; }
</style>
""", unsafe_allow_html=True)

PRIORITIES = ["P0", "P1", "P2", "P3"]
STATUSES = ["Not started", "In progress", "Waiting on input", "Blocked", "Under review", "Completed"]
IMPACTS = ["", "Revenue", "Client delivery", "Thought leadership", "Partnership", "Internal enablement", "Conference prep", "Innovation", "Other"]
EFFORTS = ["", "S", "M", "L", "XL"]
HIGH_IMPACT = {"Revenue", "Client delivery", "Thought leadership", "Partnership"}

PRIORITY_LABELS = {
    "P0": "P0 — Critical / urgent",
    "P1": "P1 — Important strategic",
    "P2": "P2 — Important, can wait",
    "P3": "P3 — Nice to have / backlog",
}

def init_data():
    if "items" not in st.session_state:
        st.session_state.items = [
            {"id": 1, "priority": "P0", "name": "Finalize AI in Clinical workshop agenda", "owner": "You", "status": "In progress", "due": date(2026, 5, 16), "impact": "Conference prep", "effort": "M", "blocker": "", "next_step": "Review abstract draft", "outcome": "Thought leadership positioning"},
            {"id": 2, "priority": "P0", "name": "Prepare Veeva capability deck", "owner": "Alice", "status": "Blocked", "due": date(2026, 5, 14), "impact": "Client delivery", "effort": "L", "blocker": "Client input", "next_step": "Chase client for brief", "outcome": "Expand Veeva partnership"},
            {"id": 3, "priority": "P1", "name": "Q3 roadmap planning session", "owner": "Bob", "status": "Not started", "due": date(2026, 5, 28), "impact": "Internal enablement", "effort": "M", "blocker": "", "next_step": "Schedule sponsor call", "outcome": "Team alignment on priorities"},
            {"id": 4, "priority": "P1", "name": "Dashboard screenshots for report", "owner": "Carol", "status": "In progress", "due": date(2026, 5, 20), "impact": "Revenue", "effort": "S", "blocker": "", "next_step": "Finalize dashboard screenshots", "outcome": "Quarterly business review"},
            {"id": 5, "priority": "P2", "name": "Update partnership one-pager", "owner": "David", "status": "Not started", "due": date(2026, 6, 5), "impact": "Partnership", "effort": "S", "blocker": "Budget approval", "next_step": "Draft new messaging", "outcome": "Support BD conversations"},
            {"id": 6, "priority": "P3", "name": "Old filing system cleanup", "owner": "Eve", "status": "Not started", "due": None, "impact": "Internal enablement", "effort": "XL", "blocker": "", "next_step": "Define scope", "outcome": "Operational efficiency"},
        ]
        st.session_state.next_id = 7
        st.session_state.show_add = False
        st.session_state.edit_id = None

def get_items():
    return st.session_state.items

def add_item(item):
    item["id"] = st.session_state.next_id
    st.session_state.next_id += 1
    st.session_state.items.append(item)

def update_item(id_, data):
    for i, item in enumerate(st.session_state.items):
        if item["id"] == id_:
            st.session_state.items[i] = {**item, **data}
            break

def delete_item(id_):
    st.session_state.items = [i for i in st.session_state.items if i["id"] != id_]

def render_stats(items):
    today = date.today()
    total = len(items)
    p0 = sum(1 for i in items if i["priority"] == "P0")
    blocked = sum(1 for i in items if i["status"] == "Blocked")
    overdue = sum(1 for i in items if i["due"] and i["due"] < today and i["status"] != "Completed")
    in_prog = sum(1 for i in items if i["status"] == "In progress")
    done = sum(1 for i in items if i["status"] == "Completed")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, num, label, cls in [
        (c1, total, "Total items", ""),
        (c2, p0, "P0 critical", ""),
        (c3, in_prog, "In progress", ""),
        (c4, blocked, "Blocked", "stat-blocked"),
        (c5, overdue, "Overdue", "stat-overdue"),
        (c6, done, "Completed", ""),
    ]:
        col.markdown(f"""
        <div class="stat-card {cls}">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

def item_form(prefix, defaults=None):
    d = defaults or {}
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Project / task name *", value=d.get("name", ""), key=f"{prefix}_name", placeholder="e.g. Finalize AI in Clinical workshop agenda")
        priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(d.get("priority", "P1")), key=f"{prefix}_priority", format_func=lambda x: PRIORITY_LABELS[x])
        owner = st.text_input("Owner", value=d.get("owner", ""), key=f"{prefix}_owner", placeholder="Single accountable person")
        status = st.selectbox("Status", STATUSES, index=STATUSES.index(d.get("status", "Not started")), key=f"{prefix}_status")
        due_val = d.get("due")
        due = st.date_input("Due date", value=due_val if due_val else None, key=f"{prefix}_due")
    with col2:
        impact_idx = IMPACTS.index(d.get("impact", "")) if d.get("impact", "") in IMPACTS else 0
        impact = st.selectbox("Impact area", IMPACTS, index=impact_idx, key=f"{prefix}_impact")
        effort_idx = EFFORTS.index(d.get("effort", "")) if d.get("effort", "") in EFFORTS else 0
        effort = st.selectbox("Effort", EFFORTS, index=effort_idx, key=f"{prefix}_effort", help="S < 1 day · M medium · L large · XL multi-week")
        blocker = st.text_input("Blocker / dependency", value=d.get("blocker", ""), key=f"{prefix}_blocker", placeholder="e.g. Client input, Budget approval")
        next_step = st.text_input("Next step", value=d.get("next_step", ""), key=f"{prefix}_next_step", placeholder="e.g. Review abstract draft")
        outcome = st.text_input("Business outcome", value=d.get("outcome", ""), key=f"{prefix}_outcome", placeholder="e.g. Expand Veeva partnership")
    return {
        "name": name, "priority": priority, "owner": owner, "status": status,
        "due": due, "impact": impact, "effort": effort,
        "blocker": blocker, "next_step": next_step, "outcome": outcome,
    }

def render_list_view(items):
    today = date.today()

    def fmt_due(d):
        if not d:
            return "—"
        label = d.strftime("%d %b %y")
        if d < today:
            return f"🔴 {label}"
        return label

    df_rows = []
    for item in items:
        df_rows.append({
            "Priority": item["priority"],
            "Project / task": item["name"],
            "Owner": item["owner"] or "—",
            "Status": item["status"],
            "Due date": fmt_due(item["due"]),
            "Impact area": item["impact"] or "—",
            "Effort": item["effort"] or "—",
            "Blocker": item["blocker"] or "—",
            "Next step": item["next_step"] or "—",
            "Business outcome": item["outcome"] or "—",
        })

    if not df_rows:
        st.info("No items match your filters. Add one using the sidebar.")
        return

    df = pd.DataFrame(df_rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority": st.column_config.TextColumn(width="small"),
            "Project / task": st.column_config.TextColumn(width="large"),
            "Owner": st.column_config.TextColumn(width="small"),
            "Status": st.column_config.TextColumn(width="medium"),
            "Due date": st.column_config.TextColumn(width="small"),
            "Impact area": st.column_config.TextColumn(width="medium"),
            "Effort": st.column_config.TextColumn(width="small"),
            "Blocker": st.column_config.TextColumn(width="medium"),
            "Next step": st.column_config.TextColumn(width="large"),
            "Business outcome": st.column_config.TextColumn(width="large"),
        }
    )

def render_matrix_view(items):
    HIGH_EFFORT = {"L", "XL"}
    quadrants = {
        "win":   {"cls": "q-win",   "tag": "Quick wins",          "title": "High impact · Low effort",   "items": []},
        "strat": {"cls": "q-strat", "tag": "Strategic projects",   "title": "High impact · High effort",  "items": []},
        "fill":  {"cls": "q-fill",  "tag": "Fill-ins",             "title": "Low impact · Low effort",    "items": []},
        "avoid": {"cls": "q-avoid", "tag": "Avoid / deprioritise", "title": "Low impact · High effort",   "items": []},
    }
    for item in items:
        hi = item["impact"] in HIGH_IMPACT
        he = item["effort"] in HIGH_EFFORT
        q = "win" if hi and not he else "strat" if hi and he else "avoid" if not hi and he else "fill"
        quadrants[q]["items"].append(item)

    st.markdown("<div style='display:flex;gap:20px;margin-bottom:6px;'><span style='flex:1;text-align:center;font-size:12px;color:#5f5e5a;font-weight:500;'>← Low effort</span><span style='flex:1;text-align:center;font-size:12px;color:#5f5e5a;font-weight:500;'>High effort →</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;color:#9b9991;margin-bottom:14px;'>Impact area determines vertical axis: Revenue, Client delivery, Thought leadership, Partnership = High impact</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for col, qkey in [(col1, "win"), (col2, "strat")]:
        with col:
            q = quadrants[qkey]
            items_html = "".join(
                f'<div class="q-item"><div class="q-item-name">{i["name"]}</div>'
                f'<div class="q-item-meta">{i["owner"] or "Unassigned"} · {i["effort"] or "?"} effort · {i["priority"]}</div></div>'
                for i in q["items"]
            ) or '<div style="font-size:11px;color:#9b9991;font-style:italic;">No items here</div>'
            st.markdown(f'<div class="q-card {q["cls"]}"><div class="q-tag">{q["tag"]}</div><div class="q-title">{q["title"]}</div>{items_html}</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    for col, qkey in [(col3, "fill"), (col4, "avoid")]:
        with col:
            q = quadrants[qkey]
            items_html = "".join(
                f'<div class="q-item"><div class="q-item-name">{i["name"]}</div>'
                f'<div class="q-item-meta">{i["owner"] or "Unassigned"} · {i["effort"] or "?"} effort · {i["priority"]}</div></div>'
                for i in q["items"]
            ) or '<div style="font-size:11px;color:#9b9991;font-style:italic;">No items here</div>'
            st.markdown(f'<div class="q-card {q["cls"]}"><div class="q-tag">{q["tag"]}</div><div class="q-title">{q["title"]}</div>{items_html}</div>', unsafe_allow_html=True)

def to_csv(items):
    rows = []
    for i in items:
        rows.append({
            "Priority": i["priority"],
            "Project / task": i["name"],
            "Owner": i["owner"],
            "Status": i["status"],
            "Due date": i["due"].strftime("%Y-%m-%d") if i["due"] else "",
            "Impact area": i["impact"],
            "Effort": i["effort"],
            "Blocker": i["blocker"],
            "Next step": i["next_step"],
            "Business outcome": i["outcome"],
        })
    buf = io.StringIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    return buf.getvalue()

def main():
    init_data()
    items = get_items()

    # Sidebar
    with st.sidebar:
        st.markdown("## Priority planner")
        st.markdown("---")

        st.markdown("### Filters")
        f_priority = st.selectbox("Priority", ["All"] + PRIORITIES, key="filter_priority")
        f_status = st.selectbox("Status", ["All"] + STATUSES, key="filter_status")
        owners = sorted(set(i["owner"] for i in items if i["owner"]))
        f_owner = st.selectbox("Owner", ["All"] + owners, key="filter_owner")
        f_impact = st.selectbox("Impact area", ["All"] + [x for x in IMPACTS if x], key="filter_impact")

        st.markdown("---")
        st.markdown("### Actions")

        if st.button("➕ Add new item", use_container_width=True, type="primary"):
            st.session_state.show_add = True
            st.session_state.edit_id = None

        csv_data = to_csv(items)
        st.download_button(
            label="⬇ Export CSV",
            data=csv_data,
            file_name="priority-planner.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("### Edit / delete item")
        item_names = {i["id"]: f"{i['priority']} — {i['name'][:35]}" for i in items}
        selected_id = st.selectbox("Select item", [None] + list(item_names.keys()), format_func=lambda x: "— choose —" if x is None else item_names[x], key="selected_item")

        if selected_id:
            col_e, col_d = st.columns(2)
            with col_e:
                if st.button("Edit", use_container_width=True):
                    st.session_state.edit_id = selected_id
                    st.session_state.show_add = False
            with col_d:
                if st.button("Delete", use_container_width=True):
                    delete_item(selected_id)
                    st.rerun()

        st.markdown("---")
        st.markdown("<div style='font-size:11px;color:#9b9991;'>Priority guide:<br>P0 = Critical / urgent<br>P1 = Important strategic<br>P2 = Important, can wait<br>P3 = Nice to have</div>", unsafe_allow_html=True)

    # Apply filters
    filtered = items
    if f_priority != "All":
        filtered = [i for i in filtered if i["priority"] == f_priority]
    if f_status != "All":
        filtered = [i for i in filtered if i["status"] == f_status]
    if f_owner != "All":
        filtered = [i for i in filtered if i["owner"] == f_owner]
    if f_impact != "All":
        filtered = [i for i in filtered if i["impact"] == f_impact]

    # Header
    st.markdown('<p class="planner-title">Team priority planner</p>', unsafe_allow_html=True)
    st.markdown('<p class="planner-sub">Track what matters, who owns it, and what\'s next</p>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    render_stats(items)
    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    # Add form
    if st.session_state.show_add:
        st.markdown("### Add new item")
        with st.form("add_form"):
            data = item_form("add")
            submitted = st.form_submit_button("Save item", type="primary")
            cancelled = st.form_submit_button("Cancel")
        if submitted:
            if data["name"].strip():
                add_item(data)
                st.session_state.show_add = False
                st.rerun()
            else:
                st.error("Project name is required.")
        if cancelled:
            st.session_state.show_add = False
            st.rerun()
        st.markdown("---")

    # Edit form
    if st.session_state.edit_id:
        edit_item = next((i for i in items if i["id"] == st.session_state.edit_id), None)
        if edit_item:
            st.markdown(f"### Edit: {edit_item['name']}")
            with st.form("edit_form"):
                data = item_form("edit", defaults=edit_item)
                saved = st.form_submit_button("Save changes", type="primary")
                cancel_edit = st.form_submit_button("Cancel")
            if saved:
                update_item(st.session_state.edit_id, data)
                st.session_state.edit_id = None
                st.rerun()
            if cancel_edit:
                st.session_state.edit_id = None
                st.rerun()
            st.markdown("---")

    # View tabs
    view = st.radio("View", ["List view", "Impact vs effort matrix"], horizontal=True, label_visibility="collapsed")

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    if view == "List view":
        render_list_view(filtered)
    else:
        render_matrix_view(filtered)

if __name__ == "__main__":
    main()

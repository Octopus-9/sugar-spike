import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ---------------- Mock Data ---------------- #
sugar_items = {
    'Coke (12oz)': {'sugar': 39, 'impact': 'Spikes blood sugar by 20%, potential energy crash in 1 hour.'},
    'Snickers Bar': {'sugar': 27, 'impact': 'Adds 27g sugar, increases prediabetes risk by 5% if daily.'},
    'Fruit Punch (8oz)': {'sugar': 30, 'impact': '30g sugar load, may disrupt sleep if consumed in the evening.'},
    'Candy Bar': {'sugar': 25, 'impact': '25g sugar, contributes to weight gain over time.'},
}

# ---------------- Session State ---------------- #
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_log_date' not in st.session_state:
    st.session_state.last_log_date = None
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'daily_budget' not in st.session_state:
    st.session_state.daily_budget = 50  # Default, customizable
if 'challenges' not in st.session_state:
    st.session_state.challenges = []  # List of active challenges
if 'goals' not in st.session_state:
    st.session_state.goals = {'weekly_sugar': 200, 'streak_target': 30}  # Mock goals

# ---------------- Helper Functions ---------------- #
def get_recommendation(item):
    recs = {
        'Coke': 'Try sparkling water with lemon—saves 39g sugar!',
        'Snickers': 'Swap for a handful of nuts—natural energy without the crash.',
        'Fruit Punch': 'Opt for unsweetened tea—cuts sugar and boosts hydration.',
        'Candy Bar': 'Go for dark chocolate (70%+)—less sugar, more antioxidants.'
    }
    for key, rec in recs.items():
        if key in item:
            return rec
    return 'Choose a low-sugar alternative next time!'

def update_streak():
    today = datetime.now().date().isoformat()
    if st.session_state.last_log_date != today:
        st.session_state.streak += 1
        st.session_state.last_log_date = today
        # Award badges
        if st.session_state.streak == 3:
            st.session_state.badges.append("Sugar Starter")
        elif st.session_state.streak == 7:
            st.session_state.badges.append("Week Warrior")
        elif st.session_state.streak == 14:
            st.session_state.badges.append("Habit Hero")

def get_today_sugar():
    today = datetime.now().date()
    return sum(
        log['sugar']
        for log in st.session_state.logs
        if pd.to_datetime(log['date']).date() == today
    )

def generate_challenge():
    challenges = [
        "Skip sugary drinks for the next 3 days!",
        "Log every snack today and aim for under 20g sugar.",
        "Replace one candy bar with fruit this week."
    ]
    return random.choice(challenges)

def get_health_tips():
    tips = [
        "Drink water before meals to reduce cravings.",
        "Read labels: Aim for under 5g sugar per serving.",
        "Exercise after sugary snacks to stabilize blood sugar."
    ]
    return random.sample(tips, 2)

# ---------------- Sidebar ---------------- #
st.sidebar.title("🍬 SugarSense Dashboard")
page = st.sidebar.radio("Navigate", ["Log Item", "Dashboard", "Insights", "Settings", "Goals"])

# Quick challenge generator
if st.sidebar.button("🎯 Get a Daily Challenge"):
    challenge = generate_challenge()
    if challenge not in st.session_state.challenges:
        st.session_state.challenges.append(challenge)
    st.sidebar.success(f"New Challenge: {challenge}")

if st.session_state.challenges:
    st.sidebar.subheader("Active Challenges")
    for chal in st.session_state.challenges:
        st.sidebar.write(f"- {chal}")

# Health tips expander
with st.sidebar.expander("💡 Quick Health Tips"):
    tips = get_health_tips()
    for tip in tips:
        st.write(f"- {tip}")

# ---------------- Log Page ---------------- #
if page == "Log Item":
    st.title("Quick Log Your Sugar Choice")
    st.markdown("Select and log in seconds—get instant feedback!")

    # Preset items with quantity
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_item = st.selectbox("🍭 Choose a sugary item:", list(sugar_items.keys()))
    with col2:
        quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1, step=1)
    with col3:
        if st.button("Log It! 🚀", use_container_width=True):
            total_sugar = sugar_items[selected_item]['sugar'] * quantity
            log_entry = {
                'date': datetime.now().isoformat(),
                'item': selected_item,
                'sugar': total_sugar,
                'quantity': quantity
            }
            st.session_state.logs.append(log_entry)
            update_streak()
            st.success(f"✅ Logged {quantity}x {selected_item} ({total_sugar}g sugar)! Streak: {st.session_state.streak} days.")

    # Custom item logging form
    with st.expander("➕ Log a Custom Item"):
        with st.form("custom_log"):
            custom_name = st.text_input("Item Name (e.g., Homemade Cookie)")
            custom_sugar = st.number_input("Sugar Amount per Unit (g)", min_value=0, step=1)
            custom_quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            custom_impact = st.text_area("Optional Impact Note", placeholder="Describe the impact...")
            submitted = st.form_submit_button("Log Custom Item")
            if submitted and custom_name and custom_sugar > 0:
                total_sugar = custom_sugar * custom_quantity
                log_entry = {
                    'date': datetime.now().isoformat(),
                    'item': custom_name,
                    'sugar': total_sugar,
                    'quantity': custom_quantity
                }
                st.session_state.logs.append(log_entry)
                update_streak()
                st.success(f"✅ Logged {custom_quantity}x {custom_name} ({total_sugar}g sugar)! Streak: {st.session_state.streak} days.")

    if st.session_state.logs:
        with st.expander("See Real-Time Impact & Suggestion"):
            impact = sugar_items.get(selected_item, {}).get('impact', custom_impact or 'Custom item logged.')
            st.write(f"⚠️ **Impact:** {impact}")
            st.info(f"💡 **Next Step:** {get_recommendation(selected_item or custom_name)}")

# ---------------- Dashboard Page ---------------- #
elif page == "Dashboard":
    st.title("📊 Your Sugar Dashboard")
    st.markdown("Track your progress, budget, and trends at a glance!")

    col1, col2, col3 = st.columns(3)
    today_sugar = get_today_sugar()

    with col1:
        st.metric("Today's Sugar", f"{today_sugar}g", delta=f"{st.session_state.daily_budget - today_sugar}g left")
    with col2:
        avg_sugar = sum(log['sugar'] for log in st.session_state.logs) / max(len(st.session_state.logs), 1)
        st.metric("Avg Logged Sugar", f"{avg_sugar:.1f}g")
    with col3:
        st.metric("Streak", f"{st.session_state.streak} days 🔥")

    # Interactive Progress Bar with Reset
    progress = min(today_sugar / st.session_state.daily_budget, 1.0)
    st.progress(
        progress,
        text=f"Sugar Budget: {today_sugar}/{st.session_state.daily_budget}g "
             f"({'Safe' if progress < 0.5 else 'Watch It' if progress < 0.8 else 'Over Limit!'})"
    )
    if st.button("Reset Today's Logs (for testing)"):
        st.session_state.logs = [log for log in st.session_state.logs if pd.to_datetime(log['date']).date() != datetime.now().date()]
        st.rerun()

    # Interactive Chart Section
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        df["date"] = pd.to_datetime(df["date"])
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        # Chart Type Toggle and Aggregation
        chart_type = st.radio("Chart Type", ["Line", "Bar"], horizontal=True)
        agg_type = st.selectbox("Aggregate By", ["Daily", "Weekly", "Monthly"])

        if min_date != max_date:
            start_date, end_date = st.slider(
                "Select Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
            )
            filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
        else:
            filtered_df = df
            st.info(f"Only one date available: {min_date}")

        if agg_type == "Daily":
            grouped = filtered_df.groupby(filtered_df["date"].dt.date)["sugar"].sum().reset_index()
            x_col = "date"
        elif agg_type == "Weekly":
            grouped = filtered_df.groupby(filtered_df["date"].dt.isocalendar().week)["sugar"].sum().reset_index()
            x_col = "week"
        else:
            grouped = filtered_df.groupby(filtered_df["date"].dt.month)["sugar"].sum().reset_index()
            x_col = "month"

        if chart_type == "Line":
            fig = px.line(grouped, x=x_col, y="sugar", markers=True, title=f"Sugar Intake ({agg_type})")
        else:
            fig = px.bar(grouped, x=x_col, y="sugar", title=f"Sugar Intake ({agg_type})")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # Badges with Interaction
    if st.session_state.badges:
        st.subheader("🏆 Your Badges")
        cols = st.columns(len(st.session_state.badges))
        for i, badge in enumerate(st.session_state.badges):
            with cols[i]:
                if st.button(badge, key=f"badge_{i}"):
                    st.info(f"Badge: {badge} - Earned for {st.session_state.streak} day streak!")

# ---------------- Insights Page ---------------- #
elif page == "Insights":
    st.title("🔍 Habit Insights")

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        df["date"] = pd.to_datetime(df["date"])
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        # Interactive Filters
        st.subheader("Filter Insights")
        filter_items = st.multiselect("Select Items to Include", options=df["item"].unique(), default=df["item"].unique())
        filtered_df = df[df["item"].isin(filter_items)]

        if min_date != max_date:
            start_date, end_date = st.slider(
                "Select Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
            )
            filtered_df = filtered_df[(filtered_df["date"].dt.date >= start_date) & (filtered_df["date"].dt.date <= end_date)]
        else:
            st.info(f"Only one date available: {min_date}")

        top_items = filtered_df["item"].value_counts().head(3)

        st.subheader("Most Logged Items")
        for item, count in top_items.items():
            st.write(f"- {item}: {count} times")

        weekly_sugar = filtered_df.groupby(filtered_df["date"].dt.isocalendar().week)["sugar"].sum()
        st.subheader("Weekly Sugar Totals")
        st.bar_chart(weekly_sugar)

        # Interactive Pie Chart for Item Breakdown
        if not filtered_df.empty:
            item_totals = filtered_df.groupby("item")["sugar"].sum().reset_index()
            fig = go.Figure(data=[go.Pie(labels=item_totals["item"], values=item_totals["sugar"], hoverinfo="label+percent+value")])
            fig.update_layout(title="Sugar Breakdown by Item")
            st.plotly_chart(fig, use_container_width=True)

        # Edit/Delete Logs
        st.subheader("Manage Your Logs")
        log_to_edit = st.selectbox("Select a log to edit/delete", options=[f"{log['item']} ({log['date'][:10]})" for log in st.session_state.logs])
        if log_to_edit:
            index = [f"{log['item']} ({log['date'][:10]})" for log in st.session_state.logs].index(log_to_edit)
            log = st.session_state.logs[index]
            with st.form(f"edit_log_{index}"):
                new_item = st.text_input("Item", value=log['item'])
                new_sugar = st.number_input("Sugar (g)", value=log['sugar'], min_value=0)
                update = st.form_submit_button("Update Log")
                delete = st.form_submit_button("Delete Log")
                if update:
                    st.session_state.logs[index] = {**log, 'item': new_item, 'sugar': new_sugar}
                    st.success("Log updated!")
                    st.rerun()
                if delete:
                    del st.session_state.logs[index]
                    st.success("Log deleted!")
                    st.rerun()

        if st.session_state.streak > 0:
            st.success(random.choice([
                "You're crushing it—keep the streak alive!",
                "Small changes add up. Proud of you!",
                "Sugar reduction hero in the making!"
            ]))
        else:
            st.warning("Log today to restart your streak!")
    else:
        st.info("Log some items first to unlock insights!")

# ---------------- Goals Page ---------------- #
elif page == "Goals":
    st.title("🎯 Your Goals")
    st.markdown("Set and track your sugar reduction goals!")

    col1, col2 = st.columns(2)
    with col1:
        weekly_goal = st.number_input("Weekly Sugar Goal (g)", value=st.session_state.goals['weekly_sugar'], min_value=50, step=10)
    with col2:
        streak_goal = st.number_input("Streak Target (days)", value=st.session_state.goals['streak_target'], min_value=7, step=1)

    if st.button("Update Goals"):
        st.session_state.goals = {'weekly_sugar': weekly_goal, 'streak_target': streak_goal}
        st.success("Goals updated!")

    # Progress towards goals
    this_week_sugar = sum(log['sugar'] for log in st.session_state.logs if pd.to_datetime(log['date']).isocalendar()[1] == datetime.now().isocalendar()[1])
    weekly_progress = min(this_week_sugar / weekly_goal, 1.0)
    streak_progress = min(st.session_state.streak / streak_goal, 1.0)

    st.subheader("Goal Progress")
    st.progress(weekly_progress, text=f"Weekly Sugar: {this_week_sugar}/{weekly_goal}g ({'On Track' if weekly_progress < 0.8 else 'Close to Goal!'})")
    st.progress(streak_progress, text=f"Streak: {st.session_state.streak}/{streak_goal} days ({'Keep Going!' if streak_progress < 1 else 'Goal Achieved!'})")

# ---------------- Settings Page ---------------- #
elif page == "Settings":
    st.title("⚙️ Settings")
    st.markdown("Customize your experience!")

    # Change Daily Budget
    new_budget = st.number_input("Set Daily Sugar Budget (g)", min_value=10, max_value=200, value=st.session_state.daily_budget, step=5)
    if st.button("Update Budget"):
        st.session_state.daily_budget = new_budget
        st.success(f"Budget updated to {new_budget}g!")

    # Reset All Data
    if st.button("Reset All Data (Caution!)"):
        st.session_state.logs = []
        st.session_state.streak = 0
        st.session_state.last_log_date = None
        st.session_state.badges = []
        st.session_state.challenges = []
        st.success("All data reset!")
        st.rerun()

# ---------------- Footer ---------------- #
st.markdown("---")
st.caption("Prototype with Streamlit & Plotly. Highly interactive with editing, goals, and dynamic updates!")
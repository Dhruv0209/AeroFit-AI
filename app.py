"""
AI Fitness and Diet Planner
Modern, premium-quality fitness dashboard with separate workout and diet planners,
persistent user history, and AI coaching.
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Local modules
import database
import ai_service
import styles
import ui_components

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AeroFit AI — Premium Fitness & Diet Architecture",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS styles
st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)


# ---------------- SESSION STATE & AUTH INITIALIZATION ---------------- #

def init_session_state():
    """Ensure user session state is configured."""
    if "user" not in st.session_state or not st.session_state["user"]:
        demo_user = database.get_default_demo_user()
        st.session_state["user"] = demo_user

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "📊 Dashboard"


init_session_state()
current_user = st.session_state["user"]
user_id = current_user["id"] if current_user else 1


# ---------------- SIDEBAR NAVIGATION & AUTH ---------------- #

with st.sidebar:
    ui_components.render_html("""
        <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.08);">
            <div style="background: linear-gradient(135deg, #10B981, #06B6D4); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">⚡</div>
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em;">AeroFit AI</div>
                <div style="font-size: 0.72rem; color: #10B981; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">Elite Performance</div>
            </div>
        </div>
    """)

    # User Profile Chip
    ui_components.render_html(f"""
        <div style="background: rgba(18, 24, 42, 0.9); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 0.85rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">{current_user.get('name', 'Athlete')}</span>
                <span class="pill-badge pill-green" style="font-size: 0.7rem;">PRO</span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Goal: <span style="color: #38BDF8; font-weight: 600;">{current_user.get('fitness_goal', 'Fitness')}</span></div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.2rem;">{current_user.get('weight_kg', 75)} kg &rarr; {current_user.get('target_weight_kg', 70)} kg</div>
        </div>
    """)

    # Navigation menu
    nav_options = [
        "📊 Dashboard",
        "🏋️‍♂️ Workout Planner",
        "🥗 Diet Planner",
        "📜 History & Logs",
        "💬 AI Coach",
        "⚙️ Profile Settings"
    ]

    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state["current_page"]) if st.session_state["current_page"] in nav_options else 0,
        label_visibility="collapsed"
    )
    st.session_state["current_page"] = selected_nav

    st.markdown("---")

    # Account management expander
    with st.expander("👤 Switch or Register Account"):
        auth_mode = st.radio("Mode", ["Switch Profile", "Register New Profile"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Switch Profile":
            username_input = st.text_input("Username", value="", key="login_user")
            password_input = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", type="primary", use_container_width=True):
                auth_user = database.authenticate_user(username_input, password_input)
                if auth_user:
                    st.session_state["user"] = auth_user
                    st.success(f"Welcome back, {auth_user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. (Demo: demo_athlete / fitness123)")

        else:
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            new_name = st.text_input("Full Name", value="", key="reg_name")
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_user and new_pass and new_name:
                    uid = database.register_user(new_user, new_pass, new_name)
                    if uid:
                        st.session_state["user"] = database.get_user_by_id(uid)
                        st.success(f"Account created! Welcome, {new_name}.")
                        st.rerun()
                    else:
                        st.error("Username already taken.")
                else:
                    st.warning("Please fill in all fields.")

    ui_components.render_html("""
        <div style="font-size: 0.75rem; color: #64748B; text-align: center; margin-top: 2rem;">
            AeroFit AI v2.5 &bull; Powered by Groq
        </div>
    """)


# ==============================================================================
# 1. DASHBOARD PAGE
# ==============================================================================
if st.session_state["current_page"] == "📊 Dashboard":
    ui_components.render_hero(
        title=f"Welcome back, {current_user.get('name', 'Athlete')}",
        subtitle="Here is your personal fitness command center. Track your progress, active protocols, and daily targets.",
        badge="ATHLETE OVERVIEW"
    )

    # Compute Biometrics (BMI, TDEE, Calorie Deficit/Surplus)
    weight = current_user.get("weight_kg", 75.0)
    target_weight = current_user.get("target_weight_kg", 70.0)
    height = current_user.get("height_cm", 175.0)
    age = current_user.get("age", 28)
    gender = current_user.get("gender", "Male")
    goal = current_user.get("fitness_goal", "Weight Loss")
    activity = current_user.get("activity_level", "Moderately Active")

    height_m = height / 100.0
    bmi = round(weight / (height_m * height_m), 1) if height_m > 0 else 22.0
    bmi_status = "Normal" if 18.5 <= bmi <= 24.9 else ("Overweight" if bmi > 24.9 else "Underweight")
    bmi_pill = "green" if bmi_status == "Normal" else "coral"

    nutrition_est = ai_service.calculate_nutrition_estimates(weight, height, age, gender, goal, activity)
    stats = database.get_user_activity_stats(user_id)

    # Active Plans
    active_workout = database.get_active_workout_plan(user_id)
    active_diet = database.get_active_diet_plan(user_id)

    # Key Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        diff = round(weight - target_weight, 1)
        sub_str = f"{abs(diff)} kg to go" if diff != 0 else "Goal achieved!"
        ui_components.render_stat_box(
            label="Current Weight",
            value=f"{weight} kg",
            subtext=f"Target: {target_weight} kg ({sub_str})",
            pill_label="BODY STAT",
            pill_type="blue"
        )
    with m_col2:
        ui_components.render_stat_box(
            label="Body Mass Index",
            value=f"{bmi}",
            subtext=f"Category: {bmi_status}",
            pill_label=bmi_status.upper(),
            pill_type=bmi_pill
        )
    with m_col3:
        target_cals = active_diet.get("target_calories") if active_diet else nutrition_est["target_calories"]
        ui_components.render_stat_box(
            label="Daily Calorie Goal",
            value=f"{target_cals:,} kcal",
            subtext=f"Est. TDEE: {nutrition_est['tdee']} kcal",
            pill_label="ENERGY TARGET",
            pill_type="green"
        )
    with m_col4:
        ui_components.render_stat_box(
            label="Today's Exercises Completed",
            value=f"{stats['today_completed_exercises']}",
            subtext=f"All-time total: {stats['total_completed_exercises']}",
            pill_label="DISCIPLINE",
            pill_type="purple"
        )

    st.write("")

    # Today's Action Center: 2 Columns (Workout Card vs Diet Card)
    c_left, c_right = st.columns([1, 1])

    with c_left:
        ui_components.render_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                <h3 style="margin: 0; color: #FFFFFF; font-size: 1.25rem;">🏋️‍♂️ Active Workout Plan</h3>
            </div>
        """)

        if active_workout and "plan_data" in active_workout:
            wp_data = active_workout["plan_data"]
            ui_components.render_html(f"""
                <div class="fitness-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #FFFFFF;">{wp_data.get('title', active_workout.get('title', 'Active Workout'))}</h4>
                        <span class="pill-badge pill-green">{wp_data.get('split_name', 'Split')}</span>
                    </div>
                    <p style="color: #94A3B8; font-size: 0.875rem;">{wp_data.get('summary', 'Tailored workout schedule.')}</p>
                    <div style="display: flex; gap: 0.75rem; font-size: 0.8rem; color: #CBD5E1; margin: 0.75rem 0;">
                        <span>🎯 <b>Goal:</b> {active_workout.get('goal', goal)}</span>
                        <span>📅 <b>Frequency:</b> {wp_data.get('days_per_week', 4)} days/wk</span>
                    </div>
                </div>
            """)

            if st.button("👉 View Full Workout Schedule", key="dash_view_workout", type="primary", use_container_width=True):
                st.session_state["current_page"] = "🏋️‍♂️ Workout Planner"
                st.rerun()
        else:
            ui_components.render_html("""
                <div class="fitness-card" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <h4 style="color: #FFFFFF; margin-bottom: 0.5rem;">No Active Workout Plan</h4>
                    <p style="color: #94A3B8; font-size: 0.875rem; margin-bottom: 1rem;">Generate a customized day-wise workout schedule designed for your equipment and goals.</p>
                </div>
            """)
            if st.button("🚀 Create Workout Plan", key="dash_create_workout", type="primary", use_container_width=True):
                st.session_state["current_page"] = "🏋️‍♂️ Workout Planner"
                st.rerun()

    with c_right:
        ui_components.render_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                <h3 style="margin: 0; color: #FFFFFF; font-size: 1.25rem;">🥗 Active Nutrition Plan</h3>
            </div>
        """)

        if active_diet and "plan_data" in active_diet:
            dp_data = active_diet["plan_data"]
            targets = dp_data.get("daily_targets", {})
            ui_components.render_html(f"""
                <div class="fitness-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #FFFFFF;">{dp_data.get('title', active_diet.get('title', 'Active Nutrition'))}</h4>
                        <span class="pill-badge pill-blue">{active_diet.get('diet_type', 'Diet')}</span>
                    </div>
                    <div style="display: flex; gap: 0.75rem; font-size: 0.85rem; color: #CBD5E1; margin: 0.75rem 0;">
                        <span>🔥 <b>Calories:</b> {targets.get('calories', active_diet.get('target_calories', 2000))} kcal</span>
                        <span>🥩 <b>Protein:</b> {targets.get('protein_g', active_diet.get('target_protein', 150))}g</span>
                        <span>🥑 <b>Fats:</b> {targets.get('fats_g', 65)}g</span>
                    </div>
                </div>
            """)

            if st.button("👉 View Full Meal Schedule & Macros", key="dash_view_diet", type="primary", use_container_width=True):
                st.session_state["current_page"] = "🥗 Diet Planner"
                st.rerun()
        else:
            ui_components.render_html("""
                <div class="fitness-card" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🥑</div>
                    <h4 style="color: #FFFFFF; margin-bottom: 0.5rem;">No Active Diet Plan</h4>
                    <p style="color: #94A3B8; font-size: 0.875rem; margin-bottom: 1rem;">Generate a personalized meal breakdown with breakfast, lunch, dinner, snacks and exact macros.</p>
                </div>
            """)
            if st.button("🚀 Create Diet Plan", key="dash_create_diet", type="primary", use_container_width=True):
                st.session_state["current_page"] = "🥗 Diet Planner"
                st.rerun()

    # Quick Access Footer Bar
    st.write("")
    st.markdown("### ⚡ Quick Shortcuts")
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        if st.button("📜 View Plan History & Past Activity", use_container_width=True):
            st.session_state["current_page"] = "📜 History & Logs"
            st.rerun()
    with q_col2:
        if st.button("💬 Ask Aero AI Coach", use_container_width=True):
            st.session_state["current_page"] = "💬 AI Coach"
            st.rerun()
    with q_col3:
        if st.button("⚙️ Update Body Metrics & Goals", use_container_width=True):
            st.session_state["current_page"] = "⚙️ Profile Settings"
            st.rerun()


# ==============================================================================
# 2. WORKOUT PLANNER PAGE
# ==============================================================================
elif st.session_state["current_page"] == "🏋️‍♂️ Workout Planner":
    ui_components.render_hero(
        title="Workout Planner & Routine Tracker",
        subtitle="Generate and execute your day-wise training split with precision sets, reps, rest intervals, and exercise completion tracking.",
        badge="STRENGTH & CONDITIONING"
    )

    active_workout = database.get_active_workout_plan(user_id)

    w_tab1, w_tab2 = st.tabs(["📋 Current Active Workout Routine", "⚡ Generate New Workout Plan"])

    with w_tab1:
        if active_workout:
            ui_components.render_workout_interactive_schedule(active_workout, user_id)
        else:
            st.info("You don't have an active workout plan yet. Create one in the 'Generate New Workout Plan' tab above!")

    with w_tab2:
        ui_components.render_html("""
            <div class="fitness-card">
                <h4 style="margin-top: 0; color: #FFFFFF;">Configure Your Training Parameters</h4>
                <p style="color: #94A3B8; font-size: 0.875rem;">Our AI will design an optimized periodized program tailored to your goals, available gym equipment, and weekly schedule.</p>
            </div>
        """)

        with st.form("workout_generator_form"):
            col1, col2 = st.columns(2)

            with col1:
                w_goal = st.selectbox(
                    "Primary Fitness Goal",
                    [
                        "Weight Loss & Muscle Definition",
                        "Hypertrophy (Muscle Size)",
                        "Strength & Power",
                        "Athletic Conditioning & Endurance",
                        "Lean Body Recomposition"
                    ],
                    index=0
                )
                w_experience = st.selectbox(
                    "Experience Level",
                    ["Beginner (0-1 years)", "Intermediate (1-3 years)", "Advanced (3+ years)"],
                    index=1
                )
                w_split = st.selectbox(
                    "Preferred Training Split",
                    [
                        "Push / Pull / Legs (PPL)",
                        "Upper / Lower Body Split",
                        "Full Body (3-4 Days/Week)",
                        "5-Day Bro Split (Chest, Back, Legs, Shoulders, Arms)",
                        "HIIT & Bodyweight Functional Circuit"
                    ],
                    index=0
                )
                w_days = st.slider("Training Days per Week", min_value=2, max_value=6, value=4)

            with col2:
                w_equipment = st.selectbox(
                    "Available Equipment",
                    [
                        "Full Commercial Gym (Barbells, Cables, Dumbbells, Machines)",
                        "Home Gym with Dumbbells & Bench",
                        "Resistance Bands & Pull-Up Bar",
                        "Bodyweight / Calisthenics Only"
                    ],
                    index=0
                )
                w_duration_mins = st.selectbox("Session Duration", ["30-45 minutes", "45-60 minutes", "60-75 minutes"], index=1)
                w_health = st.text_input("Injuries or Joint Restrictions", placeholder="e.g. Mild lower back sensitivity, avoid overhead press")
                w_comments = st.text_area("Specific Priorities or Muscle Focus", placeholder="e.g. Focus on chest development, include core finishers")

            submit_workout = st.form_submit_button("⚡ Generate Personalized Workout Protocol", type="primary", use_container_width=True)

        if submit_workout:
            with st.spinner("🧠 AeroFit AI is formulating your periodized workout protocol..."):
                try:
                    prefs = {
                        "goal": w_goal,
                        "experience_level": w_experience,
                        "split_type": w_split,
                        "equipment": w_equipment,
                        "days_per_week": w_days,
                        "session_duration": w_duration_mins,
                        "health_conditions": w_health,
                        "comments": w_comments,
                    }
                    generated = ai_service.generate_workout_plan(current_user, prefs)
                    new_plan_id = database.save_workout_plan(
                        user_id=user_id,
                        title=generated["title"],
                        plan_data=generated["plan_data"],
                        raw_markdown=generated.get("raw_markdown", ""),
                        goal=w_goal,
                        experience_level=w_experience,
                        split_type=w_split,
                        equipment=w_equipment,
                        duration_weeks=4
                    )
                    st.success("🎉 Your new personalized workout protocol is ready and activated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating workout plan: {e}")


# ==============================================================================
# 3. DIET PLANNER PAGE
# ==============================================================================
elif st.session_state["current_page"] == "🥗 Diet Planner":
    ui_components.render_hero(
        title="Personalized Nutrition & Diet Planner",
        subtitle="Day-to-day culinary meal plans structured with exact portion sizes, daily calorie targets, and macronutrient distributions.",
        badge="CLINICAL & SPORTS NUTRITION"
    )

    active_diet = database.get_active_diet_plan(user_id)

    d_tab1, d_tab2 = st.tabs(["🍽️ Current Active Diet Plan", "⚡ Generate New Nutrition Plan"])

    with d_tab1:
        if active_diet:
            ui_components.render_diet_interactive_plan(active_diet, user_id)
        else:
            st.info("You don't have an active diet plan yet. Generate one in the 'Generate New Nutrition Plan' tab above!")

    with d_tab2:
        ui_components.render_html("""
            <div class="fitness-card">
                <h4 style="margin-top: 0; color: #FFFFFF;">Configure Your Dietary Profile</h4>
                <p style="color: #94A3B8; font-size: 0.875rem;">Calculates accurate thermodynamic caloric requirements and maps out high-satiety meals for Breakfast, Lunch, Dinner, and Snacks.</p>
            </div>
        """)

        with st.form("diet_generator_form"):
            col1, col2 = st.columns(2)

            with col1:
                d_type = st.selectbox(
                    "Dietary Preference",
                    [
                        "High-Protein Balanced (Non-Vegetarian)",
                        "High-Protein Vegetarian (Paneer, Tofu, Legumes)",
                        "Indian Balanced Vegetarian",
                        "Mediterranean Diet",
                        "Vegan / 100% Plant-Based",
                        "Ketogenic (Low Carb, High Fat)",
                        "Low Carb / Paleo"
                    ],
                    index=0
                )
                d_meals_count = st.selectbox("Meals per Day", [3, 4, 5], index=1, format_func=lambda x: f"{x} Meals (e.g. Breakfast, Lunch, Snacks, Dinner)")
                d_allergies = st.text_input("Dietary Restrictions / Allergies", placeholder="e.g. Lactose intolerant, peanut allergy, gluten sensitive")

            with col2:
                # Pre-calculate recommended calories
                est_nutr = ai_service.calculate_nutrition_estimates(
                    current_user.get("weight_kg", 75.0),
                    current_user.get("height_cm", 175.0),
                    current_user.get("age", 28),
                    current_user.get("gender", "Male"),
                    current_user.get("fitness_goal", "Weight Loss"),
                    current_user.get("activity_level", "Moderately Active")
                )
                d_cal_target = st.number_input(
                    "Target Daily Calories (kcal)",
                    min_value=1200,
                    max_value=5000,
                    value=est_nutr["target_calories"],
                    step=50,
                    help=f"Estimated based on Mifflin-St Jeor formula (TDEE ~{est_nutr['tdee']} kcal)"
                )
                d_health_cond = st.text_input("Health Conditions", placeholder="e.g. High blood pressure, pre-diabetic, none")
                d_comments = st.text_area("Food Preferences or Dislikes", placeholder="e.g. Prefer quick 15-minute prep meals, include coffee")

            submit_diet = st.form_submit_button("⚡ Generate Personalized Nutrition Plan", type="primary", use_container_width=True)

        if submit_diet:
            with st.spinner("🧠 AeroFit AI is crafting your macronutrient and meal blueprint..."):
                try:
                    prefs = {
                        "diet_type": d_type,
                        "meals_per_day": d_meals_count,
                        "dietary_restrictions": d_allergies,
                        "health_conditions": d_health_cond,
                        "comments": d_comments,
                        "target_calories": d_cal_target,
                    }
                    generated_diet = ai_service.generate_diet_plan(current_user, prefs)
                    new_diet_id = database.save_diet_plan(
                        user_id=user_id,
                        title=generated_diet["title"],
                        plan_data=generated_diet["plan_data"],
                        raw_markdown=generated_diet.get("raw_markdown", ""),
                        diet_type=generated_diet.get("diet_type", d_type),
                        target_calories=generated_diet.get("target_calories", d_cal_target),
                        target_protein=generated_diet.get("target_protein", 150),
                        target_carbs=generated_diet.get("target_carbs", 200),
                        target_fats=generated_diet.get("target_fats", 65)
                    )
                    st.success("🎉 Your personalized nutrition plan has been generated and set as active!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating diet plan: {e}")


# ==============================================================================
# 4. HISTORY & LOGS PAGE
# ==============================================================================
elif st.session_state["current_page"] == "📜 History & Logs":
    ui_components.render_hero(
        title="Activity Log & Plan History",
        subtitle="Review previously generated protocols, reactivate any past training or diet blueprint without re-generating, and inspect your discipline records.",
        badge="PERSISTENT ARCHIVE"
    )

    stats = database.get_user_activity_stats(user_id)

    # Summary Row
    h_c1, h_c2, h_c3, h_c4 = st.columns(4)
    with h_c1:
        ui_components.render_stat_box("Total Workout Plans", f"{stats['total_workout_plans']}", "Saved in database", "WORKOUTS", "green")
    with h_c2:
        ui_components.render_stat_box("Total Diet Plans", f"{stats['total_diet_plans']}", "Saved in database", "NUTRITION", "blue")
    with h_c3:
        ui_components.render_stat_box("Exercises Logged Today", f"{stats['today_completed_exercises']}", "Marked complete", "TODAY", "coral")
    with h_c4:
        ui_components.render_stat_box("All-Time Completed", f"{stats['total_completed_exercises']}", "Total completed sets/exercises", "ALL-TIME", "purple")

    st.write("")
    ui_components.render_history_section(user_id)


# ==============================================================================
# 5. AI COACH CONVERSATION
# ==============================================================================
elif st.session_state["current_page"] == "💬 AI Coach":
    ui_components.render_hero(
        title="Aero Fitness & Nutrition AI Coach",
        subtitle="Your real-time sports coach with complete context of your biometrics, active workout split, and meal targets.",
        badge="REAL-TIME ASSISTANT"
    )

    active_workout = database.get_active_workout_plan(user_id)
    active_diet = database.get_active_diet_plan(user_id)

    # Prompt recommendations
    ui_components.render_html("""
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600; align-self: center;">Quick Prompts:</span>
        </div>
    """)

    quick_col1, quick_col2, quick_col3 = st.columns(3)
    preset_query = None
    with quick_col1:
        if st.button("💡 Substitute an exercise I can't do", key="qp1", use_container_width=True):
            preset_query = "I don't have access to one of the exercises in my active workout. What is an effective alternative exercise with similar muscle recruitment?"
    with quick_col2:
        if st.button("🥑 Healthy high-protein snack idea", key="qp2", use_container_width=True):
            preset_query = "Give me 3 quick, delicious high-protein snack ideas (20g+ protein) that fit into my active nutrition plan."
    with quick_col3:
        if st.button("💤 How to optimize recovery & soreness", key="qp3", use_container_width=True):
            preset_query = "What are the most evidence-based strategies to reduce delayed onset muscle soreness (DOMS) and speed up muscle recovery?"

    # Load persistent chat history from DB
    db_history = database.get_chat_history(user_id, limit=30)
    for msg in db_history:
        avatar = "⚡" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input
    user_query = st.chat_input("Ask Coach Aero about your workout, diet, form, or motivation...")
    if preset_query and not user_query:
        user_query = preset_query

    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        database.save_chat_message(user_id, "user", user_query)

        # Generate response from AI
        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Coach Aero is analyzing your request..."):
                all_msgs = database.get_chat_history(user_id, limit=10)
                reply = ai_service.ask_fitness_coach(all_msgs, current_user, active_workout, active_diet)
                st.markdown(reply)
                database.save_chat_message(user_id, "assistant", reply)

    if st.button("🧹 Clear Chat History", type="secondary"):
        database.clear_chat_history(user_id)
        st.success("Chat history cleared.")
        st.rerun()


# ==============================================================================
# 6. PROFILE & SETTINGS PAGE
# ==============================================================================
elif st.session_state["current_page"] == "⚙️ Profile Settings":
    ui_components.render_hero(
        title="Biometric Profile & Target Settings",
        subtitle="Keep your physiological metrics up to date so all future workout protocols and caloric calculations adapt dynamically.",
        badge="METRIC CALIBRATION"
    )

    with st.form("profile_update_form"):
        p_c1, p_c2 = st.columns(2)

        with p_c1:
            p_name = st.text_input("Full Name", value=current_user.get("name", "Athlete"))
            p_age = st.number_input("Age", min_value=12, max_value=100, value=current_user.get("age", 28))
            p_gender = st.selectbox("Biological Gender", ["Male", "Female", "Other"], index=0 if current_user.get("gender") == "Male" else 1)
            p_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(current_user.get("height_cm", 175.0)), step=0.5)

        with p_c2:
            p_weight = st.number_input("Current Body Weight (kg)", min_value=30.0, max_value=250.0, value=float(current_user.get("weight_kg", 75.0)), step=0.5)
            p_target_weight = st.number_input("Target Goal Weight (kg)", min_value=30.0, max_value=250.0, value=float(current_user.get("target_weight_kg", 70.0)), step=0.5)
            p_goal = st.selectbox(
                "Primary Fitness Goal",
                [
                    "Weight Loss & Muscle Definition",
                    "Hypertrophy (Muscle Gain)",
                    "Maximum Strength & Power",
                    "Athletic Conditioning & Stamina",
                    "Maintenance & Longevity"
                ],
                index=0
            )
            p_activity = st.selectbox(
                "Activity Level",
                ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                index=2
            )

        submit_profile = st.form_submit_button("💾 Save Profile Changes", type="primary", use_container_width=True)

    if submit_profile:
        ok = database.update_user_profile(
            user_id=user_id,
            name=p_name,
            age=p_age,
            gender=p_gender,
            height_cm=p_height,
            weight_kg=p_weight,
            target_weight_kg=p_target_weight,
            fitness_goal=p_goal,
            activity_level=p_activity
        )
        if ok:
            st.session_state["user"] = database.get_user_by_id(user_id)
            st.success("✅ Profile updated successfully! Your biometric targets have been recalculated.")
            st.rerun()
        else:
            st.error("Failed to update profile.")

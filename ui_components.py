"""
Reusable UI Components for AI Fitness Planner
Renders interactive workout day schedules, meal cards, macro summaries,
metric cards, and history views with consistent styling.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import database


def render_html(html: str):
    """
    Safely render HTML without Markdown converting indented lines or blank lines
    into verbatim <pre><code> blocks.
    """
    cleaned = "".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, badge: str = "AI POWERED PROTOCOL"):
    """Render a modern header section."""
    render_html(f"""
        <div class="hero-container">
            <span class="hero-badge">⚡ {badge}</span>
            <div class="hero-title">{title}</div>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    """)


def render_stat_box(label: str, value: str, subtext: str = "", pill_label: Optional[str] = None, pill_type: str = "green"):
    """Render a single dashboard metric widget."""
    pill_html = f'<span class="pill-badge pill-{pill_type}">{pill_label}</span>' if pill_label else ""
    render_html(f"""
        <div class="stat-box">
            <div class="stat-label">
                <span>{label}</span>
                {pill_html}
            </div>
            <div class="stat-value">{value}</div>
            <div class="stat-subtext">{subtext}</div>
        </div>
    """)


def render_macro_breakdown(calories: int, protein: int, carbs: int, fats: int):
    """Render visual macronutrient bars and cards without markdown codeblock artifacts."""
    total_cal = max(1, calories)
    p_cal = protein * 4
    c_cal = carbs * 4
    f_cal = fats * 9

    p_pct = min(100, int((p_cal / total_cal) * 100))
    c_pct = min(100, int((c_cal / total_cal) * 100))
    f_pct = min(100, int((f_cal / total_cal) * 100))

    render_html(f"""
        <div class="fitness-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <h4 style="margin: 0; color: #FFFFFF; font-size: 1.2rem; font-weight: 700;">Daily Target Nutrition Breakdown</h4>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">Thermodynamic caloric & macronutrient targets</div>
                </div>
                <span class="pill-badge pill-green" style="font-size: 0.95rem; padding: 0.35rem 0.85rem;">🔥 {calories:,} kcal / day</span>
            </div>

            <div style="display: flex; gap: 0.85rem; margin-bottom: 1.25rem; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 140px; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); padding: 1rem; border-radius: 12px; text-align: center;">
                    <span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em;">Protein</span>
                    <div style="font-size: 1.75rem; font-weight: 800; color: #34D399; font-family: 'Space Grotesk', sans-serif; margin: 0.2rem 0;">{protein}g</div>
                    <span style="font-size: 0.75rem; color: #A7F3D0; font-weight: 600;">{p_pct}% of calories</span>
                </div>
                <div style="flex: 1; min-width: 140px; background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.25); padding: 1rem; border-radius: 12px; text-align: center;">
                    <span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em;">Carbohydrates</span>
                    <div style="font-size: 1.75rem; font-weight: 800; color: #38BDF8; font-family: 'Space Grotesk', sans-serif; margin: 0.2rem 0;">{carbs}g</div>
                    <span style="font-size: 0.75rem; color: #BAE6FD; font-weight: 600;">{c_pct}% of calories</span>
                </div>
                <div style="flex: 1; min-width: 140px; background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.25); padding: 1rem; border-radius: 12px; text-align: center;">
                    <span style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em;">Healthy Fats</span>
                    <div style="font-size: 1.75rem; font-weight: 800; color: #FB7185; font-family: 'Space Grotesk', sans-serif; margin: 0.2rem 0;">{fats}g</div>
                    <span style="font-size: 0.75rem; color: #FECDD3; font-weight: 600;">{f_pct}% of calories</span>
                </div>
            </div>

            <div class="macro-progress-container">
                <div class="macro-bar-label"><span>🥩 Protein Target ({protein}g)</span><span style="color: #34D399;">{p_pct}% of calories</span></div>
                <div class="macro-bar-track"><div class="macro-bar-fill-green" style="width: {p_pct}%;"></div></div>
            </div>
            <div class="macro-progress-container">
                <div class="macro-bar-label"><span>🍚 Carbohydrates Target ({carbs}g)</span><span style="color: #38BDF8;">{c_pct}% of calories</span></div>
                <div class="macro-bar-track"><div class="macro-bar-fill-blue" style="width: {c_pct}%;"></div></div>
            </div>
            <div class="macro-progress-container">
                <div class="macro-bar-label"><span>🥑 Healthy Fats Target ({fats}g)</span><span style="color: #FB7185;">{f_pct}% of calories</span></div>
                <div class="macro-bar-track"><div class="macro-bar-fill-coral" style="width: {f_pct}%;"></div></div>
            </div>
        </div>
    """)


def render_single_meal_card(meal: Dict[str, Any], m_idx: int, is_done: bool, plan_id: int, user_id: int, today_str: str):
    """Render an individual meal card with food items, portion sizes, macro pills, and completion toggle."""
    items = meal.get("items", [])
    m_name = meal.get("name", f"Meal {m_idx + 1}")
    m_time = meal.get("time", "")
    time_badge = f'<span class="pill-badge pill-purple">⏰ {m_time}</span>' if m_time else ""
    meal_key = f"meal_{m_idx}"

    status_pill = '<span class="pill-badge pill-green">COMPLETED</span>' if is_done else '<span class="pill-badge pill-blue">PLANNED</span>'
    card_border = "border-left: 4px solid #10B981;" if is_done else "border-left: 4px solid #06B6D4;"
    bg_style = "background: rgba(16, 185, 129, 0.04);" if is_done else "background: rgba(15, 21, 37, 0.9);"

    items_html = ""
    for it in items:
        food_name = it.get("food", it.get("item", "Nutritious Food Item"))
        portion = it.get("portion", "1 serving")
        f_cal = it.get("calories", 0)
        f_p = it.get("protein", 0)
        f_c = it.get("carbs", 0)
        f_f = it.get("fats", 0)

        items_html += f"""
            <div class="meal-food-item">
                <div>
                    <div class="food-desc">🥗 {food_name}</div>
                    <div class="food-portion">Portion: <b>{portion}</b></div>
                </div>
                <div class="food-macros">
                    <span style="color: #34D399; background: rgba(16,185,129,0.1); padding: 2px 6px; border-radius: 4px;">{f_p}g P</span>
                    <span style="color: #38BDF8; background: rgba(6,182,212,0.1); padding: 2px 6px; border-radius: 4px;">{f_c}g C</span>
                    <span style="color: #FB7185; background: rgba(244,63,94,0.1); padding: 2px 6px; border-radius: 4px;">{f_f}g F</span>
                    <span style="color: #F8FAFC; font-weight: 700; padding: 2px 6px;">{f_cal} kcal</span>
                </div>
            </div>
        """

    instructions = meal.get("instructions", "")
    instr_html = f"""
        <div style="margin-top: 0.85rem; padding: 0.65rem 0.85rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px; font-size: 0.825rem; color: #CBD5E1;">
            <b style="color: #38BDF8;">💡 Preparation & Nutrition Note:</b> {instructions}
        </div>
    """ if instructions else ""

    render_html(f"""
        <div class="meal-card" style="{card_border} {bg_style}">
            <div class="meal-header">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <h4 class="meal-title">{m_name}</h4>
                    {status_pill}
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                    {time_badge}
                    <span class="pill-badge pill-green">🔥 {meal.get('total_calories', 'N/A')} kcal</span>
                    <span class="pill-badge pill-blue">🥩 {meal.get('protein_g', 'N/A')}g Protein</span>
                </div>
            </div>
            {items_html}
            {instr_html}
        </div>
    """)

    btn_label = "✅ Mark Meal as Not Eaten" if is_done else "🍴 Mark Meal as Eaten Today"
    btn_type = "secondary" if is_done else "primary"
    if st.button(btn_label, key=f"btn_meal_{plan_id}_{meal_key}", type=btn_type):
        database.toggle_activity_status(user_id, "diet", plan_id, meal_key, today_str)
        st.rerun()


def render_diet_interactive_plan(plan: Dict[str, Any], user_id: int):
    """Render structured meal plan with meal-by-meal cards, tabs, and macro totals."""
    plan_data = plan.get("plan_data", {})
    meals = plan_data.get("meals", [])
    targets = plan_data.get("daily_targets", {})
    plan_id = plan.get("id", 0)

    if not meals:
        st.info("No meal schedule available in this diet plan.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    completed_meals = database.get_completed_items_set(user_id, "diet", plan_id, today_str)

    # 1. Macro summary breakdown
    cal = targets.get("calories", plan.get("target_calories", 2000))
    prot = targets.get("protein_g", plan.get("target_protein", 150))
    carb = targets.get("carbs_g", plan.get("target_carbs", 200))
    fat = targets.get("fats_g", plan.get("target_fats", 65))

    render_macro_breakdown(calories=cal, protein=prot, carbs=carb, fats=fat)

    # 2. Plan overview details banner
    render_html(f"""
        <div class="fitness-card-gradient" style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <h3 style="margin: 0; color: #FFFFFF;">{plan_data.get('title', plan.get('title', 'Custom Nutrition Protocol'))}</h3>
                    <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 3px;">Personalized day-to-day culinary meal architecture</div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="pill-badge pill-purple">{plan.get('diet_type', 'Diet Protocol')}</span>
                    <span class="pill-badge pill-green">{len(completed_meals)} / {len(meals)} Meals Eaten Today</span>
                </div>
            </div>
        </div>
    """)

    # 3. Meal Schedule Tabs (Interactive per-meal and full view)
    meal_tab_labels = []
    emojis = ["🌅", "☀️", "🥪", "🌙", "🍎", "🥗"]
    for m_idx, meal in enumerate(meals):
        em = emojis[m_idx % len(emojis)]
        is_done = f"meal_{m_idx}" in completed_meals
        checkmark = "✅ " if is_done else ""
        meal_tab_labels.append(f"{checkmark}{em} {meal.get('name', f'Meal {m_idx+1}')}")

    meal_tab_labels.append("📋 View All Meals")

    tabs = st.tabs(meal_tab_labels)

    # Render individual tabs
    for m_idx, meal in enumerate(meals):
        with tabs[m_idx]:
            is_done = f"meal_{m_idx}" in completed_meals
            render_single_meal_card(meal, m_idx, is_done, plan_id, user_id, today_str)

    # Render "View All Meals" tab
    with tabs[-1]:
        st.markdown(f"**Showing all {len(meals)} meals in daily schedule:**")
        for m_idx, meal in enumerate(meals):
            is_done = f"meal_{m_idx}" in completed_meals
            render_single_meal_card(meal, m_idx, is_done, plan_id, user_id, today_str)
            st.write("")

    # 4. Guidelines and hydration section
    hydration = plan_data.get("hydration_liters", 3.0)
    guidelines = plan_data.get("guidelines", [])

    guideline_items_html = "".join([f"<li style='margin-bottom: 0.45rem;'>{g}</li>" for g in guidelines])

    render_html(f"""
        <div class="fitness-card" style="margin-top: 1.5rem;">
            <h4 style="margin-top: 0; color: #FFFFFF; font-size: 1.15rem; font-weight: 700;">💧 Hydration & Nutrition Guidelines</h4>
            <div style="display: flex; align-items: center; gap: 0.85rem; margin-bottom: 1rem; padding: 0.75rem 1rem; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.25); border-radius: 10px;">
                <span style="font-size: 1.8rem;">🌊</span>
                <div>
                    <div style="color: #38BDF8; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Hydration Target</div>
                    <div style="color: #F8FAFC; font-weight: 800; font-size: 1.25rem;">{hydration} Liters / day</div>
                </div>
            </div>
            <ul style="color: #94A3B8; font-size: 0.9rem; padding-left: 1.25rem; margin-bottom: 0;">
                {guideline_items_html}
            </ul>
        </div>
    """)


def render_workout_interactive_schedule(plan: Dict[str, Any], user_id: int):
    """Render day-wise workout schedule with interactive completion checkboxes."""
    plan_data = plan.get("plan_data", {})
    schedule = plan_data.get("schedule", [])
    plan_id = plan.get("id", 0)

    if not schedule:
        st.info("No day-wise workout schedule available in this plan.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    completed_items = database.get_completed_items_set(user_id, "workout", plan_id, today_str)

    # Overview banner
    render_html(f"""
        <div class="fitness-card-gradient">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.5rem;">
                <h3 style="margin: 0; color: #FFFFFF;">{plan_data.get('title', plan.get('title', 'Weekly Workout Protocol'))}</h3>
                <span class="pill-badge pill-green">{plan_data.get('experience_level', plan.get('experience_level', 'Intermediate'))} • {plan_data.get('split_name', plan.get('split_type', 'Split'))}</span>
            </div>
            <p style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 0.75rem;">{plan_data.get('summary', 'Structured training split tailored to your goals.')}</p>
            <div style="display: flex; gap: 1rem; font-size: 0.85rem; color: #CBD5E1;">
                <span>📅 <b>Frequency:</b> {plan_data.get('days_per_week', plan.get('duration_weeks', 4))} Days/Week</span>
                <span>⏱️ <b>Schedule:</b> Weekly Cycles</span>
                <span>✅ <b>Today's Completed:</b> {len(completed_items)} items</span>
            </div>
        </div>
    """)

    # Create tabs for each day
    day_titles = [f"Day {d.get('day_number', i+1)}: {d.get('day_name', 'Workout')}" for i, d in enumerate(schedule)]
    tabs = st.tabs(day_titles)

    for i, tab in enumerate(tabs):
        day = schedule[i]
        day_key = f"day_{day.get('day_number', i+1)}"
        with tab:
            render_html(f"""
                <div style="margin-bottom: 1rem; padding: 0.75rem 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">{day.get('title', 'Daily Training')}</div>
                    <div style="color: #38BDF8; font-weight: 600; font-size: 0.875rem;">Focus: {day.get('focus', 'Target Muscle Groups')}</div>
                </div>
            """)

            col_w1, col_w2 = st.columns(2)
            with col_w1:
                if day.get("warmup"):
                    render_html(f"""
                        <div style="padding: 0.75rem; background: rgba(6, 182, 212, 0.08); border-left: 3px solid #06B6D4; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem;">
                            <b style="color: #38BDF8;">🔥 Dynamic Warmup:</b><br>{day.get('warmup')}
                        </div>
                    """)
            with col_w2:
                if day.get("cooldown"):
                    render_html(f"""
                        <div style="padding: 0.75rem; background: rgba(139, 92, 246, 0.08); border-left: 3px solid #8B5CF6; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem;">
                            <b style="color: #A78BFA;">🧘 Cooldown & Mobility:</b><br>{day.get('cooldown')}
                        </div>
                    """)

            # Exercises list
            exercises = day.get("exercises", [])
            st.markdown(f"**Exercises ({len(exercises)} total)**")

            for ex_idx, ex in enumerate(exercises):
                ex_id = ex.get("id", f"{day_key}_ex_{ex_idx}")
                is_done = ex_id in completed_items

                card_class = "exercise-card completed" if is_done else "exercise-card"
                badge_html = '<span class="pill-badge pill-green">DONE</span>' if is_done else '<span class="pill-badge pill-blue">TARGET</span>'

                render_html(f"""
                    <div class="{card_class}">
                        <div class="exercise-header">
                            <span class="exercise-title">{ex_idx + 1}. {ex.get('name', 'Exercise')}</span>
                            {badge_html}
                        </div>
                        <div class="exercise-meta-grid">
                            <div class="meta-item"><span class="meta-item-label">Sets</span><span class="meta-item-val">{ex.get('sets', '3-4')}</span></div>
                            <div class="meta-item"><span class="meta-item-label">Reps</span><span class="meta-item-val">{ex.get('reps', '8-12')}</span></div>
                            <div class="meta-item"><span class="meta-item-label">Rest</span><span class="meta-item-val">{ex.get('rest', '60-90s')}</span></div>
                            <div class="meta-item"><span class="meta-item-label">Target Muscle</span><span class="meta-item-val">{ex.get('target_muscle', 'Full Body')}</span></div>
                        </div>
                        <div class="exercise-instructions"><b>Form Cue:</b> {ex.get('instructions', 'Maintain strict tempo and form.')}</div>
                    </div>
                """)

                btn_label = "✅ Mark as Incomplete" if is_done else "⭕ Mark as Completed"
                btn_type = "secondary" if is_done else "primary"
                if st.button(btn_label, key=f"btn_ex_{plan_id}_{ex_id}", type=btn_type):
                    database.toggle_activity_status(user_id, "workout", plan_id, ex_id, today_str)
                    st.rerun()

    # Recovery tips
    recovery_tips = plan_data.get("recovery_tips", [])
    if recovery_tips:
        tips_html = "".join([f"<li style='margin-bottom: 0.4rem;'>{tip}</li>" for tip in recovery_tips])
        render_html(f"""
            <div class="fitness-card" style="margin-top: 1.5rem;">
                <h4 style="margin-top: 0; color: #FFFFFF;">⚡ Coach Recovery & Performance Guidelines</h4>
                <ul style="color: #94A3B8; font-size: 0.9rem; padding-left: 1.25rem; margin-bottom: 0;">
                    {tips_html}
                </ul>
            </div>
        """)


def render_history_section(user_id: int):
    """Render historical workout and diet plans with reactivation and view capability."""
    workout_history = database.get_workout_history(user_id)
    diet_history = database.get_diet_history(user_id)

    tab_w, tab_d = st.tabs(["🏋️‍♂️ Workout Plans History", "🥗 Diet Plans History"])

    with tab_w:
        if not workout_history:
            st.info("No saved workout plans yet. Generate your first plan in the Workout Planner!")
        else:
            st.markdown(f"**Found {len(workout_history)} Workout Plans**")
            for wp in workout_history:
                is_active = wp.get("is_active") == 1
                status_pill = '<span class="pill-badge pill-green">ACTIVE PLAN</span>' if is_active else '<span class="pill-badge pill-blue">ARCHIVED</span>'
                plan_id = wp["id"]
                created_dt = wp.get("created_at", "N/A")

                with st.expander(f"{'⭐ ' if is_active else ''}{wp.get('title', 'Workout Plan')} — {created_dt}", expanded=is_active):
                    render_html(f"""
                        <div style="display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap;">
                            {status_pill}
                            <span class="pill-badge pill-purple">{wp.get('split_type', 'Split')}</span>
                            <span class="pill-badge pill-amber">{wp.get('experience_level', 'Level')}</span>
                            <span style="color: #94A3B8; font-size: 0.85rem;">Goal: <b>{wp.get('goal', 'Fitness')}</b></span>
                        </div>
                    """)

                    col_act1, col_act2 = st.columns([1, 1])
                    with col_act1:
                        if not is_active:
                            if st.button("🚀 Set as Active Plan", key=f"set_act_w_{plan_id}", type="primary"):
                                database.set_active_workout_plan(user_id, plan_id)
                                st.success("Activated! This plan is now set as your active workout.")
                                st.rerun()
                        else:
                            st.write("✅ Currently Active on Dashboard & Workout Planner")
                    with col_act2:
                        if st.button("🗑️ Delete Plan", key=f"del_w_{plan_id}", type="secondary"):
                            database.delete_workout_plan(user_id, plan_id)
                            st.rerun()

                    render_workout_interactive_schedule(wp, user_id)

    with tab_d:
        if not diet_history:
            st.info("No saved diet plans yet. Generate your first plan in the Diet Planner!")
        else:
            st.markdown(f"**Found {len(diet_history)} Diet Plans**")
            for dp in diet_history:
                is_active = dp.get("is_active") == 1
                status_pill = '<span class="pill-badge pill-green">ACTIVE PLAN</span>' if is_active else '<span class="pill-badge pill-blue">ARCHIVED</span>'
                plan_id = dp["id"]
                created_dt = dp.get("created_at", "N/A")

                with st.expander(f"{'⭐ ' if is_active else ''}{dp.get('title', 'Diet Plan')} — {created_dt}", expanded=is_active):
                    render_html(f"""
                        <div style="display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap;">
                            {status_pill}
                            <span class="pill-badge pill-green">{dp.get('target_calories', 2000)} kcal</span>
                            <span class="pill-badge pill-blue">{dp.get('target_protein', 150)}g Protein</span>
                            <span class="pill-badge pill-coral">{dp.get('diet_type', 'Diet')}</span>
                        </div>
                    """)

                    col_act1, col_act2 = st.columns([1, 1])
                    with col_act1:
                        if not is_active:
                            if st.button("🚀 Set as Active Diet Plan", key=f"set_act_d_{plan_id}", type="primary"):
                                database.set_active_diet_plan(user_id, plan_id)
                                st.success("Activated! This plan is now set as your active diet.")
                                st.rerun()
                        else:
                            st.write("✅ Currently Active on Dashboard & Diet Planner")
                    with col_act2:
                        if st.button("🗑️ Delete Plan", key=f"del_d_{plan_id}", type="secondary"):
                            database.delete_diet_plan(user_id, plan_id)
                            st.rerun()

                    render_diet_interactive_plan(dp, user_id)

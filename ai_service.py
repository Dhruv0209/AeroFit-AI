"""
AI Service for Fitness Planner
Integrates with Groq Cloud LLMs (LangChain Groq) to generate structured workout and diet plans,
with robust model fallback, JSON validation, and error recovery.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Candidate models in preference order
PREFERRED_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile"
]

_CACHED_MODEL_NAME = None


def get_available_groq_model() -> str:
    """Find the best available model supported by the Groq API key."""
    global _CACHED_MODEL_NAME
    if _CACHED_MODEL_NAME:
        return _CACHED_MODEL_NAME

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "openai/gpt-oss-120b"

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        available_ids = {m.id for m in client.models.list().data}

        for model in PREFERRED_MODELS:
            if model in available_ids:
                _CACHED_MODEL_NAME = model
                return model

        # Fallback to any model that is not whisper or guard
        for m_id in available_ids:
            if not any(skip in m_id.lower() for skip in ["whisper", "guard", "audio"]):
                _CACHED_MODEL_NAME = m_id
                return m_id
    except Exception:
        pass

    _CACHED_MODEL_NAME = "openai/gpt-oss-120b"
    return _CACHED_MODEL_NAME


def get_llm(temperature: float = 0.4):
    """Instantiate ChatGroq with the optimal available model."""
    from langchain_groq import ChatGroq
    api_key = os.getenv("GROQ_API_KEY")
    model_name = get_available_groq_model()
    return ChatGroq(api_key=api_key, model=model_name, temperature=temperature)


def calculate_nutrition_estimates(weight_kg: float, height_cm: float, age: int, gender: str, goal: str, activity_level: str) -> Dict[str, int]:
    """Calculate baseline BMR, TDEE, and macro targets based on Mifflin-St Jeor formula."""
    # BMR calculation
    if gender.lower() == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

    activity_multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extremely active": 1.9,
    }
    mult = activity_multipliers.get(activity_level.lower(), 1.45)
    tdee = int(bmr * mult)

    goal_lower = goal.lower()
    if "loss" in goal_lower or "cut" in goal_lower or "lean" in goal_lower:
        target_calories = max(1200, tdee - 450)
        protein_g = int(weight_kg * 2.2)
        fats_g = int((target_calories * 0.25) / 9)
        carbs_g = max(50, int((target_calories - (protein_g * 4 + fats_g * 9)) / 4))
    elif "gain" in goal_lower or "bulk" in goal_lower or "muscle" in goal_lower:
        target_calories = tdee + 350
        protein_g = int(weight_kg * 2.0)
        fats_g = int((target_calories * 0.25) / 9)
        carbs_g = max(80, int((target_calories - (protein_g * 4 + fats_g * 9)) / 4))
    else: # maintenance
        target_calories = tdee
        protein_g = int(weight_kg * 1.8)
        fats_g = int((target_calories * 0.28) / 9)
        carbs_g = max(70, int((target_calories - (protein_g * 4 + fats_g * 9)) / 4))

    return {
        "bmr": int(bmr),
        "tdee": tdee,
        "target_calories": target_calories,
        "target_protein": protein_g,
        "target_carbs": carbs_g,
        "target_fats": fats_g,
    }


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extract and parse JSON object from LLM response text."""
    if not text:
        return None

    # Try 1: standard markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    candidate = match.group(1) if match else text

    # Try 2: direct json parse
    try:
        return json.loads(candidate.strip())
    except Exception:
        pass

    # Try 3: find outermost braces
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = candidate[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            # Clean trailing commas
            cleaned = re.sub(r",\s*([\}\]])", r"\1", snippet)
            try:
                return json.loads(cleaned)
            except Exception:
                pass

    return None


# ---------------- WORKOUT GENERATION ---------------- #

WORKOUT_SYSTEM_PROMPT = """You are an elite, certified strength and conditioning coach and exercise physiologist.
Your task is to design a personalized, comprehensive, day-wise weekly workout plan formatted STRICTLY as a JSON object.

Follow these strict rules:
1. Always output valid JSON inside a ```json ``` code block.
2. Provide a structured plan with specific exercises for each active workout day.
3. For each exercise provide: name, sets, reps, rest time, target muscle group, and clear form instructions.
4. Include warm-up, cool-down, and recovery guidelines.
5. Ensure the difficulty matches the user's experience and available equipment.

JSON Schema:
{
  "title": "Title of the Workout Plan",
  "summary": "1-2 sentence overview of the strategy and benefits",
  "days_per_week": 4,
  "experience_level": "Intermediate",
  "split_name": "Push / Pull / Legs",
  "schedule": [
    {
      "day_number": 1,
      "day_name": "Monday",
      "title": "Chest, Shoulders & Triceps",
      "focus": "Upper Body Push Strength & Hypertrophy",
      "warmup": "5-8 min dynamic stretches, arm circles, band pull-aparts",
      "exercises": [
        {
          "id": "d1_e1",
          "name": "Barbell Bench Press",
          "sets": "4",
          "reps": "8-10",
          "rest": "90 sec",
          "target_muscle": "Chest (Pectorals)",
          "instructions": "Arch upper back slightly, retract scapulae, lower bar to mid-sternum, drive up explosively."
        }
      ],
      "cooldown": "5 min light static chest and shoulder stretches"
    }
  ],
  "recovery_tips": [
    "Aim for 7-9 hours of restful sleep",
    "Stay hydrated with at least 3 liters of water on training days"
  ]
}
"""


def generate_workout_plan(user: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured workout plan using Groq LLM."""
    llm = get_llm(temperature=0.3)

    user_info = f"""
USER PROFILE:
- Age: {user.get('age', 28)}, Gender: {user.get('gender', 'Male')}
- Current Weight: {user.get('weight_kg', 75)} kg, Target Weight: {user.get('target_weight_kg', 70)} kg
- Height: {user.get('height_cm', 175)} cm
- Fitness Goal: {preferences.get('goal', user.get('fitness_goal', 'Weight Loss'))}

WORKOUT PREFERENCES:
- Experience Level: {preferences.get('experience_level', 'Intermediate')}
- Preferred Workout Split: {preferences.get('split_type', 'Push Pull Legs')}
- Available Equipment: {preferences.get('equipment', 'Full Commercial Gym')}
- Training Days per Week: {preferences.get('days_per_week', 4)}
- Session Duration: {preferences.get('session_duration', '45-60')} minutes
- Health Conditions / Injuries: {preferences.get('health_conditions', 'None')}
- Additional Focus or Comments: {preferences.get('comments', 'None')}
"""

    prompt = f"{WORKOUT_SYSTEM_PROMPT}\n\n{user_info}\nCreate the full weekly workout schedule in exact JSON format."

    response = llm.invoke(prompt)
    raw_content = response.content

    plan_json = extract_json_from_text(raw_content)

    # Fallback structure if LLM didn't return perfect JSON
    if not plan_json or not isinstance(plan_json, dict) or "schedule" not in plan_json:
        plan_json = create_fallback_workout_plan(user, preferences, raw_content)

    return {
        "title": plan_json.get("title", f"{preferences.get('split_type', 'Custom')} Workout Plan"),
        "goal": preferences.get("goal", user.get("fitness_goal", "Weight Loss")),
        "experience_level": preferences.get("experience_level", "Intermediate"),
        "split_type": preferences.get("split_type", "Full Body"),
        "equipment": preferences.get("equipment", "Gym"),
        "duration_weeks": preferences.get("duration_weeks", 4),
        "plan_data": plan_json,
        "raw_markdown": raw_content,
    }


def create_fallback_workout_plan(user: Dict[str, Any], preferences: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """Generate safe, rich default plan if JSON extraction was imperfect."""
    return {
        "title": f"Custom {preferences.get('goal', 'Fitness')} Protocol",
        "summary": "Tailored training split optimized for balanced muscle activation and cardiovascular conditioning.",
        "days_per_week": preferences.get("days_per_week", 4),
        "experience_level": preferences.get("experience_level", "Intermediate"),
        "split_name": preferences.get("split_type", "Balanced Split"),
        "schedule": [
            {
                "day_number": 1,
                "day_name": "Day 1",
                "title": "Upper Body Push & Core",
                "focus": "Chest, Shoulders, Triceps, Abs",
                "warmup": "5-10 min arm swings, pushup planks, band pull-aparts",
                "exercises": [
                    {"id": "d1_e1", "name": "Dumbbell Bench Press", "sets": "4", "reps": "8-12", "rest": "90s", "target_muscle": "Chest", "instructions": "Keep elbows at a 45-degree angle; squeeze chest at peak contraction."},
                    {"id": "d1_e2", "name": "Overhead Shoulder Press", "sets": "3", "reps": "10-12", "rest": "60s", "target_muscle": "Deltoids", "instructions": "Press weights vertically without excessively arching your lower back."},
                    {"id": "d1_e3", "name": "Triceps Cable Pushdowns", "sets": "3", "reps": "12-15", "rest": "60s", "target_muscle": "Triceps", "instructions": "Pin elbows to your sides and fully extend through the triceps."},
                    {"id": "d1_e4", "name": "Hanging Knee / Leg Raises", "sets": "3", "reps": "12-15", "rest": "45s", "target_muscle": "Core", "instructions": "Engage lower abdominals and control the eccentric descent."}
                ],
                "cooldown": "Chest doorway stretch and triceps overhead stretch"
            },
            {
                "day_number": 2,
                "day_name": "Day 2",
                "title": "Lower Body Power & Quads",
                "focus": "Quadriceps, Glutes, Calves",
                "warmup": "Leg swings, bodyweight squats, hip openers",
                "exercises": [
                    {"id": "d2_e1", "name": "Barbell or Goblet Squat", "sets": "4", "reps": "8-10", "rest": "90-120s", "target_muscle": "Quads & Glutes", "instructions": "Break at the hips and knees simultaneously, keeping chest upright."},
                    {"id": "d2_e2", "name": "Romanian Deadlift", "sets": "3", "reps": "10-12", "rest": "90s", "target_muscle": "Hamstrings & Glutes", "instructions": "Hinge hips backward with soft knees until feeling hamstring stretch."},
                    {"id": "d2_e3", "name": "Walking Dumbbell Lunges", "sets": "3", "reps": "10 per leg", "rest": "60s", "target_muscle": "Quads / Stabilizers", "instructions": "Step forward with posture upright, knee gently hovering above ground."},
                    {"id": "d2_e4", "name": "Standing Calf Raises", "sets": "4", "reps": "15-20", "rest": "45s", "target_muscle": "Calves", "instructions": "Hold 1 second pause at the top stretch."}
                ],
                "cooldown": "Hamstring and quad foam rolling"
            },
            {
                "day_number": 3,
                "day_name": "Day 3",
                "title": "Upper Body Pull & Posterior Chain",
                "focus": "Lats, Upper Back, Biceps, Rear Delts",
                "warmup": "Cat-cow stretches, thoracic rotations, light rows",
                "exercises": [
                    {"id": "d3_e1", "name": "Lat Pulldowns or Pull-ups", "sets": "4", "reps": "8-10", "rest": "90s", "target_muscle": "Latissimus Dorsi", "instructions": "Pull with your elbows driving toward your hips, squeeze back."},
                    {"id": "d3_e2", "name": "Seated Cable Row", "sets": "3", "reps": "10-12", "rest": "60s", "target_muscle": "Rhomboids & Mid-Back", "instructions": "Avoid swinging torso; pull handle into lower abdomen."},
                    {"id": "d3_e3", "name": "Dumbbell Bicep Curls", "sets": "3", "reps": "10-12", "rest": "60s", "target_muscle": "Biceps", "instructions": "Control both concentric and eccentric phases without momentum."},
                    {"id": "d3_e4", "name": "Face Pulls", "sets": "3", "reps": "15", "rest": "45s", "target_muscle": "Rear Deltoids", "instructions": "Pull rope toward bridge of nose with external shoulder rotation."}
                ],
                "cooldown": "Lat stretch and child's pose"
            },
            {
                "day_number": 4,
                "day_name": "Day 4",
                "title": "Full Body Conditioning & Core",
                "focus": "Aerobic Capacity, Core Stability, Mobility",
                "warmup": "Jumping jacks, high knees, dynamic lunge twists",
                "exercises": [
                    {"id": "d4_e1", "name": "Kettlebell / Dumbbell Swings", "sets": "4", "reps": "15", "rest": "60s", "target_muscle": "Glutes & Hamstrings", "instructions": "Hinge hips with power; snap glutes at the top."},
                    {"id": "d4_e2", "name": "Dumbbell Thrusters", "sets": "3", "reps": "10-12", "rest": "60s", "target_muscle": "Full Body", "instructions": "Squat down then press dumbbells overhead in one fluid motion."},
                    {"id": "d4_e3", "name": "Plank with Shoulder Taps", "sets": "3", "reps": "20 taps", "rest": "45s", "target_muscle": "Core & Shoulders", "instructions": "Resist hip rotation as you tap alternate shoulders."}
                ],
                "cooldown": "Full body yoga stretches & diaphragmatic breathing"
            }
        ],
        "recovery_tips": [
            "Ensure 7-8 hours of quality sleep for muscular recovery",
            "Drink at least 3 liters of water throughout active days",
            "Take 10,000 steps on rest days for active recovery"
        ],
        "notes": raw_text[:300] if raw_text else ""
    }


# ---------------- DIET GENERATION ---------------- #

DIET_SYSTEM_PROMPT = """You are an elite sports dietitian and clinical nutritionist.
Your task is to design a personalized, comprehensive, day-to-day nutrition and meal plan formatted STRICTLY as a JSON object.

Follow these strict rules:
1. Always output valid JSON inside a ```json ``` code block.
2. Separate meals into Breakfast, Lunch, Dinner, and Snacks.
3. For each meal, list food items, portion sizes, estimated calories, protein (g), carbohydrates (g), and fats (g).
4. Provide total daily target calories and total macronutrient breakdown.
5. Provide hydration and practical nutrition guidelines.

JSON Schema:
{
  "title": "High-Protein Lean Definition Diet",
  "diet_type": "Mediterranean High-Protein",
  "daily_targets": {
    "calories": 2100,
    "protein_g": 160,
    "carbs_g": 200,
    "fats_g": 65
  },
  "meals": [
    {
      "name": "Breakfast",
      "time": "08:00 AM",
      "total_calories": 520,
      "protein_g": 38,
      "carbs_g": 55,
      "fats_g": 14,
      "items": [
        {
          "food": "Rolled Oatmeal with Blueberries & Whey",
          "portion": "60g oats, 1 scoop whey, 50g berries",
          "calories": 370,
          "protein": 30,
          "carbs": 50,
          "fats": 5
        },
        {
          "food": "Boiled Whole Eggs",
          "portion": "2 medium eggs",
          "calories": 150,
          "protein": 12,
          "carbs": 1,
          "fats": 10
        }
      ],
      "instructions": "Pair with a tall glass of water or green tea."
    },
    {
      "name": "Lunch",
      "time": "01:00 PM",
      "total_calories": 640,
      "protein_g": 48,
      "carbs_g": 62,
      "fats_g": 18,
      "items": [
        {
          "food": "Grilled Chicken Breast (or Tofu for Veg)",
          "portion": "180g cooked",
          "calories": 280,
          "protein": 42,
          "carbs": 0,
          "fats": 6
        },
        {
          "food": "Brown Rice or Quinoa",
          "portion": "1 cup cooked (150g)",
          "calories": 210,
          "protein": 5,
          "carbs": 45,
          "fats": 2
        },
        {
          "food": "Steamed Broccoli & Mixed Greens with Olive Oil",
          "portion": "1 bowl with 1 tsp olive oil",
          "calories": 150,
          "protein": 4,
          "carbs": 12,
          "fats": 10
        }
      ],
      "instructions": "Chew slowly and avoid sugary drinks with lunch."
    },
    {
      "name": "Afternoon Snack",
      "time": "04:30 PM",
      "total_calories": 310,
      "protein_g": 24,
      "carbs_g": 28,
      "fats_g": 9,
      "items": [
        {
          "food": "Greek Yogurt with Almonds & Honey",
          "portion": "200g Greek yogurt, 10 almonds, 1 tsp honey",
          "calories": 310,
          "protein": 24,
          "carbs": 28,
          "fats": 9
        }
      ],
      "instructions": "Ideal pre-workout snack 60-90 minutes before training."
    },
    {
      "name": "Dinner",
      "time": "08:00 PM",
      "total_calories": 630,
      "protein_g": 50,
      "carbs_g": 55,
      "fats_g": 20,
      "items": [
        {
          "food": "Baked Salmon or Paneer/Tempeh",
          "portion": "170g cooked",
          "calories": 320,
          "protein": 36,
          "carbs": 0,
          "fats": 18
        },
        {
          "food": "Baked Sweet Potato",
          "portion": "1 medium (150g)",
          "calories": 160,
          "protein": 3,
          "carbs": 37,
          "fats": 0
        },
        {
          "food": "Sautéed Asparagus & Bell Peppers",
          "portion": "1 plate with garlic & light olive oil spray",
          "calories": 150,
          "protein": 4,
          "carbs": 14,
          "fats": 8
        }
      ],
      "instructions": "Eat at least 2 hours before bedtime to support digestion and sleep quality."
    }
  ],
  "hydration_liters": 3.0,
  "guidelines": [
    "Drink 500ml water immediately upon waking",
    "Keep salt and electrolytes replenished around heavy workouts",
    "Limit alcohol and sugary sauces"
  ]
}
"""


def generate_diet_plan(user: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured diet plan using Groq LLM."""
    llm = get_llm(temperature=0.3)

    # Compute baseline recommendations
    nutrition = calculate_nutrition_estimates(
        weight_kg=user.get("weight_kg", 75.0),
        height_cm=user.get("height_cm", 175.0),
        age=user.get("age", 28),
        gender=user.get("gender", "Male"),
        goal=preferences.get("goal", user.get("fitness_goal", "Weight Loss")),
        activity_level=user.get("activity_level", "Moderately Active")
    )

    user_info = f"""
USER PROFILE & BIOMETRICS:
- Age: {user.get('age', 28)}, Gender: {user.get('gender', 'Male')}
- Current Weight: {user.get('weight_kg', 75)} kg, Target Weight: {user.get('target_weight_kg', 70)} kg
- Height: {user.get('height_cm', 175)} cm
- Fitness Goal: {preferences.get('goal', user.get('fitness_goal', 'Weight Loss'))}
- Scientific Energy Targets: TDEE ~{nutrition['tdee']} kcal | Recommended Target ~{nutrition['target_calories']} kcal
- Recommended Macro Ratio: ~{nutrition['target_protein']}g Protein, ~{nutrition['target_carbs']}g Carbs, ~{nutrition['target_fats']}g Fats

DIET PREFERENCES & REQUIREMENTS:
- Diet Type: {preferences.get('diet_type', 'Balanced / High-Protein')}
- Dietary Restrictions & Allergies: {preferences.get('dietary_restrictions', 'None')}
- Meals Per Day: {preferences.get('meals_per_day', 4)}
- Health Conditions: {preferences.get('health_conditions', 'None')}
- User Specific Notes: {preferences.get('comments', 'None')}
"""

    prompt = f"{DIET_SYSTEM_PROMPT}\n\n{user_info}\nCreate the full day-to-day meal plan with exact macros and portions in JSON format."

    response = llm.invoke(prompt)
    raw_content = response.content

    plan_json = extract_json_from_text(raw_content)

    if not plan_json or not isinstance(plan_json, dict) or "meals" not in plan_json:
        plan_json = create_fallback_diet_plan(user, preferences, nutrition, raw_content)

    daily_targets = plan_json.get("daily_targets", {})

    return {
        "title": plan_json.get("title", f"{preferences.get('diet_type', 'Personalized')} Nutrition Plan"),
        "diet_type": preferences.get("diet_type", "High Protein"),
        "target_calories": daily_targets.get("calories", nutrition["target_calories"]),
        "target_protein": daily_targets.get("protein_g", nutrition["target_protein"]),
        "target_carbs": daily_targets.get("carbs_g", nutrition["target_carbs"]),
        "target_fats": daily_targets.get("fats_g", nutrition["target_fats"]),
        "plan_data": plan_json,
        "raw_markdown": raw_content,
    }


def create_fallback_diet_plan(user: Dict[str, Any], preferences: Dict[str, Any], nutrition: Dict[str, int], raw_text: str) -> Dict[str, Any]:
    """Generate safe, rich default diet plan if JSON extraction was imperfect."""
    return {
        "title": f"Custom {preferences.get('diet_type', 'Balanced')} Nutrition Plan",
        "diet_type": preferences.get("diet_type", "High Protein"),
        "daily_targets": {
            "calories": nutrition.get("target_calories", 2000),
            "protein_g": nutrition.get("target_protein", 150),
            "carbs_g": nutrition.get("target_carbs", 190),
            "fats_g": nutrition.get("target_fats", 65)
        },
        "meals": [
            {
                "name": "Breakfast",
                "time": "08:00 AM",
                "total_calories": 480,
                "protein_g": 36,
                "carbs_g": 52,
                "fats_g": 12,
                "items": [
                    {"food": "Steel-cut Oats with Whey Protein", "portion": "60g oats + 1 scoop protein powder", "calories": 340, "protein": 28, "carbs": 48, "fats": 4},
                    {"food": "Boiled Eggs or Tofu Scramble", "portion": "2 eggs or 100g scrambled tofu", "calories": 140, "protein": 12, "carbs": 2, "fats": 8}
                ],
                "instructions": "Pair with 500ml water and black coffee or green tea."
            },
            {
                "name": "Lunch",
                "time": "01:00 PM",
                "total_calories": 620,
                "protein_g": 48,
                "carbs_g": 65,
                "fats_g": 16,
                "items": [
                    {"food": "Grilled Chicken Breast / Paneer", "portion": "170g chicken or 130g paneer", "calories": 280, "protein": 40, "carbs": 2, "fats": 8},
                    {"food": "Steamed Brown Basmati Rice or Quinoa", "portion": "150g cooked", "calories": 200, "protein": 4, "carbs": 44, "fats": 2},
                    {"food": "Fresh Garden Salad with Olive Oil Dressing", "portion": "1 large bowl", "calories": 140, "protein": 3, "carbs": 12, "fats": 8}
                ],
                "instructions": "Focus on high-fiber greens for satiety and gut health."
            },
            {
                "name": "Afternoon Power Snack",
                "time": "04:30 PM",
                "total_calories": 280,
                "protein_g": 22,
                "carbs_g": 26,
                "fats_g": 8,
                "items": [
                    {"food": "Non-Fat Greek Yogurt & Berries", "portion": "180g yogurt + 40g raspberries", "calories": 180, "protein": 18, "carbs": 18, "fats": 1},
                    {"food": "Raw Almonds or Walnuts", "portion": "12 nuts (15g)", "calories": 100, "protein": 4, "carbs": 3, "fats": 9}
                ],
                "instructions": "Fuel boost before evening workout or end-of-workday focus."
            },
            {
                "name": "Dinner",
                "time": "08:00 PM",
                "total_calories": 580,
                "protein_g": 46,
                "carbs_g": 45,
                "fats_g": 18,
                "items": [
                    {"food": "Grilled Salmon / Baked Tofu / Lentil Dal", "portion": "160g fish or 1.5 cups dal", "calories": 300, "protein": 34, "carbs": 10, "fats": 14},
                    {"food": "Roasted Sweet Potato or Whole Wheat Roti", "portion": "1 medium sweet potato or 2 rotis", "calories": 160, "protein": 4, "carbs": 35, "fats": 2},
                    {"food": "Steamed Broccoli & Zucchini", "portion": "1.5 cups steamed", "calories": 120, "protein": 4, "carbs": 12, "fats": 4}
                ],
                "instructions": "Enjoy your final meal at least 2 hours before sleeping for restorative recovery."
            }
        ],
        "hydration_liters": 3.0,
        "guidelines": [
            "Hydrate consistently throughout the day",
            "Focus on lean protein sources at every meal",
            "Prioritize whole grains and fibrous vegetables over simple sugars"
        ],
        "notes": raw_text[:300] if raw_text else ""
    }


# ---------------- AI COACH CHAT ---------------- #

def ask_fitness_coach(messages: List[Dict[str, str]], user: Dict[str, Any], active_workout: Optional[Dict[str, Any]], active_diet: Optional[Dict[str, Any]]) -> str:
    """Conversational AI coach aware of user biometrics and active plans."""
    llm = get_llm(temperature=0.5)

    context_summary = f"""
USER PROFILE:
- Name: {user.get('name', 'Athlete')}, Age: {user.get('age', 28)}, Gender: {user.get('gender', 'Male')}
- Current Weight: {user.get('weight_kg', 75)}kg, Target: {user.get('target_weight_kg', 70)}kg
- Primary Goal: {user.get('fitness_goal', 'Fitness & Health')}
"""

    if active_workout and "plan_data" in active_workout:
        wp = active_workout["plan_data"]
        context_summary += f"\nACTIVE WORKOUT PLAN: {wp.get('title', 'Active Workout')}, Split: {wp.get('split_name', 'Custom')}, Days/Wk: {wp.get('days_per_week', 4)}"

    if active_diet and "plan_data" in active_diet:
        dp = active_diet["plan_data"]
        targets = dp.get("daily_targets", {})
        context_summary += f"\nACTIVE DIET PLAN: {dp.get('title', 'Active Diet')}, Target Calories: {targets.get('calories', 'N/A')} kcal (P: {targets.get('protein_g', 'N/A')}g, C: {targets.get('carbs_g', 'N/A')}g, F: {targets.get('fats_g', 'N/A')}g)"

    coach_system_prompt = f"""You are 'Aero Coach', an empathetic, motivating, and science-grounded elite fitness and nutrition coach.
You are helping {user.get('name', 'Athlete')} achieve their fitness ambitions.
Use the following context to provide direct, actionable, encouraging advice:
{context_summary}

Keep your responses structured, clear, motivating, and easy to read with bullet points when explaining exercises or nutrition.
"""

    formatted_messages = [{"role": "system", "content": coach_system_prompt}]
    for m in messages[-8:]: # keep recent context window
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    lc_messages = []
    for m in formatted_messages:
        if m["role"] == "system":
            lc_messages.append(SystemMessage(content=m["content"]))
        elif m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    try:
        res = llm.invoke(lc_messages)
        return res.content
    except Exception as e:
        return f"I'm here to help you stay on track! However, I encountered a temporary network glitch: {e}. Please try asking again in a moment."


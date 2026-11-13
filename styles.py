"""
Custom CSS Styles for Modern AI Fitness Planner
Provides a premium fitness-themed aesthetic with sleek cards, vibrant accents,
glassmorphism, clean typography, responsive layout, and interactive states.
"""

CUSTOM_CSS = """
<style>
/* ---------------- GLOBAL & ROOT ---------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

:root {
    --bg-primary: #0A0E1A;
    --bg-secondary: #121829;
    --bg-card: rgba(20, 27, 45, 0.75);
    --bg-card-hover: rgba(28, 38, 64, 0.85);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-highlight: rgba(16, 185, 129, 0.4);
    
    --primary-green: #10B981;
    --primary-cyan: #06B6D4;
    --accent-coral: #F43F5E;
    --accent-amber: #F59E0B;
    --accent-purple: #8B5CF6;
    
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-full: 9999px;
    
    --shadow-soft: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 0 25px rgba(16, 185, 129, 0.2);
}

/* Base App Styling */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

.stApp {
    background: radial-gradient(circle at 10% 10%, #111A30 0%, #080B14 85%);
    background-attachment: fixed;
}

/* ---------------- SIDEBAR STYLING ---------------- */
section[data-testid="stSidebar"] {
    background-color: #0c1222 !important;
    border-right: 1px solid var(--border-color);
}

section[data-testid="stSidebar"] .stButton button {
    border-radius: var(--radius-md);
    font-weight: 600;
    transition: all 0.2s ease-in-out;
}

/* ---------------- PREMIUM CARDS ---------------- */
.fitness-card {
    background: var(--bg-card);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-soft);
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.2s ease;
}

.fitness-card:hover {
    border-color: rgba(255, 255, 255, 0.16);
    box-shadow: 0 14px 40px -12px rgba(0, 0, 0, 0.6);
}

.fitness-card-gradient {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%), var(--bg-card);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-glow);
}

/* ---------------- HERO & HEADERS ---------------- */
.hero-container {
    padding: 1.25rem 0 2rem 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.75rem;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.35rem;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.85rem;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: var(--radius-full);
    color: #34D399;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
}

/* ---------------- STAT / METRIC WIDGETS ---------------- */
.stat-box {
    background: rgba(18, 24, 42, 0.8);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.15rem 1.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    transition: all 0.2s ease;
}

.stat-box:hover {
    border-color: rgba(16, 185, 129, 0.35);
    transform: translateY(-2px);
}

.stat-label {
    font-size: 0.825rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}

.stat-subtext {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
}

/* ---------------- BADGES & CHIPS ---------------- */
.pill-badge {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.pill-green {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.pill-blue {
    background: rgba(6, 182, 212, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(6, 182, 212, 0.3);
}

.pill-coral {
    background: rgba(244, 63, 94, 0.15);
    color: #FB7185;
    border: 1px solid rgba(244, 63, 94, 0.3);
}

.pill-purple {
    background: rgba(139, 92, 246, 0.15);
    color: #A78BFA;
    border: 1px solid rgba(139, 92, 246, 0.3);
}

.pill-amber {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

/* ---------------- EXERCISE CARD ---------------- */
.exercise-card {
    background: rgba(15, 21, 37, 0.9);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--primary-green);
    border-radius: var(--radius-md);
    padding: 1.15rem 1.35rem;
    margin-bottom: 0.9rem;
    transition: all 0.2s ease;
}

.exercise-card:hover {
    border-color: rgba(255, 255, 255, 0.18);
    border-left-color: var(--primary-cyan);
    transform: translateX(4px);
}

.exercise-card.completed {
    border-left-color: #34D399;
    opacity: 0.75;
    background: rgba(16, 185, 129, 0.05);
}

.exercise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.exercise-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
}

.exercise-meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 0.5rem;
    margin: 0.75rem 0;
    padding: 0.65rem 0.85rem;
    background: rgba(0, 0, 0, 0.25);
    border-radius: var(--radius-sm);
}

.meta-item {
    display: flex;
    flex-direction: column;
}

.meta-item-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    font-weight: 700;
}

.meta-item-val {
    font-size: 0.95rem;
    font-weight: 700;
    color: #E2E8F0;
}

.exercise-instructions {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.45;
    margin-top: 0.4rem;
}

/* ---------------- MEAL CARD ---------------- */
.meal-card {
    background: rgba(15, 21, 37, 0.9);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--primary-cyan);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.meal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.75rem;
    margin-bottom: 0.85rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.meal-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
}

.meal-food-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
}

.meal-food-item:last-child {
    border-bottom: none;
}

.food-desc {
    font-weight: 600;
    color: #F1F5F9;
    font-size: 0.925rem;
}

.food-portion {
    font-size: 0.8rem;
    color: var(--text-muted);
}

.food-macros {
    display: flex;
    gap: 0.6rem;
    font-size: 0.8rem;
    font-weight: 600;
}

/* ---------------- MACRO PROGRESS BAR ---------------- */
.macro-progress-container {
    margin: 0.75rem 0;
}

.macro-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
}

.macro-bar-track {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.macro-bar-fill-green {
    height: 100%;
    background: linear-gradient(90deg, #10B981, #34D399);
    border-radius: var(--radius-full);
}

.macro-bar-fill-blue {
    height: 100%;
    background: linear-gradient(90deg, #06B6D4, #38BDF8);
    border-radius: var(--radius-full);
}

.macro-bar-fill-coral {
    height: 100%;
    background: linear-gradient(90deg, #F43F5E, #FB7185);
    border-radius: var(--radius-full);
}

/* ---------------- BUTTONS & INPUT OVERRIDES ---------------- */
.stButton button {
    border-radius: var(--radius-md) !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #10B981 0%, #06B6D4 100%) !important;
    color: #04101A !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35) !important;
}

.stButton button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
}

.stButton button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
}

.stButton button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Form inputs styling */
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
    border-radius: var(--radius-md) !important;
    background-color: rgba(13, 18, 32, 0.8) !important;
    border-color: var(--border-color) !important;
    color: #FFFFFF !important;
}

div[data-baseweb="select"] {
    border-radius: var(--radius-md) !important;
}

/* Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(13, 18, 32, 0.6);
    padding: 6px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm);
    padding: 8px 16px;
    font-weight: 600;
    color: var(--text-secondary);
}

.stTabs [aria-selected="true"] {
    background: rgba(16, 185, 129, 0.18) !important;
    color: #34D399 !important;
    border-bottom: none !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(10, 14, 26, 0.5);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: var(--radius-full);
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(16, 185, 129, 0.4);
}
</style>
"""


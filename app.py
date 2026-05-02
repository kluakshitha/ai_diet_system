import streamlit as st
import sqlite3
import hashlib

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Diet Planner",
    page_icon="🥗",
    layout="centered"
)

# ================= LOAD MODEL =================
@st.cache_resource
def load_predict():
    from predict import predict_diet
    return predict_diet

predict_diet = load_predict()

# ================= UI =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: url("https://img.pikbest.com/wp/202343/healthy-nutrition-close-up-of-concept-on-white-textured-background_9988050.jpg!bw700") no-repeat center center fixed;
    background-size: cover;
}
.block-container {
    max-width: 700px;
    margin-left: 40px;
}
.card {
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= HEADER =================
st.title("🧠 AI Diet Recommendation System")
st.write("Personalized diet plans powered by AI")

# ================= MENU =================
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ================= REGISTER =================
if choice == "Register":
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        try:
            c.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, hashed_pw)
            )
            conn.commit()
            st.success("Registered successfully ✅")
        except:
            st.error("Email already exists ❌")

# ================= LOGIN =================
elif choice == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = c.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if user and hashed_pw == user[3]:
            st.session_state.user = user[1]
            st.success("Login successful 🎉")
        else:
            st.error("Invalid credentials ❌")

# ================= MAIN =================
if st.session_state.user:

    st.subheader(f"Welcome {st.session_state.user}")

    age = st.number_input("Age", 1, 120)
    bmi = st.number_input("BMI", 10.0, 50.0)
    gender = st.selectbox("Gender", ["Male", "Female"])

    diseases = st.multiselect(
        "Diseases",
        [
            "None", "Diabetes", "Hypertension", "Heart Disease",
            "Obesity", "Thyroid", "PCOS", "Anemia",
            "Cholesterol", "Asthma", "Arthritis"
        ]
    )

    if "None" in diseases:
        diseases = []

    activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])

    plan_type = st.radio("Plan Type", ["Normal", "Personalized", "Premium"])

    if st.button("Get Diet Plan"):

        # mode selection
        if plan_type == "Personalized":
            mode = "yes"
        elif plan_type == "Premium":
            mode = "premium"
        else:
            mode = None

        diet, guide = predict_diet(
            age, bmi, diseases, activity, gender,
            mode, "", ""
        )

        # ===== DIET =====
        st.markdown(f"""
        <div class="card">
        <h3>🍽️ Diet Plan</h3>
        <b>{diet}</b>
        </div>
        """, unsafe_allow_html=True)

        # ===== NUTRITION =====
        st.markdown(f"""
        <div class="card">
        <h3>📊 Nutrition</h3>
        Calories: {guide['calories']}<br>
        Protein: {guide['protein']}<br>
        Carbs: {guide['carbohydrates']}<br>
        Fat: {guide['fat']}
        </div>
        """, unsafe_allow_html=True)

        # ===== FOODS =====
        st.markdown(f"""
        <div class="card">
        <h3>🥗 Recommended Foods</h3>
        {", ".join(guide["recommended_foods"])}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
        <h3>🚫 Foods to Avoid</h3>
        {", ".join(guide["foods_to_avoid"])}
        </div>
        """, unsafe_allow_html=True)

        # ===== EXERCISE =====
        if "exercise_plan" in guide:
            st.markdown(f"""
            <div class="card">
            <h3>🏋️ Exercise Plan</h3>
            {", ".join(guide["exercise_plan"])}
            </div>
            """, unsafe_allow_html=True)

        # ===== WEEKLY PLAN =====
        if "weekly_plan" in guide:
            text = ""
            for d, meal in guide["weekly_plan"].items():
                text += f"<b>{d}:</b> {meal}<br>"

            st.markdown(f"""
            <div class="card">
            <h3>📅 Weekly Plan</h3>
            {text}
            </div>
            """, unsafe_allow_html=True)

        # ===== PREMIUM =====
        if "meal_plan" in guide:
            text = ""
            for d, meals in guide["meal_plan"].items():
                text += f"<b>{d}</b><br>"
                text += f"Breakfast: {meals['Breakfast']}<br>"
                text += f"Lunch: {meals['Lunch']}<br>"
                text += f"Dinner: {meals['Dinner']}<br><br>"

            st.markdown(f"""
            <div class="card">
            <h3>🍽️ Full Meal Plan</h3>
            {text}
            </div>
            """, unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

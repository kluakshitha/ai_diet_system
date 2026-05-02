import streamlit as st
import sqlite3
import hashlib   # ✅ replaced bcrypt

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

# ================= SMART HEALTH LOGIC =================
def generate_health_plan(diet, diseases, bmi, activity):

    explanation = ""
    tips = []
    warning = ""
    exercise = []

    if "Balanced" in diet:
        explanation = "Balanced diet includes carbohydrates, proteins, and healthy fats for overall health."
    elif "Low Carb" in diet:
        explanation = "Low-carb diet helps control blood sugar and supports weight loss."
    elif "High Protein" in diet:
        explanation = "High-protein diet helps in muscle building."
    else:
        explanation = f"{diet} supports overall health."

    if "Diabetes" in diseases:
        diet = "Low Carb Diet"
        tips = [
            "Avoid sugary foods and soft drinks",
            "Eat whole grains and fiber-rich food",
            "Monitor blood sugar regularly"
        ]
        warning = "High sugar intake can be dangerous."
        exercise = ["Walking 30 mins", "Cycling", "Yoga"]

    elif "Hypertension" in diseases:
        diet = "Low Sodium Diet"
        tips = [
            "Reduce salt intake",
            "Eat potassium-rich foods like banana",
            "Avoid fried food"
        ]
        warning = "High BP can lead to heart problems."
        exercise = ["Walking", "Meditation", "Breathing exercises"]

    elif "Obesity" in diseases:
        diet = "Weight Loss Diet"
        tips = [
            "Control portion size",
            "Eat low-calorie foods",
            "Avoid fast food"
        ]
        warning = "Obesity increases risk of multiple diseases."
        exercise = ["Running", "HIIT", "Cycling"]

    elif "Heart Disease" in diseases:
        diet = "Heart Healthy Diet"
        tips = [
            "Avoid oily and fatty food",
            "Eat more fruits and vegetables",
            "Use less salt"
        ]
        warning = "Unhealthy diet can worsen heart condition."
        exercise = ["Light walking", "Yoga"]

    elif "PCOS" in diseases:
        diet = "Hormonal Balance Diet"
        tips = [
            "Avoid sugar and processed food",
            "Eat high protein meals",
            "Maintain regular sleep"
        ]
        warning = "Hormonal imbalance needs consistent care."
        exercise = ["Yoga", "Strength training"]

    elif "Anemia" in diseases:
        diet = "Iron Rich Diet"
        tips = [
            "Eat spinach and leafy vegetables",
            "Include dates and jaggery",
            "Take vitamin C with iron food"
        ]
        warning = "Low iron levels cause weakness."
        exercise = ["Light walking"]

    elif "Thyroid" in diseases:
        diet = "Thyroid Support Diet"
        tips = [
            "Eat iodine-rich foods",
            "Avoid junk food",
            "Maintain balanced diet"
        ]
        warning = "Improper diet affects thyroid levels."
        exercise = ["Yoga", "Walking"]

    else:
        tips = [
            "Maintain balanced diet",
            "Drink enough water",
            "Stay active daily"
        ]
        warning = "Follow healthy lifestyle regularly."
        exercise = ["Walking", "Stretching"]

    return diet, explanation, tips, warning, exercise


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
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()  # ✅ changed
        try:
            c.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                      (name, email, hashed_pw))
            conn.commit()
            st.success("Registered successfully")
        except:
            st.error("Email already exists")

# ================= LOGIN =================
elif choice == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()  # ✅ changed

        if user and hashed_pw == user[3]:
            st.session_state.user = user[1]
        else:
            st.error("Invalid credentials")

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

    if st.button("Get Diet Plan"):

        diet, guide = predict_diet(age, bmi, diseases, activity, gender, None, "", "")

        st.markdown(f"""
        <div class="card">
        <h3>🍽️ Recommended Diet</h3>
        <p><b>{diet}</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
        <h3>📊 Nutrition</h3>
        Calories: {guide['calories']}<br>
        Protein: {guide['protein']}<br>
        Carbs: {guide['carbohydrates']}<br>
        Fat: {guide['fat']}
        </div>
        """, unsafe_allow_html=True)

        final_diet, explanation, tips, warning, exercise = generate_health_plan(
            diet, diseases, bmi, activity
        )

        st.markdown(f"""
        <div class="card">
        <h3>🤖 AI Insights</h3>

        <b>Diet Plan:</b> {final_diet}<br><br>

        <b>Explanation:</b><br>
        {explanation}<br><br>

        <b>Tips:</b><br>
        1. {tips[0]}<br>
        2. {tips[1]}<br>
        3. {tips[2]}<br><br>

        <b>Exercise Plan:</b><br>
        - {", ".join(exercise)}<br><br>

        <b>Warning:</b><br>
        {warning}

        </div>
        """, unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

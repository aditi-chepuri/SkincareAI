import os
import base64
import uuid
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, session

from werkzeug.security import generate_password_hash, check_password_hash

import mysql.connector

from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.utils import load_img, img_to_array  # type: ignore
from tensorflow.keras.applications.efficientnet import preprocess_input  # type: ignore


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "skincare_ai_secret")


# =========================================================
# AI MODEL
# =========================================================

MODEL_PATH = "skin_model_efficientnet.h5"
CLASS_NAMES_PATH = "class_names_efficientnet.txt"

model = load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = [line.strip() for line in f if line.strip()]

print("========================================")
print("AI MODEL LOADED")
print("========================================")
print("Model :", MODEL_PATH)
print("Classes:", class_names)
print("========================================")


# Make sure exactly 4 classes are present
expected_classes = ["combination", "dry", "normal", "oily"]

if len(class_names) != 4:
    raise ValueError(
        f"Expected 4 classes, but found: {class_names}"
    )


# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# DATABASE
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="skincare_ai"
)

cursor = db.cursor(dictionary=True)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("home.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user is None:
            return render_template(
                "login.html",
                error="Email not registered."
            )

        try:

            password_match = check_password_hash(
                user["password"],
                password
            )

        except Exception:

            return render_template(
                "login.html",
                error="Invalid account password."
            )

        if password_match:

            session["user"] = user["email"]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid Email or Password."
        )

    return render_template("login.html")


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        if password != confirm_password:

            return render_template(
                "signup.html",
                error="Passwords do not match."
            )

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return render_template(
                "signup.html",
                error="Email already registered."
            )

        hashed_password = generate_password_hash(password)

        sql = """
        INSERT INTO users
        (name, email, password)
        VALUES (%s, %s, %s)
        """

        values = (
            name,
            email,
            hashed_password
        )

        cursor.execute(sql, values)

        db.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


# =========================================================
# ANALYZE PAGE
# =========================================================

@app.route("/analyze")
def analyze():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("analyze.html")


# =========================================================
# PRODUCTS
# =========================================================

@app.route("/products")
def products():

    return render_template("products.html")


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not subject or not message:

            return render_template(
                "contact.html",
                error="Please fill in all fields."
            )

        try:

            sql = """
                INSERT INTO contact_messages
                (name, email, subject, message)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                name,
                email,
                subject,
                message
            )

            cursor.execute(sql, values)

            db.commit()

            return render_template(
                "contact.html",
                success="Your message has been sent successfully!"
            )

        except Exception as e:

            print("Contact form error:", e)

            db.rollback()

            return render_template(
                "contact.html",
                error="Unable to send your message. Please try again."
            )

    return render_template("contact.html")


# =========================================================
# RESULT / AI ANALYSIS
# =========================================================

@app.route("/result", methods=["POST"])
def result():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user" not in session:
        return redirect(url_for("login"))


    # -----------------------------------------------------
    # GET CAPTURED IMAGE
    # -----------------------------------------------------

    captured_image = request.form.get("capturedImage")

    if not captured_image:

        return render_template(
            "result.html",
            error="Please capture or upload an image first."
        )


    # -----------------------------------------------------
    # SAVE IMAGE
    # -----------------------------------------------------

    try:

        if "," not in captured_image:
            raise ValueError("Invalid image data.")

        image_data = captured_image.split(",", 1)[1]

        image_bytes = base64.b64decode(
            image_data,
            validate=True
        )

        filename = uuid.uuid4().hex + ".jpg"

        img_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        with open(img_path, "wb") as image_file:

            image_file.write(image_bytes)

        print("Image saved:", img_path)

    except Exception as e:

        print("Image processing error:", e)

        return render_template(
            "analyze.html",
            error="Unable to process the selected image. Please try another image."
        )


    # -----------------------------------------------------
    # PREPARE IMAGE FOR EFFICIENTNET
    # -----------------------------------------------------

    try:

        img = load_img(
            img_path,
            target_size=(224, 224)
        )

        img_array = img_to_array(img)

        # Same preprocessing used during EfficientNet training
        img_array = preprocess_input(img_array)

        img_array = np.expand_dims(
            img_array,
            axis=0
        )

        print("Image prepared for model.")

    except Exception as e:

        print("Image loading error:", e)

        return render_template(
            "analyze.html",
            error="The uploaded file could not be read as an image."
        )


    # -----------------------------------------------------
    # AI PREDICTION
    # -----------------------------------------------------

    try:

        print("Running AI prediction...")

        prediction = model.predict(
            img_array,
            verbose=0
        )

        print("Prediction:", prediction)

        predicted_index = int(
            np.argmax(prediction)
        )

        if predicted_index >= len(class_names):

            raise ValueError(
                "Invalid prediction class."
            )

        skin_type = class_names[predicted_index]

        confidence = round(
            float(np.max(prediction)) * 100,
            2
        )

        print("Skin Type:", skin_type)
        print("Confidence:", confidence)

    except Exception as e:

        print("Model prediction error:", e)

        return render_template(
            "analyze.html",
            error="The AI model could not analyze this image. Please try again."
        )


    # =====================================================
    # RECOMMENDATIONS BY SKIN TYPE
    # =====================================================

    recommendations = {

        "dry": {

            "products": [
                "La Roche-Posay Toleriane Hydrating Cleanser",
                "The Ordinary Hyaluronic Acid 2% + B5",
                "Neutrogena Hydro Boost Gel Cream",
                "Dot & Key Watermelon Sleeping Mask"
            ],

            "benefits": [
                "Restores the skin barrier",
                "Locks in long-lasting moisture",
                "Reduces flaking and tightness",
                "Soothes rough or dull patches"
            ]
        },


        "oily": {

            "products": [
                "CeraVe Foaming Cleanser",
                "Minimalist Salicylic Acid 2% Serum",
                "Neutrogena Oil-Free Moisturizer",
                "La Roche-Posay SPF 50"
            ],

            "benefits": [
                "Controls excess oil",
                "Helps prevent acne",
                "Minimizes clogged pores",
                "Keeps skin matte through the day"
            ]
        },


        "combination": {

            "products": [
                "Simple Kind to Skin Refreshing Gel Wash",
                "Plum Green Tea Clear Face Moisturizer",
                "Minimalist Niacinamide Serum",
                "Neutrogena Ultra Sheer SPF"
            ],

            "benefits": [
                "Balances oily and dry zones",
                "Controls shine on the T-zone",
                "Keeps cheeks comfortably hydrated",
                "Evens out overall skin texture"
            ]
        },


        "normal": {

            "products": [
                "CeraVe Hydrating Cleanser",
                "Minimalist Vitamin C Serum",
                "Clinique Moisture Surge Gel Cream",
                "Neutrogena Ultra Sheer SPF 50"
            ],

            "benefits": [
                "Maintains skin's natural balance",
                "Boosts radiance and glow",
                "Protects against premature aging",
                "Preserves a healthy skin barrier"
            ]
        }

    }


    # -----------------------------------------------------
    # GET RECOMMENDATIONS
    # -----------------------------------------------------

    profile = recommendations.get(
        skin_type,
        recommendations["normal"]
    )

    products = profile["products"]

    benefits = profile["benefits"]


    # -----------------------------------------------------
    # MORNING ROUTINE
    # -----------------------------------------------------

    morning = [
        "Cleanser",
        "Moisturizer",
        "Sunscreen"
    ]


    # -----------------------------------------------------
    # NIGHT ROUTINE
    # -----------------------------------------------------

    night = [
        "Cleanser",
        "Serum",
        "Moisturizer"
    ]


    # -----------------------------------------------------
    # TIPS
    # -----------------------------------------------------

    tips = [
        "Drink 2-3 litres of water",
        "Sleep 7-8 hours",
        "Eat healthy food",
        "Wash face twice daily"
    ]


    # -----------------------------------------------------
    # AVOID
    # -----------------------------------------------------

    avoid_list = [
        "Harsh soaps",
        "Picking pimples",
        "Skipping sunscreen",
        "Overwashing your face"
    ]


    # -----------------------------------------------------
    # RESULT PAGE
    # -----------------------------------------------------

    return render_template(

        "result.html",

        skin_type=skin_type,

        confidence=confidence,

        products=products,

        benefits=benefits,

        morning=morning,

        night=night,

        tips=tips,

        avoid_list=avoid_list

    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
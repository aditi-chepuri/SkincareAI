# 🌸 SkincareAI – AI-Based Skin Type Analysis & Recommendation System

SkincareAI is an AI-powered skincare application that analyzes a user's facial image and predicts their skin type using a trained deep learning model. Based on the predicted skin type, the application provides personalized skincare product recommendations, benefits, and basic skincare routines.

## 🚀 Live Demo

**Try SkincareAI:**
https://skincareai-sftm.onrender.com

## 📌 Features

* 👤 User Signup and Login
* 📷 Image Upload and Camera Capture
* 🤖 AI-based Skin Type Prediction
* 📊 Prediction Confidence Score
* 🧴 Personalized Product Recommendations
* 🌅 Morning Skincare Routine
* 🌙 Night Skincare Routine
* 💡 Skincare Tips
* ⚠️ Products and habits to avoid
* 📩 Contact Form
* 🗄️ MySQL Database Integration
* ☁️ Cloud Deployment using Render

## 🧠 AI Model

The application uses a **Deep Learning model based on EfficientNet** for skin-type classification.

The model classifies images into four categories:

* Dry
* Oily
* Combination
* Normal

The uploaded image is resized and preprocessed before being passed to the trained model for prediction.

## 🛠️ Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### Machine Learning

* TensorFlow
* Keras
* NumPy
* EfficientNet

### Database

* MySQL
* Aiven MySQL

### Deployment

* GitHub
* Render

## 🔄 Application Workflow

```text
User
  ↓
Signup / Login
  ↓
Upload or Capture Facial Image
  ↓
Image Preprocessing
  ↓
EfficientNet Deep Learning Model
  ↓
Skin Type Prediction
  ↓
Confidence Score
  ↓
Personalized Recommendations
  ↓
Skincare Routine & Tips
```

## 📂 Project Structure

```text
SkincareAI/
│
├── static/
│   └── uploads/
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── analyze.html
│   ├── result.html
│   ├── products.html
│   └── contact.html
│
├── app.py
├── model.py
├── train.py
├── requirements.txt
├── skin_model_efficientnet.h5
└── class_names_efficientnet.txt
```

## 🗄️ Database

SkincareAI uses MySQL for storing application data.

### Tables

**users**

* User ID
* Name
* Email
* Password

**contact_messages**

* Message ID
* Name
* Email
* Subject
* Message

Database connectivity is configured using environment variables for secure deployment.

## ⚙️ How to Run Locally

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd SkincareAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure database environment variables

Set the required MySQL environment variables:

```text
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
SECRET_KEY
```

### 6. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## ☁️ Deployment

The application is deployed using **Render** with a cloud-hosted MySQL database.

The production application is available here:

https://skincareai-sftm.onrender.com

## 🔮 Future Enhancements

* More detailed skin-condition analysis
* Improved model accuracy with a larger dataset
* Personalized skincare routines based on additional user inputs
* Product filtering based on skin concerns
* Mobile application integration
* Improved image quality and preprocessing
* Explainable AI for prediction results

## 👩‍💻 Author

**Aditi Chepuri**

Data Science Student | Python | Machine Learning | SQL | Web Development

---

⭐ If you find this project useful, consider giving the repository a star!

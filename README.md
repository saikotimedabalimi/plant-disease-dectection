# 🌱 Plant Disease Detection Using Deep Learning

## 📌 Project Overview

Plant Disease Detection Using Deep Learning is an intelligent web/desktop-based application designed to identify plant diseases from leaf images. The system uses Deep Learning and Computer Vision techniques to analyze plant leaf images and classify them into healthy or diseased categories. The primary goal of this project is to assist farmers, agricultural experts, and researchers in detecting plant diseases at an early stage, thereby reducing crop losses and improving agricultural productivity.

Traditional disease detection methods rely on manual inspection, which is time-consuming, requires expertise, and may lead to inaccurate diagnoses. This project automates the disease detection process using a Convolutional Neural Network (CNN) model trained on plant leaf images.

In addition to disease prediction, the system provides detailed information about the detected disease, including its cause and recommended treatment, using a JSON-based disease database.

---

# 🎯 Problem Statement

Plant diseases significantly impact crop production and food security worldwide. Farmers often face challenges in identifying diseases accurately due to:

- Lack of agricultural expertise
- Similar symptoms among different diseases
- Delayed disease detection
- Limited access to experts
- High cost of manual monitoring

To address these challenges, this project provides an AI-powered solution that can automatically detect plant diseases from leaf images and recommend suitable remedies.

---

# 🎯 Objectives

The main objectives of this project are:

- Detect plant diseases automatically using deep learning.
- Improve disease detection accuracy.
- Provide disease cause and cure information.
- Reduce manual effort and dependency on experts.
- Help farmers take preventive actions early.
- Improve agricultural productivity and crop yield.

---

# 🚀 Features

### Disease Detection
- Detect diseases from uploaded plant leaf images.
- Identify healthy and diseased plants.

### Deep Learning Model
- CNN-based classification model.
- High prediction accuracy.

### Image Processing
- Image resizing.
- Normalization.
- Noise reduction.

### Disease Information
- Disease Name
- Cause
- Cure / Treatment Recommendation

### User-Friendly Interface
- Easy image upload.
- Fast result generation.
- Simple GUI design.

---

# 🏗️ System Architecture

```text
User
  |
  v
Upload Leaf Image
  |
  v
Image Preprocessing
  |
  v
CNN Model Prediction
  |
  v
Disease Classification
  |
  v
JSON Database
  |
  v
Display Result
```

---

# 🔄 Workflow

### Step 1: Upload Image
The user uploads a plant leaf image through the graphical user interface.

### Step 2: Image Preprocessing
The image is prepared for analysis through:
- Resizing
- Normalization
- Noise removal

### Step 3: Disease Prediction
The CNN model analyzes the image and predicts the disease.

### Step 4: Information Retrieval
Disease information is retrieved from the JSON database.

### Step 5: Result Display
The system displays:
- Disease Name
- Disease Cause
- Recommended Cure

---

# 🛠️ Technologies Used

## Programming Language
- Python

## Deep Learning Frameworks
- TensorFlow
- Keras

## Computer Vision
- OpenCV

## GUI Development
- Tkinter / Flask

## Data Storage
- JSON

## Development Tools
- VS Code
- Jupyter Notebook

---

# 📂 Project Structure

```text
Plant-Disease-Detection/
│
├── dataset/
│   ├── train/
│   ├── validation/
│   └── test/
│
├── models/
│   ├── trained_model.h5
│
├── disease_info/
│   └── disease.json
│
├── images/
│   └── sample_images/
│
├── gui/
│   ├── app.py
│
├── notebooks/
│   ├── training.ipynb
│
├── static/
│
├── templates/
│
├── requirements.txt
│
├── README.md
│
└── main.py
```

---

# 📊 Dataset Information

### Dataset Used
PlantVillage Dataset

### Dataset Contains
- Healthy Leaves
- Diseased Leaves

### Supported Crops
- Apple
- Corn
- Grape
- Potato
- Tomato
- Peach
- Orange
- Strawberry
- Pepper
- Cherry
- Soybean
- Raspberry

### Number of Classes
Approximately 38 disease categories.

---

# 🧠 Deep Learning Model

The project uses a Convolutional Neural Network (CNN) for image classification.

### CNN Layers

#### Convolution Layer
Extracts important image features.

#### Pooling Layer
Reduces image dimensions.

#### Dense Layer
Performs classification.

#### Output Layer
Predicts disease category.

### Activation Functions
- ReLU
- Softmax

### Optimizer
- Adam Optimizer

### Loss Function
- Categorical Crossentropy

---

# 📋 Disease Information Database

The project uses a JSON file to store disease-related information.

Example:

```json
{
  "name": "Tomato Early Blight",
  "cause": "Alternaria solani fungus",
  "cure": "Apply fungicides and remove infected leaves"
}
```

---

# 📈 Results

### Model Performance

| Metric | Value |
|----------|---------|
| Training Accuracy | 95% |
| Validation Accuracy | 93% |
| Testing Accuracy | 92% |

### Advantages

- Fast prediction
- High accuracy
- Easy to use
- Cost-effective
- Supports early disease detection

---

# 🧪 Testing

### Test Case 1
Input: Diseased Leaf Image

Expected Output:
Correct Disease Prediction

Result:
Passed ✅

---

### Test Case 2
Input: Healthy Leaf Image

Expected Output:
Healthy

Result:
Passed ✅

---

### Test Case 3
Input: Invalid File

Expected Output:
Error Message

Result:
Passed ✅

---

# ⚙️ Installation Guide

### Clone Repository

```bash
git clone https://github.com/yourusername/Plant-Disease-Detection.git
```

### Navigate to Project Folder

```bash
cd Plant-Disease-Detection
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

or

```bash
python main.py
```

---



# 🔮 Future Enhancements

- Mobile Application Development
- Real-Time Camera Detection
- IoT-Based Smart Farming
- Cloud Integration
- Multi-Language Support
- More Crop and Disease Categories
- Weather-Based Disease Prediction

---

# 🌍 Applications

- Smart Agriculture
- Precision Farming
- Crop Monitoring
- Agricultural Research
- Farmer Assistance Systems

---

# 👨‍💻 Team Members

### Satrajit Sahu
Backend Developer

### Ganta Dany Vikram
Frontend Developer

### Podugu Avinash
Database Designer

### Medabalimi Sai Koti
System Integration & Testing

---

# 📚 References

1. Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using Deep Learning for Image-Based Plant Disease Detection.
2. Ferentinos, K. P. (2018). Deep Learning Models for Plant Disease Detection.
3. PlantVillage Dataset.
4. TensorFlow Documentation.
5. OpenCV Documentation.

---

# 📄 License

This project is developed for educational and research purposes.

---

# ⭐ Acknowledgement

We would like to thank Lovely Professional University, our faculty members, and all contributors who supported us throughout the development of this project.

If you found this project useful, please consider giving it a ⭐ on GitHub.

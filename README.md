# FanIQ | فانيك

**FanIQ** is an AI-powered crowd analysis system designed to detect and classify crowd congestion levels at stadium gates using computer vision techniques. It provides a real-time interactive map that visualizes gate congestion levels (low, medium, high) to improve the fan experience and ensure safety.

## Team Members

- أسماء الشهري  
- ديمة المزعل  
- نوره العمار  
- هديل المطيري  

---

## Table of Contents

1. [Problem Statement](#problem-statement)  
2. [Solution Overview](#solution-overview)  
3. [Technologies Used](#technologies-used)  
4. [Dataset](#dataset)  
5. [How It Works](#how-it-works)  
6. [Demo](#demo)  
7. [Challenges & Future Plans](#challenges--future-plans)  

---


## Problem Statement

In large-scale events like football matches and concerts, especially with Saudi Arabia hosting the FIFA World Cup 2030, crowd congestion at gates becomes a major challenge. It can lead to:
- Delayed entry for attendees  
- Higher risk of stampedes  
- Difficulties in managing visitor flow  

---

## Solution Overview

FanIQ provides a smart and real-time solution that:
- Analyzes the congestion level at each gate  
- Displays a **live interactive map** built with Streamlit  
- Supports decision-makers in guiding the crowd to safer gates  

---

## Technologies Used

- Python  
- Streamlit  
- YOLOv8m (for person detection)  
- Roboflow (for dataset and model training)  
- Kaggle (for training environment)  

---

## Dataset

- **Type**: Crowd images with varying densities and annotated people  
- **Source**: [Roboflow - Crowd Counting Dataset](https://universe.roboflow.com/crowd-dataset/crowd-counting-dataset-w3o7w)  
- **Usage**:  
  - Used to train a YOLOv5 model for person detection  
  - Person count is used to determine crowd density levels (low, medium, high)  

---

## How It Works

1. **Data Preparation**  
   - The dataset was labeled and exported from Roboflow in YOLO format  

2. **Model Training**  
   - YOLOv5 was trained on the dataset using a Kaggle notebook environment  

3. **Real-time Visualization**  
   - The trained model predicts people count in images of stadium gates  
   - A Streamlit app displays the crowd status (low/medium/high) in an interactive gate map  

4. **Deployment (optional)**  
   - Can be extended to handle live camera feeds via APIs for real-time crowd tracking  

---

## Demo

Watch our project demo here:  
**[FanIQ Demo Video - Google Drive](https://drive.google.com/file/d/1URNQ-5kOLMAH3fPv2eBFKq-BVOuZnXga)**

---

## Challenges & Future Plans

### Challenges:
- Lack of real-world experimental data  
- Limited access to stadium APIs or real camera feeds  

### Future Plans:
- Improve model accuracy for real-time video analysis  
- Integrate with stadium surveillance systems via APIs  
- Conduct field testing in semi-realistic environments  
- Document technical results and publish a case study  

---

## Summary

FanIQ presents a smart solution to manage crowd congestion in stadiums by using AI to detect people in images and classify gate status. The system aims to enhance fan safety, reduce congestion, and assist organizers in making informed operational decisions.

---

**Thank you for checking out our project!**
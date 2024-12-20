# 🚆 The Effect of Uber Subsidy on BART Ridership  

This project was created as part of the **IEOR 174 Final Report** for **Fall 2024**. It explores how subsidizing Uber rides can enhance BART ridership and revenue, while promoting environmental sustainability. By analyzing a mix of Uber, BART, and driving costs, we aim to identify the optimal subsidy level that maximizes BART's benefits.  

---

## 📊 Project Overview  
- **Course:** IEOR 174, Fall 2024  
- **Authors:** Andrew Song, Helena Su, Jaewon Lee, Scott Young  
- **Objective:** Analyze the financial and environmental impact of Uber subsidies on BART ridership.  
- **Key Features:**  
  - Dynamic models for **BART pricing**, **Uber pricing**, and **driving costs**.  
  - Interactive visualizations built with **Streamlit**.  
  - Insights into the optimal subsidy level to boost revenue and reduce carbon emissions.  

---

🌐 Live Demo

You can view the live demo of the project [here](https://bart-uber-subsidy.streamlit.app/).

Link: https://bart-uber-subsidy.streamlit.app/

---

## 🚀 Getting Started  

### Prerequisites  
Make sure you have Python 3.7+ installed along with the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the App
Launch the Streamlit application:

```bash
streamlit run app.py
```

This will open the app in your default web browser.

---

## 📖 Key Features
### 🚖 Uber Pricing Model
- Uses Uber Price Estimator data.
- Cost and duration modeled dynamically using Akima interpolation.
### 🚆 BART Pricing Model
- Fixed BART fare combined with subsidized Uber costs for first-/last-mile trips.
- Analyzes subsidy levels for revenue optimization.
### 🚗 Driving Cost Model
- Estimates fuel costs for trips using real-world distance and efficiency values.
### 🌍 Environmental Impact
- Promotes sustainable transportation by increasing BART ridership, reducing car usage, and leveraging BART's 97% low-/zero-carbon power sources.

---

## 🤝 Contributors
- Andrew Song
- Helena Su
- Jaewon Lee
- Scott Young

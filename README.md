🌍 Laxminarayan Global Trade Intelligence
An Industry-Grade Data Visualization Dashboard for Global Trade & Logistics.

🔗 Live Demo Link
📌 Project Overview
The Laxminarayan Global Trade Intelligence dashboard is a high-performance tool built for exporters and importers to analyze unit economics and market trends. It transitions from a simple margin calculator into a full-scale business intelligence suite, offering real-time data fetching and macroeconomic visualizations.

This project demonstrates proficiency in Python, Data Analytics, and Full-Stack AI/ML Dashboard Development.

🚀 Key Features
Searchable HSN Database: Auto-fetches product names, base costs (USD), and duty percentages based on Harmonized System codes.

Live Currency Engine: Integrated with a real-time Exchange Rate API to provide instant INR/USD toggles across all metrics and charts.

"Bring Your Own Data" (BYOD): A dynamic CSV uploader that allows users to inject their own product datasets into the system on the fly.

Professional Analytics Suite:

Unit Economics: Metric cards showing live profit margins and total ROI.

Cost Breakdown: A modern Donut Chart visualizing the split between production, freight, insurance, and duty.

Market Volatility: 30-day price tracking using interactive line charts.

Macro Trends: 5-year historical Bar and Area charts for trade volume and price trajectory.

🛠️ Technical Stack
Frontend/App Framework: Streamlit

Data Processing: Pandas, NumPy

Interactive Graphics: Plotly (Express & Graph Objects)

APIs: ExchangeRate-API (Live Currency Data)

📂 Installation & Setup
To run this project locally, follow these steps:

Clone the repository:

Bash
git clone https://github.com/your-username/global-trade-intelligence.git
cd global-trade-intelligence
Create and activate a virtual environment:

Bash
python -m venv env
# Windows
env\Scripts\activate
# Mac/Linux
source env/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run app.py
📊 Data Format for Uploader
To use the Custom CSV Uploader, ensure your file has the following headers:
HSN, Name, Price_USD, Duty

👨‍💻 Developed By
Sujal Makwana
Student at IIIT Vadodara (B.Sc. in AI & ML)
Visionary Founder of the Laxminarayan Group of Companies

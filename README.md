# STORM - Balloon Launch Probability and Movement Prediction Model

STORM (Strategic Tracking of Object Routes & Movement) is a model that predicts the probability of **North Korean balloon launches** and estimates their potential movement paths.

## Features
- **Wind direction and speed analysis** → Compares user input with past balloon launch data to determine similarity.
- **News frequency integration** → Analyzes North Korean leaflet-related news to assess launch likelihood.
- **Route visualization** → Displays the expected movement path on an interactive map.

## Installation and Usage
```bash
# Clone the repository
git clone https://github.com/your_username/storm-prediction.git
cd storm-prediction

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run streamlit_app.py

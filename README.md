# STORM - Balloon Launch Probability and Movement Prediction Model

STORM (Strategic Tracking of Object Routes & Movement) is an AI-based model that predicts the probability of **North Korean balloon launches** and estimates their potential movement paths.

## Features
- **Wind direction and speed analysis** → Compares user input with past balloon launch data to determine similarity.
- **News frequency integration** → Analyzes North Korean leaflet-related news to assess launch likelihood.
- **Route visualization** → Displays the expected movement path on an interactive map with multiple trajectory variations.

## Installation and Usage
```bash
# Clone the repository
git clone https://github.com/bibaesj/storm.git
cd storm

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run stormwebsimilar.py

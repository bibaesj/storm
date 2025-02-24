import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

locations = {
    "Gaeseong": {"latitude": 37.9708, "longitude": 126.5544},
    "Haeju": {"latitude": 38.0406, "longitude": 125.7146},
    "Osan": {"latitude": 37.1522, "longitude": 127.0703},
    "Gwangju": {"latitude": 35.1595, "longitude": 126.8526},
}

def get_region(lat, lon):
    if lat >= 37.5 and lon >= 126.0:
        return "Gaeseong"
    elif lat >= 37.5 and lon < 126.0:
        return "Haeju"
    elif lat >= 36.0 and lat < 37.5:
        return "Osan"
    else:
        return "Gwangju"


MEAN_TARGET_SIMILARITY = 0.8450

weight_direction = 0.5002
weight_speed = 0.4628
weight_issue = 0.2955

mean_direction = 286.91
mean_speed = 15.89
mean_direction_sin = np.sin(np.radians(mean_direction))
mean_direction_cos = np.cos(np.radians(mean_direction))

def calculate_weighted_similarity(direction, speed, issue):
    direction_sin = np.sin(np.radians(direction))
    direction_cos = np.cos(np.radians(direction))

    direction_similarity = (direction_sin * mean_direction_sin + 
                            direction_cos * mean_direction_cos)

    max_speed_diff = 50  
    speed_similarity = 1 - (np.abs(speed - mean_speed) / max_speed_diff)

    issue_similarity = 1 if issue == 1 else 0

    weighted_similarity = (
        weight_speed * speed_similarity +
        weight_direction * direction_similarity +
        weight_issue * issue_similarity
    )

    probability = weighted_similarity * 100
    return weighted_similarity, probability



st.set_page_config(page_title="STORM - 풍선 예측 및 이동 경로", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    st.markdown("""
    <h2 style='text-align: center; color: #00274D; font-weight: bold;'>
    🎈 STORM <br>
    <span style='font-size: 20px; font-weight: normal;'>
    북 대남 오물 쓰레기풍선 부양 가능성 및 이동경로 예측 모델
    </span>
    </h2>
    <p style='text-align: center; font-size: 14px; font-weight: bold; color: #555; margin-top: -10px;'>
    made by. 화생방방어연구소 화생방AI연구과
    </p>
    """, unsafe_allow_html=True)


    st.markdown("""
    ### 📌 STORM 모델 개요
    **STORM (Strategic Tracking of Object Routes & Movement) 모델**은  
    과거 32차례의 풍선 부양 사례를 기반으로 **북한의 풍선 부양 가능성을 예측하는 인공지능 모델**입니다.

    **🔎 분석 요소**
    - **🌪️ 풍향 (Wind Direction):** 풍선 이동 경로에 미치는 영향 분석  
    - **💨 풍속 (Wind Speed):** 풍선이 충분한 부력을 얻을 수 있는지 평가  
    - **📰 이슈 발생 여부 (Issue Factor):** 미디어데이터 분석을 통해 '대북전단' 빈도 기준으로 풍선을 보낼 가능성이 높은지 판단  

    **📊 분석 방식**
    1. 사용자가 입력한 기상 조건을 **과거 실제 풍선 부양이 있었던 날**과 비교하여 유사도를 계산합니다.  
    2. 기상 데이터가 과거 풍선 부양 사례와 유사할수록 **높은 확률로 풍선이 부양될 가능성이 있음**을 나타냅니다.  
    3. 계산된 유사도는 **평균 유사도(0.845)**를 기준으로 판단됩니다:  
       - **📈 평균 이상:** 풍선이 부양될 가능성이 높음  
       - **📉 평균 이하:** 풍선이 부양되지 않을 가능성이 높음  

    🌍 또한, 사용자가 입력한 데이터를 기반으로 **풍선 이동 경로를 지도에서 시뮬레이션하여 시각적으로 확인**할 수 있습니다.  
       - ** 30분 간격 이동 경로**를 표시하며, **풍향 편차에 따른 이동 경로 시뮬레이션**을 제공합니다.  

    ✅ **좌측 사이드바에서 풍향과 풍속을 입력하고, 예측을 실행해보세요!**  
    """, unsafe_allow_html=True)

    st.sidebar.header("🌪️ 풍향·풍속 입력")
    regions = ["Gaeseong", "Haeju", "Osan", "Gwangju"]

    direction_inputs = {}
    speed_inputs = {}

    for region in regions:
        col1, col2 = st.sidebar.columns(2)
        direction = col1.slider(f"{region} 풍향 (도)", 0, 360, 180)
        speed = col2.slider(f"{region} 풍속 (Knots)", 0.0, 50.0, 5.0)
        direction_inputs[region] = direction
        speed_inputs[region] = speed

    avg_direction = np.mean(list(direction_inputs.values()))
    avg_speed = np.mean(list(speed_inputs.values()))

    issue_dates = [
        "2024-05-28", "2024-06-01", "2024-06-08", "2024-06-09", "2024-06-24", "2024-06-25", 
        "2024-06-26", "2024-07-18", "2024-07-21", "2024-07-24", "2024-08-10", "2024-09-04", 
        "2024-09-05", "2024-09-06", "2024-09-07", "2024-09-08", "2024-09-11", "2024-09-14", 
        "2024-09-15", "2024-09-18", "2024-09-22", "2024-10-02", "2024-10-04", "2024-10-07", 
        "2024-10-11", "2024-10-19", "2024-10-24", "2024-11-18", "2024-11-28"
    ]
    
    selected_date = st.sidebar.date_input(
    "예측할 날짜 선택",
    datetime.today(),
    min_value=datetime(2024, 5, 1),  
    max_value=datetime.today() 
)
    issue_value = 1 if selected_date.strftime("%Y-%m-%d") in issue_dates else 0

    if st.sidebar.button("🚀 풍선 부양 가능성 예측 실행"):
        st.session_state.avg_direction = avg_direction
        st.session_state.avg_speed = avg_speed
        st.session_state.issue_value = issue_value
        st.session_state.direction_inputs = direction_inputs
        st.session_state.speed_inputs = speed_inputs
        st.session_state.page = "result"
        st.rerun()

elif st.session_state.page == "result":
    st.title("🎈 STORM - 풍선 예측 및 이동 경로 분석")
    st.subheader("📊 예측 결과")

    avg_direction = st.session_state.avg_direction
    avg_speed = st.session_state.avg_speed
    issue_value = st.session_state.issue_value
    direction_inputs = st.session_state.direction_inputs
    speed_inputs = st.session_state.speed_inputs

    weighted_similarity, prediction_prob = calculate_weighted_similarity(avg_direction, avg_speed, issue_value)

    st.write(f"🚀 **실제 풍선을 부양한 날짜와 {prediction_prob:.2f}% 유사합니다.**")

    if weighted_similarity >= MEAN_TARGET_SIMILARITY:
        st.warning("⚠️ 풍선이 부양될 가능성이 높습니다!")
    else:
        st.success("✅ 풍선이 부양되지 않을 가능성이 높습니다.")

    st.sidebar.header("📍 이동 경로 설정")
    start_lat = st.sidebar.number_input("출발 위도", value=38.3, format="%.4f")
    start_lon = st.sidebar.number_input("출발 경도", value=126.6, format="%.4f")

    m = folium.Map(location=[start_lat, start_lon], zoom_start=7)
    folium.Marker([start_lat, start_lon], popup="출발 위치", icon=folium.Icon(color="red")).add_to(m)

    angle_offsets = [-15, -10, -5, 0, 5, 10, 15]  
    colors = ["#00FF66", "#FFFF00", "#FF6600", "#FF0000", "#FF6600", "#FFFF00", "#00FF66"]  

    for idx, offset in enumerate(angle_offsets):
        trajectory = [(start_lat, start_lon)]  
        current_lat, current_lon = start_lat, start_lon
        current_region = get_region(current_lat, current_lon)

        for t in range(14):  
            wind_speed_mps = speed_inputs[current_region] * 0.5144
            wind_direction = direction_inputs[current_region]
            adjusted_direction = (wind_direction + offset + 180) % 360 

            dx = wind_speed_mps * np.sin(np.radians(adjusted_direction)) * 1800
            dy = wind_speed_mps * np.cos(np.radians(adjusted_direction)) * 1800

            dlat = dy / 111320
            dlon = dx / (111320 * np.cos(np.radians(current_lat)))

            current_lat += dlat
            current_lon += dlon
            trajectory.append((current_lat, current_lon)) 

            if current_lat <= 38.0:
                current_region = get_region(current_lat, current_lon)

            folium.CircleMarker(
                location=[current_lat, current_lon],
                radius=3,  
                color=colors[idx],  
                fill=True,
                fill_opacity=0.6
            ).add_to(m)

        folium.PolyLine(
            locations=trajectory, 
            color=colors[idx],  
            weight=2,  
            opacity=0.8
        ).add_to(m)


    folium.PolyLine(trajectory, color=colors[idx], weight=2, opacity=0.6).add_to(m)

    st.subheader("🌏 이동 경로 시각화")
    folium_static(m)

    if st.button("🔙 새로운 예측 실행"):
        st.session_state.page = "main"
        st.rerun()

#!/usr/bin/env python3
"""
智慧家居監控儀表板
功能：即時顯示感測器資料並儲存至 Excel
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import threading

# 匯入自訂模組
from mqtt_subscriber import MQTTSubscriber
from data_storage import DataStorage


# 頁面設定
st.set_page_config(
    page_title="智慧家居監控儀表板",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自訂 CSS 樣式
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card-light-on {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-card-light-off {
        background: linear-gradient(135deg, #757F9A 0%, #D7DDE8 100%);
    }
    .metric-card-temp {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card-humid {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .status-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .status-connected {
        background-color: #38ef7d;
        box-shadow: 0 0 10px #38ef7d;
    }
    .status-disconnected {
        background-color: #f5576c;
        box-shadow: 0 0 10px #f5576c;
    }
</style>
""", unsafe_allow_html=True)


# 全域變數用於跨執行緒通訊
import queue
data_queue = queue.Queue()

def on_mqtt_data_received(data):
    """MQTT 資料接收回調函數 (在背景執行緒運行)"""
    # 將資料放入佇列，讓主執行緒處理
    data_queue.put(data)

def process_mqtt_data():
    """處理佇列中的 MQTT 資料 (在主執行緒運行)"""
    while not data_queue.empty():
        data = data_queue.get()
        
        # 更新 session state
        st.session_state.sensor_data = data
        
        # 加入歷史記錄
        st.session_state.history_data.append(data.copy())
        
        # 只保留最近 200 筆資料
        if len(st.session_state.history_data) > 200:
            st.session_state.history_data = st.session_state.history_data[-200:]
        
        # 儲存到 Excel（每 5 秒儲存一次，避免過於頻繁）
        current_time = time.time()
        if (st.session_state.last_save_time is None or 
            current_time - st.session_state.last_save_time > 5):
            
            if data['timestamp']:
                st.session_state.data_storage.save_data(
                    timestamp=data['timestamp'],
                    light_status=data['light_status'],
                    temperature=data['temperature'],
                    humidity=data['humidity']
                )
                st.session_state.last_save_time = current_time

def init_mqtt_connection():
    """初始化 MQTT 連線"""
    if st.session_state.mqtt_subscriber is None:
        subscriber = MQTTSubscriber()
        # 先暫時設定 callback，稍後會更新
        subscriber.set_callback(on_mqtt_data_received)
        
        if subscriber.connect():
            st.session_state.mqtt_subscriber = subscriber
        else:
            return False
    
    # 關鍵修正：每次 Rerun 都必須更新 callback
    # 這樣才能確保 callback 引用的是本次執行建立的 data_queue
    if st.session_state.mqtt_subscriber:
        st.session_state.mqtt_subscriber.set_callback(on_mqtt_data_received)
        
    return True


def create_temperature_humidity_chart(history_data):
    """建立溫濕度趨勢圖"""
    if not history_data or len(history_data) == 0:
        return None
    
    # 準備資料
    df = pd.DataFrame(history_data)
    
    # 建立雙 Y 軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 溫度線
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            name="溫度",
            line=dict(color='#f5576c', width=3),
            mode='lines+markers'
        ),
        secondary_y=False
    )
    
    # 濕度線
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            name="濕度",
            line=dict(color='#00f2fe', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # 設定 X 軸
    fig.update_xaxes(title_text="時間")
    
    # 設定 Y 軸
    fig.update_yaxes(title_text="溫度 (°C)", secondary_y=False)
    fig.update_yaxes(title_text="濕度 (%)", secondary_y=True)
    
    # 設定佈局
    fig.update_layout(
        title="溫濕度歷史趨勢",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


# 主程式
def main():
    # 初始化 Session State
    if 'mqtt_subscriber' not in st.session_state:
        st.session_state.mqtt_subscriber = None
        st.session_state.data_storage = DataStorage()
        st.session_state.sensor_data = {
            "light_status": "OFF",
            "temperature": 0.0,
            "humidity": 0.0,
            "timestamp": None
        }
        st.session_state.history_data = []
        st.session_state.last_save_time = None

    # 處理接收到的 MQTT 資料
    process_mqtt_data()

    # 標題
    st.markdown('<div class="main-title">🏠 智慧家居監控儀表板</div>', unsafe_allow_html=True)
    
    # 當前時間與連線狀態
    col_time, col_status = st.columns([3, 1])
    
    with col_time:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f'<div class="subtitle">📅 {current_time}</div>', unsafe_allow_html=True)
    
    with col_status:
        # 初始化 MQTT 連線
        if init_mqtt_connection():
            is_connected = st.session_state.mqtt_subscriber.is_connected()
            status_class = "status-connected" if is_connected else "status-disconnected"
            status_text = "已連線" if is_connected else "未連線"
            st.markdown(
                f'<div style="text-align: right; padding-top: 10px;">'
                f'<span class="status-indicator {status_class}"></span>'
                f'<span>{status_text}</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.error("❌ 無法連接到 MQTT Broker")
    
    st.markdown("---")
    
    # 狀態卡片區
    col1, col2, col3 = st.columns(3)
    
    data = st.session_state.sensor_data
    
    with col1:
        # 電燈狀態
        light_status = data.get('light_status', 'OFF')
        card_class = "metric-card-light-on" if light_status == "ON" else "metric-card-light-off"
        icon = "💡" if light_status == "ON" else "🌑"
        
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="metric-label">電燈狀態</div>
            <div class="metric-value">{icon} {light_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # 溫度
        temperature = data.get('temperature', 0.0)
        st.markdown(f"""
        <div class="metric-card metric-card-temp">
            <div class="metric-label">客廳溫度</div>
            <div class="metric-value">🌡️ {temperature:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 濕度
        humidity = data.get('humidity', 0.0)
        st.markdown(f"""
        <div class="metric-card metric-card-humid">
            <div class="metric-label">客廳濕度</div>
            <div class="metric-value">💧 {humidity:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 圖表區
    st.subheader("📊 溫濕度歷史趨勢")
    
    if st.session_state.history_data and len(st.session_state.history_data) > 0:
        chart = create_temperature_humidity_chart(st.session_state.history_data)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("📡 等待接收感測器資料...")
    
    # 資料表區
    st.subheader("📋 最近的資料記錄")
    
    if st.session_state.history_data and len(st.session_state.history_data) > 0:
        # 顯示最近 20 筆資料
        df = pd.DataFrame(st.session_state.history_data[-20:])
        df = df[['timestamp', 'light_status', 'temperature', 'humidity']]
        df.columns = ['時間', '電燈狀態', '溫度 (°C)', '濕度 (%)']
        
        # 反轉順序，最新的在上面
        df = df.iloc[::-1].reset_index(drop=True)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📡 等待接收感測器資料...")
    
    # 頁尾資訊
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        total_records = len(st.session_state.history_data)
        st.metric("記憶體中的資料筆數", f"{total_records} 筆")
    
    with col_info2:
        excel_files = st.session_state.data_storage.get_all_files()
        st.metric("Excel 檔案數量", f"{len(excel_files)} 個")
    
    with col_info3:
        if data.get('timestamp'):
            last_update = data['timestamp'].strftime("%H:%M:%S")
            st.metric("最後更新時間", last_update)
        else:
            st.metric("最後更新時間", "---")
    
    # 自動重新整理
    time.sleep(1)
    st.rerun()


if __name__ == "__main__":
    main()
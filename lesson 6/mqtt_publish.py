#!/usr/bin/env python3
"""
MQTT Publisher 範例程式
功能：發送訊息到 MQTT Broker
"""

import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# MQTT 設定
BROKER = "localhost"  # 本地 Raspberry Pi 的 MQTT Broker
PORT = 1883
TOPIC = "客廳/topic"
CLIENT_ID = "pi_publisher_001"

# 連線成功的回調函數
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 成功連接到 MQTT Broker！")
        print(f"   Broker: {BROKER}")
        print(f"   Port: {PORT}")
    else:
        print(f"❌ 連接失敗，錯誤代碼: {rc}")

# 發布成功的回調函數
def on_publish(client, userdata, mid):
    print(f"📤 訊息已發布 (Message ID: {mid})")

# 建立 MQTT 客戶端
print("🚀 正在建立 MQTT 客戶端...")
client = mqtt.Client(client_id=CLIENT_ID)

# 設定回調函數
client.on_connect = on_connect
client.on_publish = on_publish

# 連接到 Broker
print(f"🔌 正在連接到 {BROKER}:{PORT}...")
try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()  # 啟動背景執行緒處理網路流量
    
    # 等待連接完成
    time.sleep(2)
    
    # 發布多個訊息
    print(f"\n📡 開始發布訊息到主題: {TOPIC}")
    print("-" * 50)
    
    for i in range(5):
        # 準備訊息內容
        message_data = {
            "序號": i + 1,
            "時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "來源": "Raspberry Pi",
            "訊息": f"這是第 {i + 1} 則測試訊息"
        }
        
        # 轉換為 JSON 字串
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        # 發布訊息
        result = client.publish(TOPIC, message_json, qos=1)
        
        # 檢查發布狀態
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ 訊息 {i + 1} 已送出")
            print(f"   內容: {message_json}")
        else:
            print(f"❌ 訊息 {i + 1} 發送失敗")
        
        # 等待 2 秒再發送下一則
        time.sleep(2)
    
    print("-" * 50)
    print("✅ 所有訊息發送完成！")
    
    # 等待確保所有訊息都已發送
    time.sleep(2)
    
except Exception as e:
    print(f"❌ 發生錯誤: {e}")

finally:
    # 斷開連接
    client.loop_stop()
    client.disconnect()
    print("🔌 已斷開連接")

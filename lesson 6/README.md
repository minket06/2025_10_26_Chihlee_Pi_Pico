# 智慧家居監控儀表板 (Smart Home Dashboard)

這是一個基於 Streamlit 的即時監控儀表板，用於顯示智慧家居的感測器資料（電燈、溫度、濕度）。系統透過 MQTT 協定訂閱數據，並將資料即時顯示於網頁上，同時自動儲存為 Excel 檔案。

## 功能特色

- **即時監控**：
  - 💡 電燈狀態 (ON/OFF)
  - 🌡️ 客廳溫度 (°C)
  - 💧 客廳濕度 (%)
- **視覺化圖表**：即時更新的溫濕度趨勢圖 (雙 Y 軸)。
- **資料持久化**：自動將接收到的資料儲存為 Excel 檔案 (`.xlsx`)，每日自動分檔。
- **美觀介面**：使用現代化的卡片式設計與響應式佈局。

## 系統需求

- Python 3.10+
- MQTT Broker (預設使用 localhost:1883)

## 安裝說明

本專案使用 `uv` 進行套件管理。

1. **安裝相依套件**：
   ```bash
   uv sync
   ```

## 快速開始

### 1. 啟動 MQTT Broker (若尚未啟動)
確保您的 Raspberry Pi 上已經運行了 MQTT Broker (如 Mosquitto)。
```bash
sudo systemctl start mosquitto
```

### 2. 啟動模擬感測器 (測試用)
如果您還沒有實際的硬體裝置，可以使用我們提供的模擬程式來發送測試資料：
```bash
# 在 lesson 6 資料夾內執行
uv run python mqtt_publisher_test.py
```
*此程式會定期發送模擬的溫濕度與電燈狀態資料。*

### 3. 啟動監控儀表板
開啟一個新的終端機視窗，執行 Streamlit 應用程式：
```bash
# 在 lesson 6 資料夾內執行
uv run streamlit run app.py
```

應用程式啟動後，瀏覽器應會自動開啟 `http://localhost:8501`。

## 檔案結構

- `app.py`: Streamlit 主應用程式，負責介面顯示與邏輯整合。
- `mqtt_subscriber.py`: MQTT 訂閱模組，負責接收感測器資料。
- `data_storage.py`: 資料儲存模組，負責 Excel 檔案讀寫。
- `mqtt_publisher_test.py`: 測試用的 MQTT 發布者，用於模擬感測器。
- `PRD.md`: 產品需求文件。

## MQTT 設定

預設使用以下 Topic (可於 `mqtt_subscriber.py` 中修改)：
- 電燈: `home/living_room/light`
- 溫度: `home/living_room/temperature`
- 濕度: `home/living_room/humidity`

## Pico 端發送格式說明

若您使用 Raspberry Pi Pico (MicroPython) 作為感測器裝置，請依照以下格式發送 MQTT 訊息：

### 1. Topic 與 Payload 格式

| 監控項目 | Topic (主題) | Payload (JSON 格式) | 範例 |
| :--- | :--- | :--- | :--- |
| **溫度** | `home/living_room/temperature` | `{"value": <數值>}` | `{"value": 25.5}` |
| **濕度** | `home/living_room/humidity` | `{"value": <數值>}` | `{"value": 60.2}` |
| **電燈** | `home/living_room/light` | `{"status": "<狀態>"}` | `{"status": "ON"}` |

### 2. Pico MicroPython 範例程式

請將以下程式碼儲存為 `main.py` 並上傳至您的 Raspberry Pi Pico W：

```python
import network
import time
import json
from umqtt.simple import MQTTClient
from machine import Pin
import random # 僅用於模擬數據，實際使用請移除

# --- 設定區 ---
WIFI_SSID = "您的WiFi名稱"
WIFI_PASSWORD = "您的WiFi密碼"
MQTT_BROKER = "192.168.X.X"  # 請改為 Raspberry Pi 的 IP
CLIENT_ID = "pico_sensor_01"

# --- 連接 Wi-Fi ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('正在連接 Wi-Fi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    print('\nWi-Fi 已連線! IP:', wlan.ifconfig()[0])

# --- 連接 MQTT ---
def connect_mqtt():
    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER)
        client.connect()
        print('MQTT Broker 已連線!')
        return client
    except Exception as e:
        print('MQTT 連線失敗:', e)
        return None

# --- 主程式 ---
def main():
    connect_wifi()
    client = connect_mqtt()
    
    while True:
        if client:
            try:
                # 1. 模擬溫度數據 (實際請讀取 DHT11/DHT22)
                temp = 20 + random.randint(0, 10) + random.random()
                temp_payload = json.dumps({"value": round(temp, 1)})
                client.publish("home/living_room/temperature", temp_payload)
                print(f"發送溫度: {temp_payload}")

                # 2. 模擬濕度數據
                humid = 50 + random.randint(0, 20) + random.random()
                humid_payload = json.dumps({"value": round(humid, 1)})
                client.publish("home/living_room/humidity", humid_payload)
                print(f"發送濕度: {humid_payload}")

                # 3. 模擬電燈狀態 (隨機切換)
                status = "ON" if random.choice([True, False]) else "OFF"
                light_payload = json.dumps({"status": status})
                client.publish("home/living_room/light", light_payload)
                print(f"發送電燈: {light_payload}")

            except Exception as e:
                print("發送錯誤:", e)
                # 斷線重連機制
                try:
                    client.connect()
                except:
                    pass
        else:
            print("嘗試重新連接 MQTT...")
            client = connect_mqtt()
            
        time.sleep(5) # 每 5 秒發送一次

if __name__ == "__main__":
    main()
```

## 資料儲存

資料會儲存在 `lesson 6` 目錄下，檔名格式為 `sensor_data_YYYYMMDD.xlsx`。
包含欄位：`timestamp`, `light_status`, `temperature`, `humidity`。

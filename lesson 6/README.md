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

```python
import network
import time
import json
from umqtt.simple import MQTTClient

# MQTT 設定 (請修改為您的 Broker IP)
MQTT_BROKER = "192.168.X.X"
CLIENT_ID = "pico_sensor_01"

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.connect()
    return client

# 發送資料範例
def publish_data(client):
    # 發送溫度
    temp_data = json.dumps({"value": 26.5})
    client.publish("home/living_room/temperature", temp_data)
    
    # 發送濕度
    humid_data = json.dumps({"value": 70.0})
    client.publish("home/living_room/humidity", humid_data)
    
    # 發送電燈狀態
    light_data = json.dumps({"status": "ON"})
    client.publish("home/living_room/light", light_data)

# 主程式邏輯...
```

## 資料儲存

資料會儲存在 `lesson 6` 目錄下，檔名格式為 `sensor_data_YYYYMMDD.xlsx`。
包含欄位：`timestamp`, `light_status`, `temperature`, `humidity`。

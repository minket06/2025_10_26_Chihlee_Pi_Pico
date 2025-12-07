# lesson6_Teacher 專案分析報告

這個專案是一個基於 Flask 的物聯網 (IoT) 監控儀表板，主要功能是透過 MQTT 協定接收感測器數據（如溫度、濕度、電燈狀態），並即時顯示在網頁上。它被設計用來替代 Streamlit 版本，以解決在 Raspberry Pi 上可能遇到的相容性或效能問題。

## 1. 專案架構與檔案功能

| 檔案名稱 | 用途 | 關鍵技術 |
| :--- | :--- | :--- |
| **`app_flask.py`** | 後端主程式，負責網頁伺服器、MQTT 連線與數據處理。 | Flask, Flask-SocketIO, Paho-MQTT, Threading |
| **`templates/index.html`** | 前端頁面，負責介面顯示與即時更新。 | HTML5, CSS3, JavaScript, Chart.js, Socket.IO Client |
| **`generate_test_data.py`** | 生成模擬的歷史數據 CSV/Excel 檔。 | CSV, OpenPyXL, Random |
| **`test_mqtt_publish.py`** | 模擬感測器裝置，發送測試 MQTT 訊息。 | Paho-MQTT, JSON |
| **`start.sh`** | 啟動腳本，自動檢查數據並啟動 Flask。 | Bash Shell |

---

## 2. 程式邏輯詳細分析

### A. 後端邏輯 (`app_flask.py`)

1.  **初始化與全域設定**:
    *   使用 `Flask` 建立 Web 伺服器。
    *   使用 `SocketIO` 建立 WebSocket 通道，實現伺服器主動推播數據給瀏覽器 (Server-Push)。
    *   定義 `MQTT_BROKER`, `MQTT_PORT`, `MQTT_TOPIC` 等連線資訊。

2.  **數據持久化 (CSV 處理)**:
    *   **`load_from_csv()`**: 程式啟動時，讀取 `sensor_data.csv`，將最後 100 筆數據載入記憶體 (`sensor_data` 列表)，作為歷史趨勢圖的基礎。
    *   **`save_to_csv(data)`**: 每次收到新 MQTT 訊息時，將數據追加寫入 CSV 檔案，確保重啟後數據不遺失。

3.  **MQTT 處理 (核心邏輯)**:
    *   使用 `paho.mqtt.client` 建立客戶端。
    *   **背景執行**: 透過 `threading.Thread` 啟動 `start_mqtt` 函數，確保 MQTT 監聽與 Flask 網頁伺服器並行運作，不會互相卡住。
    *   **`on_message` 回調**:
        1.  收到訊息後解析 JSON payload。
        2.  更新全域變數 `latest_data` 和 `sensor_data`。
        3.  維持記憶體中僅保留最新的 100 筆數據 (`pop(0)`)。
        4.  寫入 CSV。
        5.  **關鍵**: 呼叫 `socketio.emit('new_data', latest_data)`，即時通知所有連線中的瀏覽器更新畫面。

4.  **API 接口**:
    *   `/`: 回傳 `index.html` 頁面。
    *   `/api/latest`: 提供給前端 Polling (輪詢) 用，回傳最新一筆狀態。
    *   `/api/history`: 回傳最近 100 筆歷史數據，用於繪製圖表。

### B. 前端邏輯 (`templates/index.html`)

1.  **介面結構**:
    *   **狀態列**: 顯示 MQTT 連線狀態與最後更新時間。
    *   **感測器卡片**: 用大字體顯示電燈狀態、溫度、濕度。
    *   **圖表區**: 使用 `<canvas>` 繪製歷史趨勢圖。

2.  **即時更新機制**:
    *   **WebSocket (`socket.on('new_data', ...)`)**: 這是最即時的更新方式。當後端收到 MQTT 訊息時，前端會立即觸發此事件，呼叫 `fetchLatest()` 更新介面數字。
    *   **定期輪詢 (`setInterval`)**: 設定每 5 秒呼叫一次 `fetchHistory()`，確保圖表與後端歷史數據同步 (即使沒有新 MQTT 訊息，也能確保圖表顯示正常)。

3.  **視覺化 (Chart.js)**:
    *   建立一個雙 Y 軸折線圖 (Line Chart)。
    *   左軸顯示溫度 (紅色)，右軸顯示濕度 (藍色)。
    *   `updateChart()` 函式負責將後端傳來的歷史陣列轉換為圖表所需的 Label 與 Dataset。

---

## 3. 您可以手動修改的部分

### 🛠️ 1. 修改 MQTT 設定 (針對真實硬體)
如果您要連接真實的 Arduino/ESP32 裝置，或更換 Broker：
*   **檔案**: `app_flask.py`
*   **位置**: 第 19-21 行
    ```python
    MQTT_BROKER = "您的Broker IP"  # 例如 "192.168.1.100"
    MQTT_PORT = 1883             # 如果有加密可能改為 8883
    MQTT_TOPIC = "您的/自訂/主題" # 例如 "Home/LivingRoom/Sensor"
    ```

### 🛠️ 2. 調整歷史數據保留數量
如果希望圖表顯示更長或更短時間的趨勢：
*   **檔案**: `app_flask.py`
*   **位置**: 第 54 行 (`loaded_data[-100:]`) 與 第 119 行 (`if len(sensor_data) > 100:`)
*   **修改**: 將 `100` 改為您想要的數字 (例如 `500`)。

### 🎨 3. 修改網頁外觀 (CSS)
您可以自訂儀表板的顏色、字型或排版：
*   **檔案**: `templates/index.html` (中的 `<style>` 區塊)
*   **範例**:
    *   **背景顏色**: 修改 `body` 的 `background` (第 18 行)。
    *   **卡片樣式**: 修改 `.sensor-card` (第 71 行)。
    *   **電燈圖示**: 修改 `.light-on` 和 `.light-off` 的顏色 (第 115-122 行)。

### 📊 4. 修改圖表設定
調整圖表的顏色、類型或座標軸範圍：
*   **檔案**: `templates/index.html` (JavaScript 區塊)
*   **位置**: `const chart = new Chart(...)` (第 200 行附近)
*   **修改**:
    *   `borderColor`: 修改線條顏色。
    *   `y` 和 `y1` scales: 可以加入 `min` 和 `max` 屬性來固定座標軸範圍，例如：
        ```javascript
        y: {
            min: 0,
            max: 50,
            // ... 其他設定
        }
        ```

### 🔌 5. 新增更多感測器數據
如果您想加入新的數據 (例如 PM2.5)：
1.  **後端 (`app_flask.py`)**:
    *   在 `on_message` (第 103 行附近) 加入解析程式碼：`pm25 = data_dict.get('pm25', 0)`。
    *   在 `latest_data` 與 `csv_data` 字典中加入新欄位。
    *   修改 `save_to_csv` 的 `fieldnames`。
2.  **前端 (`index.html`)**:
    *   在 HTML 新增一個 `<div class="sensor-card">` 來顯示 PM2.5。
    *   在 `updateDisplay` 函式中加入更新邏輯：`document.getElementById('pm25').textContent = data.pm25;`。

---

## 4. 總結

`lesson6_Teacher` 是一個結構完整且易於擴充的 IoT 樣板。它將前後端分離得宜：
*   **後端**專注於數據採集 (MQTT) 與儲存 (CSV)。
*   **前端**專注於即時呈現 (SocketIO + Chart.js)。

此架構非常適合作為學習或專題的基礎，您可以根據上述「手動修改的部分」輕鬆將其改造為符合您需求的監控系統。

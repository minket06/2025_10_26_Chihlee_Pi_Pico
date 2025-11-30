# 智慧家居監控儀表板 - 實作計劃

本專案將在 `lesson 6` 資料夾內建立一個基於 Streamlit 的 MQTT 訂閱監控系統,用於即時顯示智慧家居感測器資料(電燈狀態、溫濕度),並將資料儲存至 Excel 檔案。

## 用戶審核項目

> [!IMPORTANT]
> **MQTT Broker 設定確認**
> 
> 根據現有的 `mqtt_publish.py`,系統將使用以下設定:
> - Broker: `localhost` (Raspberry Pi 本機)
> - Port: `1883`
> - Topics: 需要確認實際的 topic 名稱
>   - 目前 `mqtt_publish.py` 使用 `客廳/topic`
>   - PRD 建議使用 `home/living_room/light`, `home/living_room/temperature`, `home/living_room/humidity`
> 
> **請確認**: 您希望使用哪種 topic 命名方式?或是需要我配合現有的 MQTT publisher 調整?

> [!WARNING]
> **資料來源說明**
> 
> 目前專案中沒有看到實際的溫濕度感測器發布程式。本實作將:
> 1. 建立一個模擬的 MQTT publisher 用於測試(發送模擬的溫濕度資料)
> 2. Streamlit 應用程式訂閱這些資料並顯示
> 
> 如果您已有實際的 Pico 感測器程式,請提供相關資訊以便整合。

---

## 擬議變更

### 核心模組

#### [NEW] [mqtt_subscriber.py](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson%206/mqtt_subscriber.py)

**MQTT 訂閱管理模組**
- 實作 `MQTTSubscriber` 類別,負責:
  - 連線到 MQTT Broker (localhost:1883)
  - 訂閱多個 topics (電燈、溫度、濕度)
  - 接收並解析訊息
  - 自動重連機制
  - 使用 callback 函數將資料傳遞給主程式
- QoS 設定為 1 (至少傳送一次)
- 執行緒安全的資料傳遞機制

#### [NEW] [data_storage.py](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson%206/data_storage.py)

**資料儲存管理模組**
- 實作 `DataStorage` 類別,負責:
  - Excel 檔案的建立與讀取
  - 資料追加寫入功能
  - 檔案命名: `sensor_data_YYYYMMDD.xlsx`
  - 資料欄位: timestamp, light_status, temperature, humidity
  - 使用 `openpyxl` 或 `pandas` 進行 Excel 操作
- 每日自動建立新檔案
- 執行緒安全的寫入機制

---

### Streamlit 應用程式

#### [MODIFY] [app.py](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson%206/app.py)

**主應用程式 - 完整重寫**

將建立完整的監控儀表板,包含:

1. **頁面配置**
   - 使用 `st.set_page_config()` 設定頁面標題與圖示
   - 寬螢幕模式以容納圖表

2. **標題區**
   - 顯示應用程式名稱: "🏠 智慧家居監控儀表板"
   - 顯示當前時間 (使用 `st.empty()` 實現即時更新)

3. **狀態卡片區** (使用 `st.columns()` 三欄佈局)
   - 電燈狀態卡片:
     - 顯示 ON/OFF 狀態
     - 使用 `st.metric()` 或自訂 HTML/CSS
     - 綠色 (開啟) / 灰色 (關閉) 視覺指示
   - 溫度卡片:
     - 顯示當前溫度值 (°C)
     - 使用大字體顯示
   - 濕度卡片:
     - 顯示當前濕度值 (%)
     - 使用大字體顯示

4. **圖表區**
   - 使用 `st.line_chart()` 或 `plotly` 繪製溫濕度趨勢圖
   - X 軸: 時間 (datetime)
   - Y 軸: 溫度/濕度數值
   - 支援雙 Y 軸顯示 (溫度與濕度分開刻度)
   - 顯示最近 N 筆資料 (如: 最近 100 筆)

5. **資料表區** (可選)
   - 使用 `st.dataframe()` 顯示最近的資料記錄
   - 可排序、可搜尋

6. **背景執行**
   - 整合 `mqtt_subscriber.py` 在背景執行緒訂閱資料
   - 使用 `st.session_state` 儲存即時資料
   - 使用 `st.rerun()` 或定時器更新介面

---

### 測試與輔助程式

#### [NEW] [mqtt_publisher_test.py](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson%206/mqtt_publisher_test.py)

**模擬資料發布程式**
- 用於測試的 MQTT publisher
- 定期發送模擬的溫濕度資料
- 隨機切換電燈狀態
- 資料格式符合 PRD 規範
- 可獨立執行用於測試

#### [NEW] [README.md](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson%206/README.md)

**專案說明文件**
- 專案簡介
- 系統需求
- 安裝步驟
- 使用方式
- MQTT 設定說明
- 故障排除

---

### 依賴套件

#### [MODIFY] [pyproject.toml](file:///home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/pyproject.toml)

需要新增以下套件:
- `openpyxl` - Excel 檔案操作
- `plotly` - 互動式圖表 (可選,若使用 Streamlit 內建圖表則不需要)

---

## 驗證計劃

### 自動化測試

#### 1. MQTT 連線測試
```bash
# 在 lesson 6 目錄執行
cd /home/pi/Documents/Github/2025_10_26_Chihlee_Pi_Pico/lesson\ 6

# 啟動測試 publisher (在背景執行)
uv run python mqtt_publisher_test.py &

# 等待 5 秒讓 publisher 開始運作
sleep 5

# 測試訂閱功能 (應該能接收到訊息)
uv run python -c "from mqtt_subscriber import MQTTSubscriber; import time; sub = MQTTSubscriber(); sub.connect(); time.sleep(10); sub.disconnect()"
```

**預期結果**: 應該能看到接收到的 MQTT 訊息輸出

#### 2. 資料儲存測試
```bash
# 測試 Excel 儲存功能
uv run python -c "from data_storage import DataStorage; import datetime; ds = DataStorage(); ds.save_data(datetime.datetime.now(), 'ON', 25.5, 60.2); print('測試完成,請檢查生成的 Excel 檔案')"

# 檢查是否生成 Excel 檔案
ls -lh sensor_data_*.xlsx
```

**預期結果**: 應該生成一個 Excel 檔案,包含測試資料

### 手動驗證

#### 3. Streamlit 應用程式整合測試

**步驟**:
1. 開啟終端機,進入 lesson 6 目錄
2. 啟動模擬 publisher:
   ```bash
   uv run python mqtt_publisher_test.py &
   ```
3. 啟動 Streamlit 應用程式:
   ```bash
   uv run streamlit run app.py
   ```
4. 在瀏覽器中開啟顯示的 URL (通常是 http://localhost:8501)

**驗證項目**:
- [ ] 頁面標題正確顯示
- [ ] 當前時間每秒更新
- [ ] 電燈狀態卡片顯示且會變化
- [ ] 溫度卡片顯示數值且會更新
- [ ] 濕度卡片顯示數值且會更新
- [ ] 圖表顯示溫濕度趨勢線
- [ ] 圖表 X 軸顯示時間,Y 軸顯示數值
- [ ] 資料表顯示最近的記錄
- [ ] Excel 檔案持續更新 (檢查檔案修改時間)

#### 4. 錯誤處理測試

**步驟**:
1. 在 Streamlit 運行時,停止 MQTT Broker:
   ```bash
   sudo systemctl stop mosquitto
   ```
2. 觀察應用程式是否顯示錯誤訊息或嘗試重連
3. 重新啟動 MQTT Broker:
   ```bash
   sudo systemctl start mosquitto
   ```
4. 確認應用程式自動恢復連線

**預期結果**: 應用程式應該優雅地處理斷線,並在 Broker 恢復後自動重連

---

## 實作順序

1. **第一階段**: 建立核心模組
   - `mqtt_subscriber.py`
   - `data_storage.py`
   - `mqtt_publisher_test.py`

2. **第二階段**: 建立 Streamlit 應用程式
   - 基本佈局與狀態卡片
   - 整合 MQTT 訂閱
   - 整合資料儲存

3. **第三階段**: 圖表與美化
   - 實作溫濕度趨勢圖
   - 美化介面設計
   - 新增資料表顯示

4. **第四階段**: 測試與文件
   - 執行所有驗證測試
   - 撰寫 README.md
   - 建立驗證文件

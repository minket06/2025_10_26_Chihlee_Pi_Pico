#!/usr/bin/env python3
"""
資料儲存管理模組
功能：將感測器資料儲存至 Excel 檔案
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import threading
from typing import Optional


class DataStorage:
    """資料儲存類別，負責將感測器資料儲存至 Excel"""
    
    def __init__(self, data_dir: str = "."):
        """
        初始化資料儲存
        
        Args:
            data_dir: 資料儲存目錄
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        
        # 資料欄位
        self.columns = ["timestamp", "light_status", "temperature", "humidity"]
    
    def _get_filename(self, date: Optional[datetime] = None) -> Path:
        """
        取得當日的檔案名稱
        
        Args:
            date: 日期，預設為今天
            
        Returns:
            檔案路徑
        """
        if date is None:
            date = datetime.now()
        
        filename = f"sensor_data_{date.strftime('%Y%m%d')}.xlsx"
        return self.data_dir / filename
    
    def save_data(
        self,
        timestamp: datetime,
        light_status: str,
        temperature: float,
        humidity: float
    ) -> bool:
        """
        儲存一筆感測器資料
        
        Args:
            timestamp: 時間戳記
            light_status: 電燈狀態
            temperature: 溫度
            humidity: 濕度
            
        Returns:
            是否成功儲存
        """
        try:
            with self.lock:
                filepath = self._get_filename(timestamp)
                
                # 建立新資料
                new_data = pd.DataFrame([{
                    "timestamp": timestamp,
                    "light_status": light_status,
                    "temperature": temperature,
                    "humidity": humidity
                }])
                
                # 如果檔案已存在，讀取並追加
                if filepath.exists():
                    existing_data = pd.read_excel(filepath)
                    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
                else:
                    combined_data = new_data
                
                # 儲存至 Excel
                combined_data.to_excel(filepath, index=False, engine='openpyxl')
                
                return True
                
        except Exception as e:
            print(f"❌ 儲存資料時發生錯誤: {e}")
            return False
    
    def load_data(self, date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
        """
        載入指定日期的資料
        
        Args:
            date: 日期，預設為今天
            
        Returns:
            資料 DataFrame，若檔案不存在則返回 None
        """
        try:
            filepath = self._get_filename(date)
            
            if not filepath.exists():
                return None
            
            return pd.read_excel(filepath, engine='openpyxl')
            
        except Exception as e:
            print(f"❌ 載入資料時發生錯誤: {e}")
            return None
    
    def get_recent_data(self, n: int = 100) -> Optional[pd.DataFrame]:
        """
        取得最近 N 筆資料
        
        Args:
            n: 資料筆數
            
        Returns:
            資料 DataFrame
        """
        try:
            # 載入今天的資料
            data = self.load_data()
            
            if data is None or len(data) == 0:
                return None
            
            # 取最後 N 筆
            return data.tail(n)
            
        except Exception as e:
            print(f"❌ 取得最近資料時發生錯誤: {e}")
            return None
    
    def get_all_files(self) -> list:
        """
        取得所有資料檔案
        
        Returns:
            檔案路徑列表
        """
        return sorted(self.data_dir.glob("sensor_data_*.xlsx"))


# 測試程式
if __name__ == "__main__":
    import time
    
    print("🧪 測試資料儲存模組\n")
    
    storage = DataStorage()
    
    # 測試儲存資料
    print("📝 儲存測試資料...")
    for i in range(5):
        timestamp = datetime.now()
        light_status = "ON" if i % 2 == 0 else "OFF"
        temperature = 20.0 + i * 0.5
        humidity = 55.0 + i * 2
        
        success = storage.save_data(timestamp, light_status, temperature, humidity)
        
        if success:
            print(f"✅ 已儲存第 {i+1} 筆資料: 溫度={temperature:.1f}°C, 濕度={humidity:.1f}%")
        else:
            print(f"❌ 儲存第 {i+1} 筆資料失敗")
        
        time.sleep(0.5)
    
    # 測試讀取資料
    print("\n📖 讀取今日資料...")
    data = storage.load_data()
    
    if data is not None:
        print(f"✅ 成功讀取 {len(data)} 筆資料")
        print("\n資料預覽:")
        print(data.to_string(index=False))
    else:
        print("❌ 沒有資料")
    
    # 顯示檔案列表
    print("\n📁 所有資料檔案:")
    files = storage.get_all_files()
    for f in files:
        print(f"  - {f.name}")
    
    print("\n✅ 測試完成！")

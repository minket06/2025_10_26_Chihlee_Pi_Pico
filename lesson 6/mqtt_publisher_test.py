#!/usr/bin/env python3
"""
MQTT 測試發布程式
功能：模擬智慧家居感測器，定期發送測試資料
"""

import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime


class SmartHomeSensorSimulator:
    """智慧家居感測器模擬器"""
    
    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        client_id: str = "sensor_simulator"
    ):
        """
        初始化模擬器
        
        Args:
            broker: MQTT Broker 位址
            port: MQTT Broker 埠號
            client_id: 客戶端 ID
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        
        # MQTT 主題
        self.topics = {
            "light": "home/living_room/light",
            "temperature": "home/living_room/temperature",
            "humidity": "home/living_room/humidity"
        }
        
        # 模擬資料
        self.light_status = "OFF"
        self.temperature = 25.0
        self.humidity = 60.0
        
        # MQTT 客戶端
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish
        
        self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """連線成功的回調函數"""
        if rc == 0:
            print(f"✅ 成功連接到 MQTT Broker: {self.broker}:{self.port}")
            self.connected = True
        else:
            print(f"❌ 連接失敗，錯誤代碼: {rc}")
            self.connected = False
    
    def _on_publish(self, client, userdata, mid):
        """發布成功的回調函數"""
        pass  # 不顯示每次發布的訊息，避免輸出過多
    
    def connect(self) -> bool:
        """連接到 MQTT Broker"""
        try:
            print(f"🔌 正在連接到 {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            # 等待連接完成
            timeout = 5
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """斷開連接"""
        print("\n🔌 正在斷開連接...")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def _update_light(self):
        """更新電燈狀態（隨機切換）"""
        # 10% 機率切換狀態
        if random.random() < 0.1:
            self.light_status = "OFF" if self.light_status == "ON" else "ON"
    
    def _update_temperature(self):
        """更新溫度（模擬自然變化）"""
        # 溫度在 20-30°C 之間隨機變化
        change = random.uniform(-0.5, 0.5)
        self.temperature += change
        self.temperature = max(20.0, min(30.0, self.temperature))
    
    def _update_humidity(self):
        """更新濕度（模擬自然變化）"""
        # 濕度在 40-80% 之間隨機變化
        change = random.uniform(-2.0, 2.0)
        self.humidity += change
        self.humidity = max(40.0, min(80.0, self.humidity))
    
    def publish_light_status(self):
        """發布電燈狀態"""
        data = {"status": self.light_status}
        payload = json.dumps(data)
        self.client.publish(self.topics["light"], payload, qos=1)
        print(f"💡 發布電燈狀態: {self.light_status}")
    
    def publish_temperature(self):
        """發布溫度"""
        data = {"value": round(self.temperature, 1)}
        payload = json.dumps(data)
        self.client.publish(self.topics["temperature"], payload, qos=1)
        print(f"🌡️  發布溫度: {self.temperature:.1f}°C")
    
    def publish_humidity(self):
        """發布濕度"""
        data = {"value": round(self.humidity, 1)}
        payload = json.dumps(data)
        self.client.publish(self.topics["humidity"], payload, qos=1)
        print(f"💧 發布濕度: {self.humidity:.1f}%")
    
    def run(self, interval: float = 2.0):
        """
        開始模擬發送資料
        
        Args:
            interval: 發送間隔（秒）
        """
        if not self.connected:
            print("❌ 未連接到 MQTT Broker")
            return
        
        print(f"\n🚀 開始模擬感測器資料發送（每 {interval} 秒）")
        print("按 Ctrl+C 停止\n")
        print("-" * 60)
        
        try:
            counter = 0
            while True:
                counter += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n[{timestamp}] 第 {counter} 次發送:")
                
                # 更新模擬資料
                self._update_light()
                self._update_temperature()
                self._update_humidity()
                
                # 發布資料
                self.publish_light_status()
                self.publish_temperature()
                self.publish_humidity()
                
                print("-" * 60)
                
                # 等待下次發送
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  停止發送...")


# 主程式
if __name__ == "__main__":
    print("🏠 智慧家居感測器模擬器")
    print("=" * 60)
    
    simulator = SmartHomeSensorSimulator()
    
    if simulator.connect():
        simulator.run(interval=2.0)
        simulator.disconnect()
    else:
        print("❌ 無法啟動模擬器")
    
    print("\n👋 再見！")

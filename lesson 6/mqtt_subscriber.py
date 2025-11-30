#!/usr/bin/env python3
"""
MQTT 訂閱管理模組
功能：訂閱 MQTT 主題並接收感測器資料
"""

import paho.mqtt.client as mqtt
import json
import threading
import time
from typing import Callable, Optional, Dict, Any
from datetime import datetime


class MQTTSubscriber:
    """MQTT 訂閱者類別，負責接收智慧家居感測器資料"""
    
    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        client_id: str = "streamlit_subscriber"
    ):
        """
        初始化 MQTT 訂閱者
        
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
        
        # 資料儲存
        self.latest_data = {
            "light_status": "OFF",
            "temperature": 0.0,
            "humidity": 0.0,
            "timestamp": None
        }
        
        # 回調函數
        self.data_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # MQTT 客戶端
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # 連線狀態
        self.connected = False
        self.lock = threading.Lock()
        
    def _on_connect(self, client, userdata, flags, rc):
        """連線成功的回調函數"""
        if rc == 0:
            print(f"✅ 成功連接到 MQTT Broker: {self.broker}:{self.port}")
            self.connected = True
            
            # 訂閱所有主題
            for topic_name, topic in self.topics.items():
                client.subscribe(topic, qos=1)
                print(f"📡 已訂閱主題: {topic}")
        else:
            print(f"❌ 連接失敗，錯誤代碼: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """斷線的回調函數"""
        print(f"⚠️  與 MQTT Broker 斷開連接 (rc: {rc})")
        self.connected = False
        
        if rc != 0:
            print("🔄 嘗試重新連接...")
    
    def _on_message(self, client, userdata, msg):
        """接收訊息的回調函數"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # 解析訊息
            with self.lock:
                timestamp = datetime.now()
                
                if topic == self.topics["light"]:
                    # 電燈狀態
                    try:
                        data = json.loads(payload)
                        self.latest_data["light_status"] = data.get("status", payload)
                    except json.JSONDecodeError:
                        self.latest_data["light_status"] = payload
                    
                    print(f"💡 電燈狀態: {self.latest_data['light_status']}")
                
                elif topic == self.topics["temperature"]:
                    # 溫度
                    try:
                        data = json.loads(payload)
                        self.latest_data["temperature"] = float(data.get("value", data.get("temperature", 0)))
                    except (json.JSONDecodeError, ValueError):
                        self.latest_data["temperature"] = float(payload)
                    
                    print(f"🌡️  溫度: {self.latest_data['temperature']:.1f}°C")
                
                elif topic == self.topics["humidity"]:
                    # 濕度
                    try:
                        data = json.loads(payload)
                        self.latest_data["humidity"] = float(data.get("value", data.get("humidity", 0)))
                    except (json.JSONDecodeError, ValueError):
                        self.latest_data["humidity"] = float(payload)
                    
                    print(f"💧 濕度: {self.latest_data['humidity']:.1f}%")
                
                self.latest_data["timestamp"] = timestamp
                
                # 呼叫回調函數
                if self.data_callback:
                    self.data_callback(self.latest_data.copy())
        
        except Exception as e:
            print(f"❌ 處理訊息時發生錯誤: {e}")
    
    def set_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        設定資料接收的回調函數
        
        Args:
            callback: 接收資料字典的函數
        """
        self.data_callback = callback
    
    def connect(self):
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
            
            if not self.connected:
                print("⚠️  連接超時")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """斷開與 MQTT Broker 的連接"""
        print("🔌 正在斷開連接...")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def get_latest_data(self) -> Dict[str, Any]:
        """
        取得最新的感測器資料
        
        Returns:
            包含最新資料的字典
        """
        with self.lock:
            return self.latest_data.copy()
    
    def is_connected(self) -> bool:
        """
        檢查是否已連接
        
        Returns:
            連接狀態
        """
        return self.connected


# 測試程式
if __name__ == "__main__":
    def on_data_received(data):
        print(f"\n📊 收到新資料: {data}\n")
    
    subscriber = MQTTSubscriber()
    subscriber.set_callback(on_data_received)
    
    if subscriber.connect():
        print("\n✅ 訂閱者已啟動，等待接收資料...")
        print("按 Ctrl+C 停止\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  停止訂閱...")
            subscriber.disconnect()
            print("👋 再見！")

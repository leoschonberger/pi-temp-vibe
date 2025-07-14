from datetime import datetime
from typing import Optional, Dict, Any

class TemperatureReading:
    def __init__(self, sensor_name: str, temperature: float, timestamp: Optional[datetime] = None):
        self.sensor_name = sensor_name
        self.temperature = temperature
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_name': self.sensor_name,
            'temperature': self.temperature,
            'timestamp': self.timestamp.isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemperatureReading':
        timestamp = datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
        return cls(
            sensor_name=data['sensor_name'],
            temperature=data['temperature'],
            timestamp=timestamp
        ) 
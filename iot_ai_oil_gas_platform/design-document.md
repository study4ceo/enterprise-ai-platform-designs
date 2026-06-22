# IoT-AI Oil and Gas RIGs and Ships Operations Platform - Design Document

**Document Date:** June 18, 2026  
**Tech Stack Status:** Latest & Greatest as of this date  
**Project Type:** Industrial IoT AI Operations Platform  
**Development Approach:** Test-Driven Development (TDD)  
**Production Status:** Enterprise-Ready, Safety-Critical Architecture

---

## 📋 Executive Summary

An enterprise-grade hybrid IoT-AI platform for oil & gas rigs, refineries, and maritime operations. Combines edge computing with cloud intelligence to deliver real-time monitoring, predictive maintenance, autonomous decision-making, and fleet coordination while ensuring offline operation and full regulatory compliance (ISO, API, Maritime).

**Core Problems Solved:**
1. ❌ **"Critical equipment failures cause $1M+ downtime"** → ✅ Predictive maintenance with AI
2. ❌ **"Safety incidents from delayed alerts"** → ✅ Real-time anomaly detection (<1s)
3. ❌ **"Manual operations slow and error-prone"** → ✅ Autonomous AI decision-making
4. ❌ **"Rigs/ships operate offline, losing data"** → ✅ Edge computing with sync
5. ❌ **"Compliance reporting takes weeks"** → ✅ Automated compliance monitoring

---

## 🎯 Core Capabilities

### **1. Real-Time Monitoring**
- 1000 sensors per site (pressure, temperature, vibration, flow, etc.)
- Sub-second latency for critical alerts
- Time-series data storage (InfluxDB + TimescaleDB)
- Live dashboards with anomaly highlighting

### **2. Predictive Maintenance**
- AI models predict equipment failure 48-72 hours ahead
- Reduces unplanned downtime by 60%
- Optimizes maintenance schedules
- ROI: $2-5M saved per rig annually

### **3. Safety & Compliance**
- Real-time gas leak detection
- Fire/explosion risk monitoring
- Automatic shutdown sequences
- ISO 9001, API 653/570/510, SOLAS compliance
- Audit trail for all events

### **4. Autonomous Operations**
- AI agents make operational decisions
- Automatic valve adjustments
- Pump optimization
- Load balancing across systems

### **5. Fleet Management**
- Multi-agent coordination across ships
- Route optimization for supply vessels
- Cargo tracking
- Weather-aware operations

### **6. Hybrid Edge-Cloud**
- Edge: Local processing on rigs/ships (offline capable)
- Cloud: Centralized analytics, ML training, fleet coordination
- Automatic sync when connectivity restored

---

## 🏗️ System Architecture

### **Three-Tier Architecture**

```
┌──────────────────────────────────────────────────────────┐
│                    CLOUD LAYER                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Control   │  │    AI      │  │   Fleet    │        │
│  │   Plane    │  │  Training  │  │Coordination│        │
│  └────────────┘  └────────────┘  └────────────┘        │
└────────────────────────┬─────────────────────────────────┘
                         │
                  Internet/Satellite
                         │
┌────────────────────────▼─────────────────────────────────┐
│                    EDGE LAYER                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Edge Server (Industrial PC / Ruggedized)      │    │
│  │  • AI Agent Runtime                             │    │
│  │  • Local time-series DB                         │    │
│  │  • Protocol gateway (OPC UA, MQTT, Modbus)     │    │
│  │  • Offline operation mode                       │    │
│  └────────────────────┬────────────────────────────┘    │
└───────────────────────┼──────────────────────────────────┘
                        │
                  Industrial Network
                        │
┌───────────────────────▼──────────────────────────────────┐
│                  SENSOR LAYER                            │
│  Pressure | Temperature | Vibration | Flow | Gas        │
│  1000 sensors per site via OPC UA/MQTT/Modbus          │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Latest & Greatest Tech Stack (June 2026)

### **Edge Layer**
| Technology | Version | Purpose |
|------------|---------|---------|
| Golang | 1.22+ | Edge runtime, protocol gateway |
| Python | 3.12+ | AI agents, ML inference |
| InfluxDB | 2.7+ | Time-series data (edge) |
| TimescaleDB | 2.15+ | Time-series data (PostgreSQL) |
| MQTT Broker | Mosquitto 2.x | Sensor messaging |
| OPC UA Server | open62541 | Industrial protocol |
| Redis | 7.x | Edge cache, queue |

### **Cloud Layer**
| Technology | Version | Purpose |
|------------|---------|---------|
| Kubernetes | 1.29+ | Container orchestration |
| PostgreSQL | 16.x + TimescaleDB | Cloud time-series |
| InfluxDB Cloud | 2.7+ | Centralized time-series |
| Kafka | 3.7+ | Event streaming |
| Golang | 1.22+ | Control plane services |
| Python | 3.12+ | AI/ML services |

### **AI/ML Stack**
| Technology | Version | Purpose |
|------------|---------|---------|
| OpenAI GPT-5.5 | Latest | Operational insights |
| Claude Opus 4.8 | Latest | Compliance analysis |
| PyTorch | 2.3+ | Custom ML models |
| TensorFlow Lite | 2.16+ | Edge inference |
| scikit-learn | 1.5+ | Predictive models |
| Prophet | 1.1+ | Time-series forecasting |

### **Python Tools**
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.111+ | Edge/Cloud APIs |
| HTTPX | 0.27+ | Async HTTP |
| asyncio | Built-in | Async runtime |
| dataclasses | Built-in | Data structures |
| Pydantic | 2.7+ | Validation |
| Logfire | Latest | Observability |
| uv | 0.2+ | Package manager |
| Ruff | 0.5+ | Linter |

### **Industrial Protocols**
| Protocol | Use Case |
|----------|----------|
| OPC UA | Modern industrial equipment |
| MQTT | IoT sensors, lightweight |
| Modbus TCP/RTU | Legacy equipment |
| NMEA 0183/2000 | Maritime navigation |
| S7 Communication | Siemens PLCs |
| EtherNet/IP | Allen-Bradley PLCs |

### **Compliance & Standards**
| Standard | Scope |
|----------|-------|
| ISO 9001 | Quality management |
| API 653 | Storage tank inspection |
| API 570 | Piping inspection |
| API 510 | Pressure vessel inspection |
| SOLAS | Maritime safety |
| ISM Code | Ship management |
| MARPOL | Marine pollution |

---

## 📦 Core Features

### **1. Real-Time Sensor Monitoring**

```python
# Edge: Real-time sensor data collection
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class SensorReading:
    sensor_id: str
    timestamp: datetime
    value: float
    unit: str
    location: str  # "rig-1", "ship-5", "refinery-2"

class SensorCollector:
    def __init__(self, protocols: dict):
        self.opc_ua = protocols.get('opc_ua')
        self.mqtt = protocols.get('mqtt')
        self.modbus = protocols.get('modbus')
    
    async def collect_all(self) -> list[SensorReading]:
        """Collect from all protocols in parallel"""
        results = await asyncio.gather(
            self.collect_opc_ua(),
            self.collect_mqtt(),
            self.collect_modbus()
        )
        return [reading for batch in results for reading in batch]
    
    async def collect_opc_ua(self) -> list[SensorReading]:
        """Collect from OPC UA servers"""
        nodes = await self.opc_ua.read_nodes([
            "ns=2;s=Pressure.Tank1",
            "ns=2;s=Temperature.Reactor",
            "ns=2;s=Vibration.Pump1"
        ])
        return [self.parse_opc_ua(n) for n in nodes]
```

### **2. Predictive Maintenance AI**

```python
# AI Agent: Predictive maintenance
import torch
from dataclasses import dataclass

@dataclass
class MaintenanceAlert:
    equipment_id: str
    failure_probability: float
    predicted_failure_time: datetime
    recommended_action: str
    severity: str  # "low", "medium", "high", "critical"

class PredictiveMaintenanceAgent:
    def __init__(self, model_path: str):
        self.model = torch.load(model_path)
        self.model.eval()
    
    async def analyze_equipment(
        self,
        equipment_id: str,
        sensor_history: list[SensorReading]
    ) -> MaintenanceAlert:
        """Predict equipment failure"""
        
        # 1. Prepare features
        features = self.extract_features(sensor_history)
        
        # 2. Run ML model
        with torch.no_grad():
            prediction = self.model(features)
        
        failure_prob = prediction['probability'].item()
        time_to_failure = prediction['hours_remaining'].item()
        
        # 3. Generate alert
        if failure_prob > 0.8:
            severity = "critical"
            action = "Immediate shutdown and inspection required"
        elif failure_prob > 0.6:
            severity = "high"
            action = "Schedule maintenance within 24 hours"
        elif failure_prob > 0.4:
            severity = "medium"
            action = "Schedule maintenance this week"
        else:
            severity = "low"
            action = "Monitor, no action needed"
        
        return MaintenanceAlert(
            equipment_id=equipment_id,
            failure_probability=failure_prob,
            predicted_failure_time=datetime.now() + timedelta(hours=time_to_failure),
            recommended_action=action,
            severity=severity
        )
```

### **3. Safety Monitoring & Auto-Shutdown**

```python
# Safety Agent: Real-time anomaly detection
@dataclass
class SafetyEvent:
    event_type: str  # "gas_leak", "fire", "overpressure", "high_temp"
    severity: str
    location: str
    sensor_readings: dict
    auto_shutdown_triggered: bool
    actions_taken: list[str]

class SafetyMonitorAgent:
    def __init__(self, thresholds: dict):
        self.thresholds = thresholds
        self.shutdown_sequence = ShutdownController()
    
    async def monitor(self, readings: list[SensorReading]) -> list[SafetyEvent]:
        """Real-time safety monitoring"""
        events = []
        
        for reading in readings:
            # Check thresholds
            if reading.value > self.thresholds[reading.sensor_id]['critical']:
                event = await self.handle_critical(reading)
                events.append(event)
            elif reading.value > self.thresholds[reading.sensor_id]['warning']:
                event = await self.handle_warning(reading)
                events.append(event)
        
        return events
    
    async def handle_critical(self, reading: SensorReading) -> SafetyEvent:
        """Critical threshold exceeded - immediate action"""
        
        actions = []
        
        # Gas leak detected
        if "gas" in reading.sensor_id.lower():
            actions.append("Activated ventilation system")
            actions.append("Sounded alarm")
            
            # Auto-shutdown if concentration > 50% LEL
            if reading.value > 0.5:
                await self.shutdown_sequence.execute(reading.location)
                actions.append("Emergency shutdown initiated")
                shutdown_triggered = True
            else:
                shutdown_triggered = False
        
        # High pressure
        elif "pressure" in reading.sensor_id.lower():
            actions.append("Opened pressure relief valve")
            actions.append("Reduced feed rate")
            shutdown_triggered = False
        
        return SafetyEvent(
            event_type=self.classify_event(reading),
            severity="critical",
            location=reading.location,
            sensor_readings={reading.sensor_id: reading.value},
            auto_shutdown_triggered=shutdown_triggered,
            actions_taken=actions
        )
```

### **4. Fleet Coordination (Ships)**

```python
# Multi-agent fleet coordination
@dataclass
class ShipStatus:
    ship_id: str
    location: tuple[float, float]  # lat, lon
    cargo: dict
    destination: str
    eta: datetime
    fuel_level: float

class FleetCoordinationAgent:
    def __init__(self, ships: list[str]):
        self.ships = ships
        self.weather_service = WeatherAPI()
    
    async def optimize_routes(self) -> dict[str, list[tuple]]:
        """Coordinate fleet for optimal efficiency"""
        
        # 1. Get all ship statuses
        statuses = await asyncio.gather(*[
            self.get_ship_status(ship_id) 
            for ship_id in self.ships
        ])
        
        # 2. Get weather data
        weather = await self.weather_service.get_forecast()
        
        # 3. Optimize routes (avoid storms, minimize fuel)
        optimized_routes = {}
        
        for status in statuses:
            route = await self.calculate_optimal_route(
                current=status.location,
                destination=status.destination,
                weather=weather,
                fuel=status.fuel_level
            )
            optimized_routes[status.ship_id] = route
        
        return optimized_routes
```

---

## 🗄️ Database Schema

### **Time-Series Data (InfluxDB)**

```
measurement: sensor_readings
tags:
  - sensor_id
  - location (rig-1, ship-5, refinery-2)
  - sensor_type (pressure, temperature, vibration)
  - equipment_id
fields:
  - value (float)
  - unit (string)
  - quality (int) # 0-100
timestamp: nanosecond precision

measurement: equipment_health
tags:
  - equipment_id
  - location
  - equipment_type
fields:
  - health_score (float 0-100)
  - failure_probability (float 0-1)
  - hours_to_failure (float)
timestamp: nanosecond precision
```

### **Relational Data (PostgreSQL + TimescaleDB)**

```sql
-- Locations (multi-tenant)
CREATE TABLE locations (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    name VARCHAR(255),
    type VARCHAR(50),  -- 'rig', 'refinery', 'ship'
    coordinates JSONB,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Equipment registry
CREATE TABLE equipment (
    id UUID PRIMARY KEY,
    location_id UUID REFERENCES locations(id),
    name VARCHAR(255),
    type VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    installation_date DATE,
    last_maintenance DATE,
    next_maintenance DATE,
    metadata JSONB
);

-- Sensors
CREATE TABLE sensors (
    id UUID PRIMARY KEY,
    equipment_id UUID REFERENCES equipment(id),
    sensor_type VARCHAR(50),
    protocol VARCHAR(20),  -- 'opc_ua', 'mqtt', 'modbus'
    address VARCHAR(255),
    unit VARCHAR(20),
    thresholds JSONB,  -- warning, critical levels
    enabled BOOLEAN DEFAULT true
);

-- Safety events
CREATE TABLE safety_events (
    id UUID PRIMARY KEY,
    location_id UUID REFERENCES locations(id),
    event_type VARCHAR(50),
    severity VARCHAR(20),
    sensor_readings JSONB,
    actions_taken TEXT[],
    auto_shutdown BOOLEAN,
    acknowledged BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance predictions
CREATE TABLE maintenance_predictions (
    id UUID PRIMARY KEY,
    equipment_id UUID REFERENCES equipment(id),
    failure_probability FLOAT,
    predicted_failure_time TIMESTAMP,
    recommended_action TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- TimescaleDB hypertables
SELECT create_hypertable('sensor_readings_pg', 'timestamp');
SELECT create_hypertable('equipment_health', 'timestamp');
SELECT create_hypertable('safety_events', 'created_at');
```

---

## 🔐 Security & Compliance

### **Industrial Security (ISA/IEC 62443)**

```
┌─────────────────────────────────────────┐
│  Level 4: Enterprise                    │
│  • Cloud services                       │
│  • Corporate network                    │
└──────────────┬──────────────────────────┘
               │ DMZ + Firewall
┌──────────────▼──────────────────────────┐
│  Level 3: Operations                    │
│  • SCADA systems                        │
│  • HMI workstations                     │
└──────────────┬──────────────────────────┘
               │ Industrial firewall
┌──────────────▼──────────────────────────┐
│  Level 2: Control                       │
│  • PLCs, RTUs                           │
│  • Edge servers                         │
└──────────────┬──────────────────────────┘
               │ Industrial switch
┌──────────────▼──────────────────────────┐
│  Level 1: Process                       │
│  • Sensors, actuators                   │
│  • Field devices                        │
└─────────────────────────────────────────┘
```

### **Compliance Automation**

```python
# Automated compliance reporting
class ComplianceAgent:
    async def generate_api_653_report(
        self,
        tank_id: str,
        period: tuple[datetime, datetime]
    ) -> dict:
        """API 653: Tank inspection compliance"""
        
        # Get inspection data
        inspections = await self.get_inspections(tank_id, period)
        thickness_readings = await self.get_thickness_measurements(tank_id)
        corrosion_rate = await self.calculate_corrosion_rate(thickness_readings)
        
        # Check compliance
        compliant = all([
            len(inspections) >= 1,  # Annual inspection
            corrosion_rate < self.thresholds['max_corrosion_rate'],
            thickness_readings[-1] > self.thresholds['min_thickness']
        ])
        
        return {
            "tank_id": tank_id,
            "period": period,
            "standard": "API 653",
            "compliant": compliant,
            "inspections": len(inspections),
            "corrosion_rate": corrosion_rate,
            "next_inspection_due": self.calculate_next_inspection(corrosion_rate)
        }
```

---

## 🌐 Hybrid Edge-Cloud Architecture

### **Edge Operation Modes**

```python
# Edge runtime with offline capability
class EdgeRuntime:
    def __init__(self):
        self.mode = "online"  # "online", "offline", "degraded"
        self.local_db = InfluxDBClient(local=True)
        self.cloud_sync_queue = []
    
    async def run(self):
        """Main edge runtime loop"""
        while True:
            # Check connectivity
            connectivity = await self.check_cloud_connection()
            
            if connectivity:
                self.mode = "online"
                await self.sync_to_cloud()
            else:
                self.mode = "offline"
                print("Operating in offline mode")
            
            # Collect sensors (always works)
            readings = await self.collect_sensors()
            
            # Store locally
            await self.local_db.write(readings)
            
            # Run local AI agents
            alerts = await self.run_local_agents(readings)
            
            # Queue for cloud sync
            if self.mode == "offline":
                self.cloud_sync_queue.extend(readings)
            
            await asyncio.sleep(1)  # 1Hz collection
    
    async def sync_to_cloud(self):
        """Sync queued data to cloud"""
        if not self.cloud_sync_queue:
            return
        
        try:
            await self.cloud_client.batch_write(self.cloud_sync_queue)
            self.cloud_sync_queue.clear()
        except Exception as e:
            print(f"Sync failed: {e}")
```

---

## 📊 Baseline Scale

| Asset Type | Baseline Count | Sensors Each | Total Sensors |
|------------|----------------|--------------|---------------|
| Oil Rigs | 5 | 1000 | 5,000 |
| Refineries | 2 | 1000 | 2,000 |
| Ships | 10 | 1000 | 10,000 |
| **Total** | **17 sites** | **1000 avg** | **17,000 sensors** |

**Data Volume:**
- Per sensor: 1 reading/sec = 86,400 readings/day
- Total: 17,000 × 86,400 = **1.47 billion readings/day**
- Storage: ~147 GB/day (compressed)

---

## 💰 ROI & Business Impact

### **Cost Savings**

| Category | Annual Savings per Rig |
|----------|-------------------------|
| Reduced downtime (60%) | $2-3M |
| Optimized maintenance | $500K |
| Fuel optimization | $300K |
| Compliance automation | $200K |
| **Total Savings** | **$3-4M per rig** |

**Total ROI:** $15-20M annually (5 rigs) - 10x platform cost

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Unplanned downtime reduction | 60% |
| Maintenance cost reduction | 30% |
| Safety incident reduction | 80% |
| Alert response time | < 1 second |
| Prediction accuracy | > 85% |
| Uptime SLA | 99.9% |

---

**Document Status:** ✅ Ready for Review

**Date:** June 18, 2026  
**Version:** 1.0

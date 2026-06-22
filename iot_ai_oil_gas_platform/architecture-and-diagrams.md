# IoT-AI Oil & Gas Platform - Architecture & System Diagrams

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Cloud Layer"
        CP[Control Plane<br/>Golang]
        AI_TRAIN[AI Training<br/>Python]
        FLEET[Fleet Coordination<br/>Multi-Agent]
        CLOUD_TS[(InfluxDB Cloud)]
        CLOUD_PG[(PostgreSQL<br/>TimescaleDB)]
    end
    
    subgraph "Internet/Satellite"
        CONN[Connectivity]
    end
    
    subgraph "Edge Layer - Rig"
        EDGE_RIG[Edge Server<br/>Industrial PC]
        LOCAL_TS_RIG[(InfluxDB Local)]
        AGENT_RIG[AI Agents<br/>Python]
    end
    
    subgraph "Edge Layer - Ship"
        EDGE_SHIP[Edge Server<br/>Ruggedized]
        LOCAL_TS_SHIP[(InfluxDB Local)]
        AGENT_SHIP[AI Agents<br/>Python]
    end
    
    subgraph "Sensor Layer - Rig"
        OPC_RIG[OPC UA Sensors<br/>1000 sensors]
        MODBUS_RIG[Modbus Sensors]
    end
    
    subgraph "Sensor Layer - Ship"
        NMEA[NMEA Navigation]
        MQTT_SHIP[MQTT Sensors]
    end
    
    CP <--> CONN
    AI_TRAIN <--> CONN
    FLEET <--> CONN
    
    CONN <--> EDGE_RIG
    CONN <--> EDGE_SHIP
    
    EDGE_RIG --> LOCAL_TS_RIG
    EDGE_RIG --> AGENT_RIG
    
    EDGE_SHIP --> LOCAL_TS_SHIP
    EDGE_SHIP --> AGENT_SHIP
    
    AGENT_RIG --> OPC_RIG
    AGENT_RIG --> MODBUS_RIG
    
    AGENT_SHIP --> NMEA
    AGENT_SHIP --> MQTT_SHIP
    
    EDGE_RIG -.Sync.-> CLOUD_TS
    EDGE_SHIP -.Sync.-> CLOUD_TS
    
    CP --> CLOUD_PG
```

---

## 2. Hybrid Edge-Cloud Data Flow

```mermaid
sequenceDiagram
    participant Sensors
    participant Edge
    participant LocalDB
    participant Agent
    participant Cloud
    
    loop Every Second
        Sensors->>Edge: Sensor readings (OPC UA/MQTT/Modbus)
        Edge->>Edge: Parse protocols
        Edge->>LocalDB: Store locally (InfluxDB)
        Edge->>Agent: Trigger analysis
        
        Agent->>Agent: Run ML inference
        
        alt Anomaly Detected
            Agent->>Agent: Generate alert
            Agent->>Edge: Trigger action
            Edge->>Sensors: Adjust valves/pumps
        end
        
        alt Online Mode
            Edge->>Cloud: Sync data
            Cloud-->>Edge: Updated ML models
        else Offline Mode
            Edge->>Edge: Queue for sync
            Note over Edge: Continue local operations
        end
    end
```

---

## 3. Predictive Maintenance Pipeline

```mermaid
flowchart TD
    START([Sensor Data Collection]) --> COLLECT[Collect Historical Data<br/>30 days]
    
    COLLECT --> FEATURES[Extract Features<br/>Mean, Std, Trends, FFT]
    
    FEATURES --> MODEL[ML Model<br/>Random Forest / LSTM]
    
    MODEL --> PREDICT{Failure<br/>Probability?}
    
    PREDICT -->|< 40%| NORMAL[Normal Operation<br/>Continue monitoring]
    PREDICT -->|40-60%| MEDIUM[Medium Risk<br/>Schedule maintenance]
    PREDICT -->|60-80%| HIGH[High Risk<br/>Maintenance within 24h]
    PREDICT -->|> 80%| CRITICAL[Critical Risk<br/>Immediate shutdown]
    
    CRITICAL --> SHUTDOWN[Auto-Shutdown Sequence]
    HIGH --> ALERT_HIGH[Alert: High Priority]
    MEDIUM --> ALERT_MED[Alert: Medium Priority]
    NORMAL --> LOG[Log to database]
    
    SHUTDOWN --> NOTIFY[Notify Operations Team]
    ALERT_HIGH --> NOTIFY
    ALERT_MED --> NOTIFY
```

---

## 4. Safety Monitoring Architecture

```mermaid
graph TB
    subgraph "Sensor Layer"
        GAS[Gas Detectors<br/>H2S, CH4, CO2]
        PRESSURE[Pressure Sensors]
        TEMP[Temperature Sensors]
        VIBRATION[Vibration Sensors]
        FIRE[Fire Detectors]
    end
    
    subgraph "Safety Agent"
        MONITOR[Real-Time Monitor<br/>< 100ms latency]
        THRESHOLD[Threshold Checker]
        CLASSIFIER[Event Classifier]
    end
    
    subgraph "Response System"
        AUTO[Auto-Shutdown<br/>Controller]
        ALARM[Alarm System]
        VENTILATION[Ventilation Control]
        SUPPRESSION[Fire Suppression]
    end
    
    GAS --> MONITOR
    PRESSURE --> MONITOR
    TEMP --> MONITOR
    VIBRATION --> MONITOR
    FIRE --> MONITOR
    
    MONITOR --> THRESHOLD
    THRESHOLD -->|Exceeded| CLASSIFIER
    
    CLASSIFIER -->|Gas Leak| AUTO
    CLASSIFIER -->|Gas Leak| ALARM
    CLASSIFIER -->|Gas Leak| VENTILATION
    
    CLASSIFIER -->|Fire| SUPPRESSION
    CLASSIFIER -->|Fire| AUTO
    
    CLASSIFIER -->|Overpressure| AUTO
    
    AUTO --> LOG[(Safety Event Log)]
```

---

## 5. Multi-Protocol Gateway

```mermaid
graph LR
    subgraph "Sensors"
        OPC[OPC UA Devices<br/>Modern equipment]
        MQTT_DEV[MQTT Devices<br/>IoT sensors]
        MODBUS[Modbus Devices<br/>Legacy PLCs]
        NMEA_DEV[NMEA Devices<br/>Ship navigation]
        S7[Siemens S7<br/>PLCs]
    end
    
    subgraph "Protocol Gateway (Golang)"
        OPC_HANDLER[OPC UA Handler]
        MQTT_HANDLER[MQTT Handler]
        MODBUS_HANDLER[Modbus Handler]
        NMEA_HANDLER[NMEA Handler]
        S7_HANDLER[S7 Handler]
        
        NORMALIZER[Data Normalizer]
    end
    
    subgraph "Unified Data Stream"
        STREAM[Standardized<br/>Sensor Stream]
    end
    
    OPC --> OPC_HANDLER
    MQTT_DEV --> MQTT_HANDLER
    MODBUS --> MODBUS_HANDLER
    NMEA_DEV --> NMEA_HANDLER
    S7 --> S7_HANDLER
    
    OPC_HANDLER --> NORMALIZER
    MQTT_HANDLER --> NORMALIZER
    MODBUS_HANDLER --> NORMALIZER
    NMEA_HANDLER --> NORMALIZER
    S7_HANDLER --> NORMALIZER
    
    NORMALIZER --> STREAM
```

---

## 6. Fleet Coordination (Ships)

```mermaid
graph TB
    subgraph "Cloud - Fleet Coordinator"
        FLEET_AGENT[Fleet Coordination Agent]
        WEATHER[Weather API]
        ROUTE_OPT[Route Optimizer]
    end
    
    subgraph "Ship 1"
        S1_EDGE[Edge Server]
        S1_GPS[GPS/NMEA]
        S1_FUEL[Fuel Sensors]
    end
    
    subgraph "Ship 2"
        S2_EDGE[Edge Server]
        S2_GPS[GPS/NMEA]
        S2_FUEL[Fuel Sensors]
    end
    
    subgraph "Ship 10"
        S10_EDGE[Edge Server]
        S10_GPS[GPS/NMEA]
        S10_FUEL[Fuel Sensors]
    end
    
    S1_GPS --> S1_EDGE
    S1_FUEL --> S1_EDGE
    S2_GPS --> S2_EDGE
    S2_FUEL --> S2_EDGE
    S10_GPS --> S10_EDGE
    S10_FUEL --> S10_EDGE
    
    S1_EDGE -->|Status| FLEET_AGENT
    S2_EDGE -->|Status| FLEET_AGENT
    S10_EDGE -->|Status| FLEET_AGENT
    
    WEATHER --> ROUTE_OPT
    FLEET_AGENT --> ROUTE_OPT
    
    ROUTE_OPT -->|Optimized routes| S1_EDGE
    ROUTE_OPT -->|Optimized routes| S2_EDGE
    ROUTE_OPT -->|Optimized routes| S10_EDGE
```

---

## 7. Edge Offline Operation

```mermaid
stateDiagram-v2
    [*] --> Online
    
    Online --> Offline: Connection Lost
    Online --> Online: Normal Operation
    
    Offline --> Online: Connection Restored
    Offline --> Offline: Continue Local
    
    state Online {
        [*] --> CollectSensors
        CollectSensors --> StoreLocal
        StoreLocal --> RunAgents
        RunAgents --> SyncCloud
        SyncCloud --> [*]
    }
    
    state Offline {
        [*] --> CollectSensors_Off
        CollectSensors_Off --> StoreLocal_Off
        StoreLocal_Off --> RunAgents_Off
        RunAgents_Off --> QueueSync
        QueueSync --> [*]
    }
    
    Online --> SyncQueue: On reconnect
    SyncQueue --> Online: Sync complete
```

---

## 8. Compliance Monitoring

```mermaid
graph TD
    subgraph "Data Collection"
        INSPECT[Inspection Records]
        THICKNESS[Thickness Measurements]
        PRESSURE_TEST[Pressure Tests]
        SAFETY_AUDIT[Safety Audits]
    end
    
    subgraph "Compliance Agent"
        API653[API 653 Checker<br/>Tank Inspection]
        API570[API 570 Checker<br/>Piping]
        API510[API 510 Checker<br/>Pressure Vessels]
        ISO9001[ISO 9001 Checker<br/>Quality]
        SOLAS[SOLAS Checker<br/>Maritime Safety]
    end
    
    subgraph "Reports"
        AUTO_REPORT[Automated Reports]
        ALERT_NONCOMPLIANT[Non-Compliance Alerts]
        NEXT_DUE[Next Inspection Schedule]
    end
    
    INSPECT --> API653
    INSPECT --> API570
    INSPECT --> API510
    
    THICKNESS --> API653
    PRESSURE_TEST --> API510
    SAFETY_AUDIT --> ISO9001
    SAFETY_AUDIT --> SOLAS
    
    API653 --> AUTO_REPORT
    API570 --> AUTO_REPORT
    API510 --> AUTO_REPORT
    ISO9001 --> AUTO_REPORT
    SOLAS --> AUTO_REPORT
    
    API653 -->|Non-compliant| ALERT_NONCOMPLIANT
    API570 -->|Non-compliant| ALERT_NONCOMPLIANT
    
    AUTO_REPORT --> NEXT_DUE
```

---

## 9. Data Architecture (Time-Series + Relational)

```mermaid
graph TB
    subgraph "Data Sources"
        SENSORS[17,000 Sensors<br/>1 reading/sec]
    end
    
    subgraph "Edge Storage"
        INFLUX_EDGE[(InfluxDB Edge<br/>Local time-series)]
    end
    
    subgraph "Cloud Storage"
        INFLUX_CLOUD[(InfluxDB Cloud<br/>Long-term time-series)]
        TIMESCALE[(TimescaleDB<br/>PostgreSQL + time-series)]
        PG[(PostgreSQL<br/>Relational data)]
    end
    
    subgraph "Analytics"
        GRAFANA[Grafana<br/>Dashboards]
        JUPYTER[Jupyter<br/>Data Science]
        BI[Power BI<br/>Business Intelligence]
    end
    
    SENSORS -->|1.47B readings/day| INFLUX_EDGE
    INFLUX_EDGE -.Sync.-> INFLUX_CLOUD
    INFLUX_EDGE -.Sync.-> TIMESCALE
    
    TIMESCALE --> PG
    
    INFLUX_CLOUD --> GRAFANA
    TIMESCALE --> GRAFANA
    PG --> BI
    
    INFLUX_CLOUD --> JUPYTER
    TIMESCALE --> JUPYTER
```

---

## 10. Security Architecture (ISA/IEC 62443)

```mermaid
graph TB
    subgraph "Level 4: Enterprise"
        CLOUD[Cloud Services]
        CORP[Corporate Network]
    end
    
    subgraph "DMZ"
        FW1[Firewall]
        VPN[VPN Gateway]
    end
    
    subgraph "Level 3: Operations"
        SCADA[SCADA System]
        HMI[HMI Workstations]
    end
    
    subgraph "Industrial Firewall"
        IFW[Industrial Firewall]
    end
    
    subgraph "Level 2: Control"
        EDGE[Edge Servers]
        PLC[PLCs / RTUs]
    end
    
    subgraph "Industrial Switch"
        ISWITCH[Managed Switch]
    end
    
    subgraph "Level 1: Process"
        SENSORS_SEC[Sensors]
        ACTUATORS[Actuators]
    end
    
    CLOUD <--> FW1
    CORP <--> FW1
    FW1 <--> VPN
    VPN <--> SCADA
    VPN <--> HMI
    
    SCADA <--> IFW
    HMI <--> IFW
    
    IFW <--> EDGE
    IFW <--> PLC
    
    EDGE <--> ISWITCH
    PLC <--> ISWITCH
    
    ISWITCH <--> SENSORS_SEC
    ISWITCH <--> ACTUATORS
```

---

## 11. Deployment Topology

```mermaid
graph TB
    subgraph "Cloud - AWS/GCP/Azure"
        K8S[Kubernetes Cluster]
        RDS[(RDS PostgreSQL)]
        CACHE[(ElastiCache Redis)]
        INFLUX_SVC[InfluxDB Cloud]
    end
    
    subgraph "Rig 1 - North Sea"
        R1_EDGE[Edge Server<br/>Industrial PC]
        R1_INFLUX[(InfluxDB)]
        R1_SENSORS[1000 Sensors]
    end
    
    subgraph "Rig 2 - Gulf of Mexico"
        R2_EDGE[Edge Server<br/>Industrial PC]
        R2_INFLUX[(InfluxDB)]
        R2_SENSORS[1000 Sensors]
    end
    
    subgraph "Refinery 1 - Texas"
        REF1_EDGE[Edge Server<br/>Ruggedized]
        REF1_INFLUX[(InfluxDB)]
        REF1_SENSORS[1000 Sensors]
    end
    
    subgraph "Ship Fleet - 10 vessels"
        S_EDGE[Edge Servers × 10]
        S_INFLUX[(InfluxDB × 10)]
        S_SENSORS[1000 Sensors each]
    end
    
    R1_SENSORS --> R1_EDGE
    R1_EDGE --> R1_INFLUX
    
    R2_SENSORS --> R2_EDGE
    R2_EDGE --> R2_INFLUX
    
    REF1_SENSORS --> REF1_EDGE
    REF1_EDGE --> REF1_INFLUX
    
    S_SENSORS --> S_EDGE
    S_EDGE --> S_INFLUX
    
    R1_EDGE -.Satellite/Internet.-> K8S
    R2_EDGE -.Satellite/Internet.-> K8S
    REF1_EDGE -.Internet.-> K8S
    S_EDGE -.Satellite.-> K8S
    
    K8S --> RDS
    K8S --> CACHE
    K8S --> INFLUX_SVC
```

---

## 12. CI/CD Pipeline

```mermaid
flowchart LR
    GIT[Git Push] --> BUILD[Build & Test<br/>Go + Python]
    
    BUILD --> TEST_EDGE[Edge Tests<br/>Unit + Integration]
    BUILD --> TEST_CLOUD[Cloud Tests<br/>Unit + Integration]
    
    TEST_EDGE --> DOCKER_EDGE[Build Edge Image]
    TEST_CLOUD --> DOCKER_CLOUD[Build Cloud Image]
    
    DOCKER_EDGE --> DEPLOY_EDGE[Deploy to Edge<br/>via Ansible]
    DOCKER_CLOUD --> DEPLOY_CLOUD[Deploy to Cloud<br/>Kubernetes]
    
    DEPLOY_EDGE --> VERIFY_EDGE[Health Check<br/>Edge Sites]
    DEPLOY_CLOUD --> VERIFY_CLOUD[Health Check<br/>Cloud Services]
    
    VERIFY_EDGE --> DONE[✓ Deployed]
    VERIFY_CLOUD --> DONE
```

---

**Status:** ✅ Complete - 12 Architecture Diagrams

**Version:** 1.0  
**Date:** June 18, 2026

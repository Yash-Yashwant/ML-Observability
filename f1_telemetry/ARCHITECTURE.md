# F1 Telemetry System Architecture

## System Design Overview

```
┌─────────────────┐
│  Static Data    │
│  (output.json)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Data Storage Layer                 │
│  ┌──────────┐  ┌─────────────────┐ │
│  │ TimeSeries│  │  Metadata DB    │ │
│  │   DB      │  │  (PostgreSQL)   │ │
│  │(TimescaleDB│  │                 │ │
│  │or InfluxDB)│  │  - Drivers      │ │
│  │           │  │  - Sessions     │ │
│  │- Position │  │  - Teams        │ │
│  │- Speed    │  └─────────────────┘ │
│  │- Telemetry│                      │
│  └──────────┘                       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Streaming Layer                    │
│  ┌──────────────────────────────┐  │
│  │  Replay Engine (In-Memory)   │  │
│  │  - Reads from DB              │  │
│  │  - Buffers 30s of data        │  │
│  │  - Emits events every 50ms    │  │
│  └──────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  API Layer (WebSocket/SSE)          │
│  - Real-time event streaming        │
│  - Playback controls (pause/seek)   │
│  - Multiple concurrent viewers      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Visualization Layer                │
│  - Web Dashboard                    │
│  - Track rendering                  │
│  - Telemetry charts                 │
└─────────────────────────────────────┘
```

## Data Storage Options

### Option 1: **TimescaleDB** (Recommended for Production)
**Best for: Time-series telemetry with SQL queries**

```yaml
Pros:
  - PostgreSQL extension (familiar SQL)
  - Excellent for time-series queries
  - Automatic data retention policies
  - Good compression (10x)
  - Supports continuous aggregates (pre-computed views)
  
Cons:
  - Requires PostgreSQL knowledge
  - More setup than SQLite
  
Use Case:
  - Multiple races/seasons
  - Complex analytical queries
  - Production deployment
```

### Option 2: **SQLite** (Recommended for POC/Development)
**Best for: Simple, file-based, zero-config**

```yaml
Pros:
  - Zero configuration
  - Single file database
  - Built into Python
  - Perfect for development
  - Easy to share/backup
  
Cons:
  - Limited concurrent writes
  - No built-in time-series optimization
  - Can get slow with millions of rows
  
Use Case:
  - Proof of concept
  - Single-user desktop app
  - Quick prototyping
```

### Option 3: **Parquet Files + DuckDB**
**Best for: Analytics-first, read-heavy workloads**

```yaml
Pros:
  - Columnar format (fast analytics)
  - No database server needed
  - Excellent compression
  - DuckDB = SQL queries on Parquet
  - Git-friendly (can version control small files)
  
Cons:
  - Not ideal for streaming writes
  - Best for batch processing
  
Use Case:
  - Post-race analysis
  - Research/ML model training
  - Sharing datasets
```

### Option 4: **InfluxDB**
**Best for: Pure time-series, high-frequency data**

```yaml
Pros:
  - Purpose-built for time-series
  - Very fast ingestion
  - Built-in downsampling
  - Great monitoring/alerting
  
Cons:
  - Learning curve (InfluxQL)
  - Overkill for static replay
  - More complex deployment
  
Use Case:
  - Live telemetry streaming
  - IoT-style data ingestion
  - Real-time monitoring
```

## Recommended Architecture for Your Use Case

### **Phase 1: POC (Start Here)**
```
output.json 
    ↓
Parse & Store in SQLite
    ↓
In-memory Replay Engine
    ↓
WebSocket API
    ↓
Web Dashboard
```

**Why SQLite:**
- Fast to implement
- No server setup
- Perfect for single race/session
- Easy to migrate later

### **Phase 2: Production**
```
output.json 
    ↓
Parse & Store in TimescaleDB
    ↓
Redis (for replay session state)
    ↓
FastAPI + WebSocket
    ↓
React Dashboard
```

**Why TimescaleDB:**
- Handle multiple races
- Complex queries (compare laps across seasons)
- Better performance at scale
- Production-ready

## Database Schema Design

### Schema for SQLite/TimescaleDB:

```sql
-- Metadata tables (small, relational)

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    year INTEGER,
    round INTEGER,
    session_type VARCHAR(50),  -- 'Race', 'Qualifying', 'Practice'
    circuit_name VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY,
    driver_number INTEGER,
    driver_name VARCHAR(100),
    team_name VARCHAR(100),
    team_color VARCHAR(6)  -- Hex color
);

-- Time-series tables (large, indexed by time)

CREATE TABLE telemetry (
    timestamp TIMESTAMPTZ NOT NULL,
    session_id UUID,
    driver_id INTEGER,
    
    -- Position
    position_x FLOAT,
    position_y FLOAT,
    
    -- Speed & motion
    speed INTEGER,  -- km/h
    throttle SMALLINT,  -- 0-100%
    brake BOOLEAN,
    gear SMALLINT,
    drs SMALLINT,  -- 0=off, 1=available, 2=active
    
    -- Status
    lap_number INTEGER,
    lap_distance FLOAT,  -- Distance into current lap (meters)
    
    PRIMARY KEY (timestamp, driver_id)
);

-- Index for fast time-range queries
CREATE INDEX idx_telemetry_time ON telemetry (timestamp, driver_id);
CREATE INDEX idx_telemetry_driver ON telemetry (driver_id, timestamp);

-- For TimescaleDB only: Convert to hypertable
-- SELECT create_hypertable('telemetry', 'timestamp');


CREATE TABLE lap_times (
    session_id UUID,
    driver_id INTEGER,
    lap_number INTEGER,
    lap_time FLOAT,  -- seconds
    sector_1_time FLOAT,
    sector_2_time FLOAT,
    sector_3_time FLOAT,
    compound VARCHAR(20),  -- Tire compound
    is_personal_best BOOLEAN,
    is_overall_best BOOLEAN,
    timestamp TIMESTAMPTZ,
    
    PRIMARY KEY (session_id, driver_id, lap_number)
);

CREATE TABLE tire_stints (
    session_id UUID,
    driver_id INTEGER,
    stint_number INTEGER,
    compound VARCHAR(20),
    is_new BOOLEAN,
    start_lap INTEGER,
    end_lap INTEGER,
    total_laps INTEGER,
    
    PRIMARY KEY (session_id, driver_id, stint_number)
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    session_id UUID,
    timestamp TIMESTAMPTZ,
    event_type VARCHAR(50),  -- 'PIT_STOP', 'CRASH', 'FLAG', etc.
    driver_id INTEGER,
    event_data JSONB  -- Flexible storage for event details
);
```

## Data Streaming Strategy

### **How to Stream Static Data:**

```python
# Pseudocode for streaming engine

class TelemetryStreamer:
    def __init__(self, db_connection, session_id):
        self.db = db_connection
        self.session_id = session_id
        
        # Load session time bounds
        self.start_time, self.end_time = self._get_session_bounds()
        
        # Current playback state
        self.current_time = self.start_time
        self.playback_speed = 1.0  # 1x, 2x, 4x, etc.
        self.is_playing = False
        
        # Buffer for smooth playback
        self.buffer = []
        self.buffer_duration = 30  # seconds
    
    def _fetch_buffer(self):
        """Pre-fetch next 30s of data from database"""
        query = """
            SELECT * FROM telemetry
            WHERE session_id = ? 
            AND timestamp >= ? 
            AND timestamp < ?
            ORDER BY timestamp
        """
        end_buffer_time = self.current_time + timedelta(seconds=self.buffer_duration)
        self.buffer = self.db.execute(query, 
                                      (self.session_id, 
                                       self.current_time, 
                                       end_buffer_time))
    
    def get_frame(self, frame_time: datetime) -> dict:
        """
        Get telemetry snapshot at specific time
        Returns all car positions at that moment
        """
        # Check if we need to refill buffer
        if not self.buffer or frame_time > self.buffer[-1]['timestamp']:
            self._fetch_buffer()
        
        # Find all telemetry points at this timestamp
        # (or interpolate between closest points)
        frame_data = self._interpolate_frame(frame_time)
        
        return {
            'timestamp': frame_time,
            'cars': frame_data
        }
    
    def stream_loop(self, frame_rate: int = 20):
        """
        Main streaming loop - emits frames at specified FPS
        """
        frame_interval = 1.0 / frame_rate  # 50ms for 20 FPS
        
        while self.is_playing and self.current_time < self.end_time:
            # Get frame
            frame = self.get_frame(self.current_time)
            
            # Emit to clients (WebSocket broadcast)
            yield frame
            
            # Advance time based on playback speed
            delta = timedelta(seconds=frame_interval * self.playback_speed)
            self.current_time += delta
            
            # Sleep to maintain frame rate (real-time playback)
            time.sleep(frame_interval)
    
    def seek(self, timestamp: datetime):
        """Jump to specific time"""
        self.current_time = timestamp
        self._fetch_buffer()
    
    def set_speed(self, speed: float):
        """Change playback speed"""
        self.playback_speed = speed
```

## Data Flow

### **Ingestion (One-Time):**
```
output.json → Parser → SQLite/TimescaleDB
```

### **Playback (Real-Time Streaming):**
```
User clicks "Play"
    ↓
Replay Engine fetches 30s buffer from DB
    ↓
Engine emits frame every 50ms
    ↓
WebSocket sends to client
    ↓
Dashboard renders frame
```

### **User Interactions:**
```
User clicks "Seek to lap 10"
    ↓
Engine calculates timestamp for lap 10
    ↓
Fetches new buffer from DB
    ↓
Resumes streaming from that point
```

## Storage Sizing Estimates

### Qualifying Session (1 hour):
```
- Telemetry points: ~20 drivers × 60 min × 60 sec × 10 Hz = 720,000 rows
- Storage (uncompressed): ~50 MB
- Storage (compressed): ~5-10 MB
```

### Race (2 hours):
```
- Telemetry points: ~20 drivers × 120 min × 60 sec × 10 Hz = 1,440,000 rows
- Storage (uncompressed): ~100 MB
- Storage (compressed): ~10-20 MB
```

### Full Season (24 races):
```
- Total storage: ~500 MB - 1 GB (compressed)
- Manageable in SQLite
- Ideal for TimescaleDB
```


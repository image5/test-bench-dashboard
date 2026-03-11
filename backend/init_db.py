"""
Database Initialization Script
Initialize database with sample data
"""

import sys
import os

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, SessionLocal
from app.models.laboratory import Laboratory
from app.models.bench import TestBench, BenchType, BenchStatus


def init_sample_data():
    """Initialize sample data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Laboratory).first():
            print("[INFO] Database already has data, skipping initialization")
            return
        
        print("[INFO] Initializing sample data...")
        
        # Create laboratories
        lab1 = Laboratory(
            id="lab-power-001",
            name="Power System Test Lab",
            description="Powertrain and motor test benches",
            width=1920,
            height=1080,
        )
        lab2 = Laboratory(
            id="lab-battery-001",
            name="Battery Test Lab",
            description="Battery system test benches",
            width=1920,
            height=1080,
        )
        db.add_all([lab1, lab2])
        db.commit()
        
        # Create sample benches
        sample_benches = [
            # Power Test Lab
            {
                "id": "bench-hil-001",
                "name": "HIL-001",
                "type": BenchType.HIL,
                "ip_address": "192.168.1.101",
                "port": 8080,
                "position_x": 100,
                "position_y": 100,
                "laboratory_id": lab1.id,
            },
            {
                "id": "bench-hil-002",
                "name": "HIL-002",
                "type": BenchType.HIL,
                "ip_address": "192.168.1.102",
                "port": 8080,
                "position_x": 350,
                "position_y": 100,
                "laboratory_id": lab1.id,
            },
            {
                "id": "bench-sys-001",
                "name": "SYS-001",
                "type": BenchType.SYSTEM,
                "ip_address": "192.168.1.201",
                "port": 8080,
                "position_x": 600,
                "position_y": 100,
                "laboratory_id": lab1.id,
            },
            {
                "id": "asm-001",
                "name": "ASM-001",
                "type": BenchType.ASSEMBLY,
                "ip_address": "192.168.1.301",
                "port": 8080,
                "position_x": 100,
                "position_y": 300,
                "laboratory_id": lab1.id,
            },
            {
                "id": "hw-001",
                "name": "HW-001",
                "type": BenchType.HARDWARE,
                "ip_address": "192.168.1.401",
                "port": 8080,
                "position_x": 350,
                "position_y": 300,
                "laboratory_id": lab1.id,
            },
            {
                "id": "sw-001",
                "name": "SW-001",
                "type": BenchType.SOFTWARE,
                "ip_address": "192.168.1.501",
                "port": 8080,
                "position_x": 600,
                "position_y": 300,
                "laboratory_id": lab1.id,
            },
            # Battery Test Lab
            {
                "id": "bat-hil-001",
                "name": "BAT-HIL-001",
                "type": BenchType.HIL,
                "ip_address": "192.168.2.101",
                "port": 8080,
                "position_x": 100,
                "position_y": 100,
                "laboratory_id": lab2.id,
            },
            {
                "id": "bat-sys-001",
                "name": "BAT-SYS-001",
                "type": BenchType.SYSTEM,
                "ip_address": "192.168.2.201",
                "port": 8080,
                "position_x": 350,
                "position_y": 100,
                "laboratory_id": lab2.id,
            },
        ]
        
        for bench_data in sample_benches:
            bench = TestBench(**bench_data, status=BenchStatus.OFFLINE)
            db.add(bench)
        
        db.commit()
        print(f"[OK] Created {len(sample_benches)} sample benches")
        print(f"[OK] Created 2 sample laboratories")
        
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    init_sample_data()
    print("\n[OK] Database initialization complete!")

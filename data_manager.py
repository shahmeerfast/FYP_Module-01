#!/usr/bin/env python3
"""
Data Manager for Large Scale Requirements Processing
===================================================

This module handles data management, storage, and retrieval for the requirements
engineering system. It supports multiple data formats and provides efficient
storage and querying capabilities.

Features:
- Multiple data format support (JSON, CSV, Parquet, SQLite)
- Data validation and cleaning
- Incremental processing
- Data versioning
- Query and filtering capabilities
"""

import os
import json
import sqlite3
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import hashlib
import pickle

@dataclass
class DataRecord:
    """Represents a single data record"""
    id: str
    content: str
    type: str  # 'text' or 'audio'
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    processed_data: Dict[str, Any] = None
    status: str = 'pending'  # 'pending', 'processing', 'completed', 'failed'
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
        if self.processed_data is None:
            self.processed_data = {}

class DataManager:
    """Manages data storage and retrieval for requirements processing"""
    
    def __init__(self, data_dir: str = "data", db_file: str = "requirements.db"):
        self.data_dir = Path(data_dir)
        self.db_file = self.data_dir / db_file
        self.logger = logging.getLogger(__name__)
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)
        (self.data_dir / "exports").mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for metadata storage"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Create main records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    type TEXT,
                    file_path TEXT,
                    metadata TEXT,
                    processed_data TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Create processing history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT,
                    processor_version TEXT,
                    status TEXT,
                    error_message TEXT,
                    processing_time REAL,
                    timestamp TEXT,
                    FOREIGN KEY (record_id) REFERENCES records (id)
                )
            ''')
            
            # Create batch processing table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_processing (
                    batch_id TEXT PRIMARY KEY,
                    total_records INTEGER,
                    successful_records INTEGER,
                    failed_records INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    status TEXT
                )
            ''')
            
            conn.commit()
    
    def add_record(self, record: DataRecord) -> str:
        """Add a new record to the database"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO records 
                (id, content, type, file_path, metadata, processed_data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.id,
                record.content,
                record.type,
                record.file_path,
                json.dumps(record.metadata),
                json.dumps(record.processed_data),
                record.status,
                record.created_at,
                record.updated_at
            ))
            
            conn.commit()
        
        self.logger.info(f"Added record {record.id}")
        return record.id
    
    def get_record(self, record_id: str) -> Optional[DataRecord]:
        """Retrieve a record by ID"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, type, file_path, metadata, processed_data, 
                       status, created_at, updated_at
                FROM records WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            if row:
                return DataRecord(
                    id=row[0],
                    content=row[1],
                    type=row[2],
                    file_path=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                    processed_data=json.loads(row[5]) if row[5] else {},
                    status=row[6],
                    created_at=row[7],
                    updated_at=row[8]
                )
        
        return None
    
    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update a record with new data"""
        record = self.get_record(record_id)
        if not record:
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        record.updated_at = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE records SET 
                content = ?, type = ?, file_path = ?, metadata = ?, 
                processed_data = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (
                record.content,
                record.type,
                record.file_path,
                json.dumps(record.metadata),
                json.dumps(record.processed_data),
                record.status,
                record.updated_at,
                record.id
            ))
            
            conn.commit()
        
        return True
    
    def list_records(self, status: str = None, record_type: str = None, 
                    limit: int = None, offset: int = 0) -> List[DataRecord]:
        """List records with optional filtering"""
        query = "SELECT id, content, type, file_path, metadata, processed_data, status, created_at, updated_at FROM records"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if record_type:
            conditions.append("type = ?")
            params.append(record_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            records = []
            for row in cursor.fetchall():
                records.append(DataRecord(
                    id=row[0],
                    content=row[1],
                    type=row[2],
                    file_path=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                    processed_data=json.loads(row[5]) if row[5] else {},
                    status=row[6],
                    created_at=row[7],
                    updated_at=row[8]
                ))
        
        return records
    
    def add_processing_history(self, record_id: str, processor_version: str, 
                             status: str, error_message: str = None, 
                             processing_time: float = None):
        """Add processing history entry"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_history 
                (record_id, processor_version, status, error_message, processing_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record_id,
                processor_version,
                status,
                error_message,
                processing_time,
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM records")
            total_records = cursor.fetchone()[0]
            
            # Status breakdown
            cursor.execute("SELECT status, COUNT(*) FROM records GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Type breakdown
            cursor.execute("SELECT type, COUNT(*) FROM records GROUP BY type")
            type_counts = dict(cursor.fetchall())
            
            # Recent processing
            cursor.execute('''
                SELECT COUNT(*) FROM processing_history 
                WHERE timestamp > datetime('now', '-24 hours')
            ''')
            recent_processing = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'status_breakdown': status_counts,
                'type_breakdown': type_counts,
                'recent_processing': recent_processing
            }
    
    def export_to_csv(self, output_file: str = None, status: str = None) -> str:
        """Export records to CSV file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.data_dir}/exports/records_{timestamp}.csv"
        
        records = self.list_records(status=status)
        
        # Convert to DataFrame
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'content': record.content,
                'type': record.type,
                'file_path': record.file_path,
                'status': record.status,
                'created_at': record.created_at,
                'updated_at': record.updated_at,
                'metadata': json.dumps(record.metadata),
                'processed_data': json.dumps(record.processed_data)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        
        self.logger.info(f"Exported {len(records)} records to {output_file}")
        return output_file
    
    def export_to_json(self, output_file: str = None, status: str = None) -> str:
        """Export records to JSON file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.data_dir}/exports/records_{timestamp}.json"
        
        records = self.list_records(status=status)
        
        # Convert to list of dictionaries
        data = [asdict(record) for record in records]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported {len(records)} records to {output_file}")
        return output_file
    
    def import_from_csv(self, csv_file: str) -> int:
        """Import records from CSV file"""
        df = pd.read_csv(csv_file)
        imported_count = 0
        
        for _, row in df.iterrows():
            try:
                record = DataRecord(
                    id=row['id'],
                    content=row['content'],
                    type=row['type'],
                    file_path=row.get('file_path'),
                    metadata=json.loads(row.get('metadata', '{}')),
                    processed_data=json.loads(row.get('processed_data', '{}')),
                    status=row.get('status', 'pending')
                )
                
                self.add_record(record)
                imported_count += 1
                
            except Exception as e:
                self.logger.error(f"Error importing record from CSV: {str(e)}")
        
        self.logger.info(f"Imported {imported_count} records from {csv_file}")
        return imported_count
    
    def import_from_directory(self, directory: str, file_patterns: List[str] = None) -> int:
        """Import all files from a directory"""
        if file_patterns is None:
            file_patterns = ['.txt', '.wav', '.mp3', '.m4a', '.flac']
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory {directory} not found")
        
        imported_count = 0
        
        for pattern in file_patterns:
            for file_path in directory_path.glob(f"**/*{pattern}"):
                try:
                    # Generate unique ID
                    file_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
                    
                    # Read content
                    if file_path.suffix.lower() in ['.wav', '.mp3', '.m4a', '.flac']:
                        content = f"Audio file: {file_path.name}"
                        record_type = 'audio'
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        record_type = 'text'
                    
                    record = DataRecord(
                        id=file_id,
                        content=content,
                        type=record_type,
                        file_path=str(file_path),
                        metadata={'source_file': str(file_path)},
                        status='pending'
                    )
                    
                    self.add_record(record)
                    imported_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error importing file {file_path}: {str(e)}")
        
        self.logger.info(f"Imported {imported_count} files from {directory}")
        return imported_count
    
    def cleanup_old_records(self, days_old: int = 30, status: str = 'failed') -> int:
        """Clean up old records with specified status"""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_old).isoformat()
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM records 
                WHERE status = ? AND created_at < ?
            ''', (status, cutoff_date))
            
            deleted_count = cursor.rowcount
            conn.commit()
        
        self.logger.info(f"Cleaned up {deleted_count} old {status} records")
        return deleted_count
    
    def get_batch_processing_queue(self, batch_size: int = 10) -> List[DataRecord]:
        """Get records ready for batch processing"""
        return self.list_records(status='pending', limit=batch_size)
    
    def mark_batch_completed(self, record_ids: List[str], status: str = 'completed'):
        """Mark a batch of records as completed"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in record_ids])
            cursor.execute(f'''
                UPDATE records 
                SET status = ?, updated_at = ?
                WHERE id IN ({placeholders})
            ''', [status, datetime.now().isoformat()] + record_ids)
            
            conn.commit()
        
        self.logger.info(f"Marked {len(record_ids)} records as {status}")

def main():
    """Test the data manager"""
    # Initialize data manager
    dm = DataManager()
    
    # Create sample records
    sample_records = [
        DataRecord(
            id="req_001",
            content="The system must provide real-time stock price updates",
            type="text",
            metadata={"priority": "high", "category": "functional"}
        ),
        DataRecord(
            id="req_002",
            content="Users should be able to create personalized watchlists",
            type="text",
            metadata={"priority": "medium", "category": "functional"}
        )
    ]
    
    # Add records
    for record in sample_records:
        dm.add_record(record)
    
    # List records
    records = dm.list_records()
    print(f"Total records: {len(records)}")
    
    # Get stats
    stats = dm.get_processing_stats()
    print(f"Processing stats: {stats}")
    
    # Export to CSV
    csv_file = dm.export_to_csv()
    print(f"Exported to: {csv_file}")

if __name__ == "__main__":
    main()

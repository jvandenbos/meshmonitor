"""SQLite database for persistent storage of messages and nodes."""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class MeshtasticDB:
    """SQLite database for Meshtastic data persistence."""
    
    def __init__(self, db_path: str = "meshtastic.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.local = threading.local()
        self._init_db()
        logger.info(f"Database initialized at {db_path}")
    
    def _get_conn(self):
        """Get thread-local database connection."""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Nodes table with timestamp tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                long_name TEXT,
                short_name TEXT,
                hw_model TEXT,
                role TEXT,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                battery_level INTEGER,
                voltage REAL,
                rssi INTEGER,
                snr REAL,
                hops INTEGER DEFAULT -1,
                is_direct BOOLEAN DEFAULT FALSE,
                distance_km REAL,
                position_updated_at TIMESTAMP,
                telemetry_updated_at TIMESTAMP,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                last_heard TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages table with full tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_node TEXT,
                to_node TEXT,
                channel INTEGER DEFAULT 0,
                port_num INTEGER,
                message_type TEXT,
                text TEXT,
                encrypted BOOLEAN DEFAULT FALSE,
                hop_count INTEGER,
                hop_limit INTEGER,
                rssi INTEGER,
                snr REAL,
                packet_id TEXT,
                want_ack BOOLEAN DEFAULT FALSE,
                via_mqtt BOOLEAN DEFAULT FALSE,
                delayed BOOLEAN DEFAULT FALSE,
                priority INTEGER,
                raw_data TEXT,
                received_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_node) REFERENCES nodes(id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_node)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_received ON messages(received_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_last_seen ON nodes(last_seen)')
        
        # Node history table for tracking changes over time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL,
                rssi INTEGER,
                snr REAL,
                battery_level INTEGER,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                hops INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES nodes(id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_node ON node_history(node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_time ON node_history(recorded_at)')
        
        conn.commit()
        logger.info("Database schema initialized")
    
    def save_node(self, node_data: Dict[str, Any]) -> bool:
        """Save or update node information."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            node_id = node_data.get('id')
            if not node_id:
                return False
            
            now = datetime.now().isoformat()
            
            # Check if node exists
            cursor.execute('SELECT id, first_seen FROM nodes WHERE id = ?', (node_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing node
                first_seen = existing['first_seen']
                cursor.execute('''
                    UPDATE nodes SET
                        long_name = ?,
                        short_name = ?,
                        hw_model = ?,
                        role = ?,
                        latitude = ?,
                        longitude = ?,
                        altitude = ?,
                        battery_level = ?,
                        voltage = ?,
                        rssi = ?,
                        snr = ?,
                        hops = ?,
                        is_direct = ?,
                        distance_km = ?,
                        position_updated_at = ?,
                        telemetry_updated_at = ?,
                        last_seen = ?,
                        last_heard = ?,
                        metadata = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    node_data.get('long_name'),
                    node_data.get('short_name'),
                    node_data.get('hw_model'),
                    node_data.get('role'),
                    node_data.get('latitude'),
                    node_data.get('longitude'),
                    node_data.get('altitude'),
                    node_data.get('battery_level'),
                    node_data.get('voltage'),
                    node_data.get('rssi'),
                    node_data.get('snr'),
                    node_data.get('hops', -1),
                    node_data.get('is_direct', False),
                    node_data.get('distance_km'),
                    node_data.get('position_updated_at'),
                    node_data.get('telemetry_updated_at'),
                    node_data.get('last_seen', now),
                    node_data.get('last_heard', now),
                    json.dumps(node_data.get('metadata', {}), default=str),
                    now,
                    node_id
                ))
            else:
                # Insert new node
                cursor.execute('''
                    INSERT INTO nodes (
                        id, long_name, short_name, hw_model, role,
                        latitude, longitude, altitude, battery_level, voltage,
                        rssi, snr, hops, is_direct, distance_km,
                        position_updated_at, telemetry_updated_at,
                        first_seen, last_seen, last_heard, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    node_id,
                    node_data.get('long_name'),
                    node_data.get('short_name'),
                    node_data.get('hw_model'),
                    node_data.get('role'),
                    node_data.get('latitude'),
                    node_data.get('longitude'),
                    node_data.get('altitude'),
                    node_data.get('battery_level'),
                    node_data.get('voltage'),
                    node_data.get('rssi'),
                    node_data.get('snr'),
                    node_data.get('hops', -1),
                    node_data.get('is_direct', False),
                    node_data.get('distance_km'),
                    node_data.get('position_updated_at'),
                    node_data.get('telemetry_updated_at'),
                    now,  # first_seen
                    node_data.get('last_seen', now),
                    node_data.get('last_heard', now),
                    json.dumps(node_data.get('metadata', {}), default=str)
                ))
            
            # Record history entry if we have metrics
            if any([node_data.get('rssi'), node_data.get('battery_level'), 
                   node_data.get('latitude'), node_data.get('hops') is not None]):
                cursor.execute('''
                    INSERT INTO node_history (
                        node_id, rssi, snr, battery_level,
                        latitude, longitude, altitude, hops
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    node_id,
                    node_data.get('rssi'),
                    node_data.get('snr'),
                    node_data.get('battery_level'),
                    node_data.get('latitude'),
                    node_data.get('longitude'),
                    node_data.get('altitude'),
                    node_data.get('hops')
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving node: {e}")
            return False
    
    def save_message(self, message_data: Dict[str, Any]) -> bool:
        """Save message to database."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (
                    from_node, to_node, channel, port_num, message_type,
                    text, encrypted, hop_count, hop_limit, rssi, snr,
                    packet_id, want_ack, via_mqtt, delayed, priority,
                    raw_data, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_data.get('from'),
                message_data.get('to'),
                message_data.get('channel', 0),
                message_data.get('port_num'),
                message_data.get('type'),
                message_data.get('text'),
                message_data.get('encrypted', False),
                message_data.get('hop_count'),
                message_data.get('hop_limit'),
                message_data.get('rssi'),
                message_data.get('snr'),
                message_data.get('packet_id'),
                message_data.get('want_ack', False),
                message_data.get('via_mqtt', False),
                message_data.get('delayed', False),
                message_data.get('priority'),
                json.dumps(message_data.get('raw', {}), default=str),
                message_data.get('timestamp', datetime.now().isoformat())
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def get_nodes(self, active_only: bool = False, 
                  max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """Get all nodes from database."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM nodes'
            params = []
            
            if active_only:
                cutoff = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
                query += ' WHERE last_seen > ?'
                params.append(cutoff)
            
            query += ' ORDER BY last_seen DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            nodes = []
            for row in rows:
                node = dict(row)
                if node.get('metadata'):
                    try:
                        node['metadata'] = json.loads(node['metadata'])
                    except:
                        node['metadata'] = {}
                nodes.append(node)
            
            return nodes
            
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return []
    
    def get_messages(self, limit: int = 100, 
                    message_type: Optional[str] = None,
                    from_node: Optional[str] = None,
                    since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get messages from database with filters."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM messages WHERE 1=1'
            params = []
            
            if message_type:
                query += ' AND message_type = ?'
                params.append(message_type)
            
            if from_node:
                query += ' AND from_node = ?'
                params.append(from_node)
            
            if since:
                query += ' AND received_at > ?'
                params.append(since.isoformat())
            
            query += ' ORDER BY received_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                msg = dict(row)
                if msg.get('raw_data'):
                    try:
                        msg['raw'] = json.loads(msg['raw_data'])
                    except:
                        msg['raw'] = {}
                messages.append(msg)
            
            # Return in chronological order for display
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    def get_node_history(self, node_id: str, 
                        hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a node."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT * FROM node_history 
                WHERE node_id = ? AND recorded_at > ?
                ORDER BY recorded_at DESC
            ''', (node_id, cutoff))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting node history: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30) -> tuple[int, int]:
        """Remove old messages and history older than specified days."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Delete old messages
            cursor.execute('DELETE FROM messages WHERE received_at < ?', (cutoff,))
            messages_deleted = cursor.rowcount
            
            # Delete old history
            cursor.execute('DELETE FROM node_history WHERE recorded_at < ?', (cutoff,))
            history_deleted = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Cleaned up {messages_deleted} messages and {history_deleted} history entries")
            return messages_deleted, history_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0, 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Total nodes
            cursor.execute('SELECT COUNT(*) as count FROM nodes')
            total_nodes = cursor.fetchone()['count']
            
            # Active nodes (seen in last 24 hours)
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute('SELECT COUNT(*) as count FROM nodes WHERE last_seen > ?', (cutoff,))
            active_nodes = cursor.fetchone()['count']
            
            # Total messages
            cursor.execute('SELECT COUNT(*) as count FROM messages')
            total_messages = cursor.fetchone()['count']
            
            # Messages by type
            cursor.execute('''
                SELECT message_type, COUNT(*) as count 
                FROM messages 
                GROUP BY message_type
            ''')
            message_types = {row['message_type']: row['count'] for row in cursor.fetchall()}
            
            # Database file size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            return {
                'total_nodes': total_nodes,
                'active_nodes': active_nodes,
                'total_messages': total_messages,
                'message_types': message_types,
                'database_size_mb': round(db_size / 1024 / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
            delattr(self.local, 'conn')

# Global database instance
db = MeshtasticDB()
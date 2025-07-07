"""
Memory system for WebSurfer-β v2.0

This module provides persistent memory capabilities for learning
successful selectors and website patterns.
"""

import asyncio
import logging
import sqlite3
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class Memory:
    """
    Persistent memory system for WebSurfer-β agent.
    
    This class manages a SQLite database to store:
    - Successful selectors for specific websites and actions
    - Website patterns and navigation knowledge
    - Performance metrics and success rates
    """
    
    def __init__(self, db_path: str = "websurfer_memory.db"):
        self.db_path = db_path
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the memory database and create tables.
        
        Returns:
            bool: True if successfully initialized, False otherwise
        """
        try:
            # Create database directory if it doesn't exist
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS known_selectors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website_domain TEXT NOT NULL,
                        action_description TEXT NOT NULL,
                        successful_selector TEXT NOT NULL,
                        success_count INTEGER DEFAULT 1,
                        last_used_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(website_domain, action_description, successful_selector)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS website_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website_domain TEXT NOT NULL,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        confidence_score REAL DEFAULT 1.0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(website_domain, pattern_type)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS action_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website_domain TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        action_description TEXT NOT NULL,
                        selector_used TEXT,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        execution_time REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_known_selectors_domain 
                    ON known_selectors(website_domain)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_known_selectors_description 
                    ON known_selectors(action_description)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_action_history_domain 
                    ON action_history(website_domain)
                """)
                
                await db.commit()
                
            self.initialized = True
            logger.info(f"✅ Memory system initialized: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory system: {e}")
            return False
    
    async def add_successful_selector(
        self, 
        domain: str, 
        description: str, 
        selector: str
    ) -> bool:
        """
        Add or update a successful selector in the database.
        
        Args:
            domain (str): Website domain (e.g., "google.com")
            description (str): Natural language description of the element
            selector (str): The CSS selector that worked
            
        Returns:
            bool: True if successfully added/updated, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if selector already exists
                cursor = await db.execute("""
                    SELECT id, success_count FROM known_selectors
                    WHERE website_domain = ? AND action_description = ? AND successful_selector = ?
                """, (domain, description, selector))
                
                row = await cursor.fetchone()
                
                if row:
                    # Update existing record
                    await db.execute("""
                        UPDATE known_selectors 
                        SET success_count = success_count + 1, 
                            last_used_timestamp = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (row[0],))
                    logger.debug(f"📝 Updated selector success count for {domain}: {description}")
                else:
                    # Insert new record
                    await db.execute("""
                        INSERT INTO known_selectors 
                        (website_domain, action_description, successful_selector)
                        VALUES (?, ?, ?)
                    """, (domain, description, selector))
                    logger.info(f"💾 Saved new successful selector for {domain}: {description}")
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save successful selector: {e}")
            return False
    
    async def get_known_selector(
        self, 
        domain: str, 
        description: str
    ) -> Optional[str]:
        """
        Get the most successful selector for a domain and description.
        
        Args:
            domain (str): Website domain
            description (str): Natural language description of the element
            
        Returns:
            Optional[str]: The best known selector, or None if not found
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT successful_selector, success_count, last_used_timestamp
                    FROM known_selectors
                    WHERE website_domain = ? AND action_description = ?
                    ORDER BY success_count DESC, last_used_timestamp DESC
                    LIMIT 1
                """, (domain, description))
                
                row = await cursor.fetchone()
                
                if row:
                    logger.debug(f"🎯 Found known selector for {domain}: {description}")
                    return row[0]
                else:
                    logger.debug(f"🔍 No known selector for {domain}: {description}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to get known selector: {e}")
            return None
    
    async def get_similar_selectors(
        self, 
        domain: str, 
        description: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar selectors for a domain based on description similarity.
        
        Args:
            domain (str): Website domain
            description (str): Natural language description
            limit (int): Maximum number of selectors to return
            
        Returns:
            List[Dict[str, Any]]: List of similar selectors with metadata
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Simple similarity search based on common words
                words = description.lower().split()
                
                selectors = []
                for word in words:
                    cursor = await db.execute("""
                        SELECT successful_selector, action_description, success_count
                        FROM known_selectors
                        WHERE website_domain = ? AND action_description LIKE ?
                        ORDER BY success_count DESC
                        LIMIT ?
                    """, (domain, f"%{word}%", limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        selector_info = {
                            'selector': row[0],
                            'description': row[1],
                            'success_count': row[2]
                        }
                        if selector_info not in selectors:
                            selectors.append(selector_info)
                
                # Sort by success count and limit
                selectors.sort(key=lambda x: x['success_count'], reverse=True)
                return selectors[:limit]
                
        except Exception as e:
            logger.error(f"❌ Failed to get similar selectors: {e}")
            return []
    
    async def record_action_history(
        self,
        domain: str,
        action_type: str,
        action_description: str,
        selector_used: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> bool:
        """
        Record an action in the history for analytics.
        
        Args:
            domain (str): Website domain
            action_type (str): Type of action (click, type, navigate, etc.)
            action_description (str): Description of the action
            selector_used (str, optional): Selector that was used
            success (bool): Whether the action succeeded
            error_message (str, optional): Error message if failed
            execution_time (float, optional): Time taken to execute
            
        Returns:
            bool: True if successfully recorded, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO action_history 
                    (website_domain, action_type, action_description, selector_used, 
                     success, error_message, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (domain, action_type, action_description, selector_used, 
                      success, error_message, execution_time))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to record action history: {e}")
            return False
    
    async def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """
        Get statistics for a specific domain.
        
        Args:
            domain (str): Website domain
            
        Returns:
            Dict[str, Any]: Statistics for the domain
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get selector count
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM known_selectors WHERE website_domain = ?
                """, (domain,))
                selector_count = (await cursor.fetchone())[0]
                
                # Get success rate
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total_actions,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_actions
                    FROM action_history 
                    WHERE website_domain = ?
                """, (domain,))
                
                stats_row = await cursor.fetchone()
                total_actions = stats_row[0] if stats_row[0] else 0
                successful_actions = stats_row[1] if stats_row[1] else 0
                
                success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
                
                # Get most recent activity
                cursor = await db.execute("""
                    SELECT MAX(timestamp) FROM action_history WHERE website_domain = ?
                """, (domain,))
                last_activity = (await cursor.fetchone())[0]
                
                return {
                    'domain': domain,
                    'known_selectors': selector_count,
                    'total_actions': total_actions,
                    'successful_actions': successful_actions,
                    'success_rate': round(success_rate, 2),
                    'last_activity': last_activity
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get domain stats: {e}")
            return {}
    
    async def get_top_domains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently used domains.
        
        Args:
            limit (int): Number of domains to return
            
        Returns:
            List[Dict[str, Any]]: List of top domains with stats
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 
                        website_domain,
                        COUNT(*) as action_count,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_actions,
                        MAX(timestamp) as last_activity
                    FROM action_history
                    GROUP BY website_domain
                    ORDER BY action_count DESC
                    LIMIT ?
                """, (limit,))
                
                domains = []
                async for row in cursor:
                    domain_info = {
                        'domain': row[0],
                        'action_count': row[1],
                        'successful_actions': row[2],
                        'success_rate': round((row[2] / row[1] * 100), 2) if row[1] > 0 else 0,
                        'last_activity': row[3]
                    }
                    domains.append(domain_info)
                
                return domains
                
        except Exception as e:
            logger.error(f"❌ Failed to get top domains: {e}")
            return []
    
    async def cleanup_old_data(self, days_old: int = 30) -> bool:
        """
        Clean up old action history data.
        
        Args:
            days_old (int): Remove data older than this many days
            
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM action_history 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days_old))
                
                await db.commit()
                logger.info(f"🧹 Cleaned up action history older than {days_old} days")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")
            return False
    
    async def export_knowledge(self, export_path: str) -> bool:
        """
        Export knowledge base to JSON file.
        
        Args:
            export_path (str): Path to export the knowledge base
            
        Returns:
            bool: True if export successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            import json
            
            async with aiosqlite.connect(self.db_path) as db:
                # Export known selectors
                cursor = await db.execute("""
                    SELECT * FROM known_selectors
                """)
                
                selectors = []
                async for row in cursor:
                    selectors.append({
                        'id': row[0],
                        'website_domain': row[1],
                        'action_description': row[2],
                        'successful_selector': row[3],
                        'success_count': row[4],
                        'last_used_timestamp': row[5],
                        'created_timestamp': row[6]
                    })
                
                export_data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'known_selectors': selectors,
                    'total_selectors': len(selectors)
                }
                
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                logger.info(f"📤 Exported knowledge base to {export_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to export knowledge: {e}")
            return False
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get overall memory system statistics.
        
        Returns:
            Dict[str, Any]: Memory system statistics
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get total selectors
                cursor = await db.execute("SELECT COUNT(*) FROM known_selectors")
                total_selectors = (await cursor.fetchone())[0]
                
                # Get total domains
                cursor = await db.execute("SELECT COUNT(DISTINCT website_domain) FROM known_selectors")
                total_domains = (await cursor.fetchone())[0]
                
                # Get total actions
                cursor = await db.execute("SELECT COUNT(*) FROM action_history")
                total_actions = (await cursor.fetchone())[0]
                
                # Get overall success rate
                cursor = await db.execute("""
                    SELECT 
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_actions
                    FROM action_history
                """)
                successful_actions = (await cursor.fetchone())[0] or 0
                
                success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
                
                return {
                    'total_selectors': total_selectors,
                    'total_domains': total_domains,
                    'total_actions': total_actions,
                    'successful_actions': successful_actions,
                    'overall_success_rate': round(success_rate, 2),
                    'database_path': self.db_path
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get memory stats: {e}")
            return {}
    
    async def close(self) -> None:
        """Close the memory system."""
        # SQLite connections are automatically closed when using async with
        logger.info("🔚 Memory system closed")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 
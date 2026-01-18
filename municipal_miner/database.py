"""Database operations using sqlite-utils."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from sqlite_utils import Database
from loguru import logger


class MunicipalDatabase:
    """Manages the SQLite database for documents and signals."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db = Database(str(self.db_path))
        self._ensure_schema()

    def _ensure_schema(self):
        """Create tables if they don't exist."""

        # Documents table
        if "documents" not in self.db.table_names():
            self.db["documents"].create({
                "id": int,
                "filename": str,
                "file_path": str,
                "file_hash": str,
                "municipality_name": str,
                "state": str,
                "meeting_date": str,
                "meeting_type": str,
                "raw_text": str,
                "page_count": int,
                "processed": bool,
                "created_at": str,
            }, pk="id")

            # Add indexes
            self.db["documents"].create_index(["file_hash"], unique=True, if_not_exists=True)
            self.db["documents"].create_index(["municipality_name"], if_not_exists=True)
            self.db["documents"].create_index(["meeting_date"], if_not_exists=True)

        # Signals table
        if "signals" not in self.db.table_names():
            self.db["signals"].create({
                "id": int,
                "document_id": int,
                "municipality_name": str,
                "state": str,
                "meeting_date": str,
                "vertical": str,
                "signal_type": str,
                "specific_quote": str,
                "context": str,
                "contact_person": str,
                "estimated_value": str,
                "urgency": str,
                "next_action": str,
                "confidence_score": float,
                "raw_llm_response": str,
                "created_at": str,
            }, pk="id", foreign_keys=[("document_id", "documents", "id")])

            # Add indexes
            self.db["signals"].create_index(["vertical"], if_not_exists=True)
            self.db["signals"].create_index(["signal_type"], if_not_exists=True)
            self.db["signals"].create_index(["confidence_score"], if_not_exists=True)
            self.db["signals"].create_index(["municipality_name"], if_not_exists=True)

        logger.info(f"Database initialized at {self.db_path}")

    def document_exists(self, file_hash: str) -> bool:
        """Check if document already exists by hash."""
        return bool(list(self.db["documents"].rows_where("file_hash = ?", [file_hash])))

    def insert_document(self, document_data: Dict[str, Any]) -> int:
        """Insert a new document and return its ID."""
        document_data["created_at"] = datetime.utcnow().isoformat()
        document_data["processed"] = False

        result = self.db["documents"].insert(document_data)
        doc_id = result.last_pk
        logger.info(f"Inserted document: {document_data['filename']} (ID: {doc_id})")
        return doc_id

    def insert_signals(self, document_id: int, signals_data: List[Dict[str, Any]]):
        """Insert multiple signals for a document."""
        for signal in signals_data:
            signal["document_id"] = document_id
            signal["created_at"] = datetime.utcnow().isoformat()
            self.db["signals"].insert(signal)

        logger.info(f"Inserted {len(signals_data)} signals for document {document_id}")

    def mark_document_processed(self, document_id: int):
        """Mark a document as processed."""
        self.db["documents"].update(document_id, {"processed": True})

    def get_signals(self, vertical: Optional[str] = None, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Retrieve signals with optional filtering."""
        query = "SELECT * FROM signals WHERE confidence_score >= ?"
        params = [min_confidence]

        if vertical:
            query += " AND vertical = ?"
            params.append(vertical)

        query += " ORDER BY confidence_score DESC, meeting_date DESC"

        return list(self.db.execute(query, params).fetchall())

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        total_docs = self.db["documents"].count
        processed_docs = self.db.execute("SELECT COUNT(*) FROM documents WHERE processed = 1").fetchone()[0]
        total_signals = self.db["signals"].count

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "total_signals": total_signals,
        }

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

"""JSON file storage for large content blobs."""
import json
from pathlib import Path
from typing import Any, Dict, Optional
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class JSONStore:
    """JSON file storage manager."""

    def __init__(self, base_path: str):
        """
        Initialize JSON store.

        Args:
            base_path: Base directory for JSON storage
        """
        self.base_path = Path(base_path)
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """Ensure base directory exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_analysis_dir(self, analysis_id: str) -> Path:
        """
        Get directory for a specific analysis.

        Args:
            analysis_id: Analysis ID

        Returns:
            Path to analysis directory
        """
        analysis_dir = self.base_path / analysis_id
        analysis_dir.mkdir(parents=True, exist_ok=True)
        return analysis_dir

    def save_raw_content(self, analysis_id: str, filename: str, content: str):
        """
        Save raw HTML content.

        Args:
            analysis_id: Analysis ID
            filename: File name (e.g., 'homepage.html')
            content: HTML content
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        raw_dir = analysis_dir / "raw_content"
        raw_dir.mkdir(exist_ok=True)

        file_path = raw_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Saved raw content", extra={
            "analysis_id": analysis_id,
            "file_name": filename,
            "size": len(content)
        })

    def load_raw_content(self, analysis_id: str, filename: str) -> Optional[str]:
        """
        Load raw HTML content.

        Args:
            analysis_id: Analysis ID
            filename: File name

        Returns:
            HTML content or None if not found
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        file_path = analysis_dir / "raw_content" / filename

        if not file_path.exists():
            return None

        return file_path.read_text(encoding="utf-8")

    def save_parsed_data(self, analysis_id: str, data_type: str, data: Dict[str, Any]):
        """
        Save parsed data as JSON.

        Args:
            analysis_id: Analysis ID
            data_type: Type of data (e.g., 'schema_data', 'content_metrics')
            data: Data to save
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        parsed_dir = analysis_dir / "parsed_content"
        parsed_dir.mkdir(exist_ok=True)

        file_path = parsed_dir / f"{data_type}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved parsed data", extra={
            "analysis_id": analysis_id,
            "data_type": data_type
        })

    def load_parsed_data(self, analysis_id: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Load parsed data from JSON.

        Args:
            analysis_id: Analysis ID
            data_type: Type of data

        Returns:
            Parsed data or None if not found
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        file_path = analysis_dir / "parsed_content" / f"{data_type}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_simulation_data(self, analysis_id: str, simulation_data: Dict[str, Any]):
        """
        Save simulation prompts and responses.

        Args:
            analysis_id: Analysis ID
            simulation_data: Simulation data
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        sim_dir = analysis_dir / "simulation"
        sim_dir.mkdir(exist_ok=True)

        file_path = sim_dir / "simulation_results.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(simulation_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved simulation data", extra={"analysis_id": analysis_id})

    def save_final_report(self, analysis_id: str, report: Dict[str, Any]):
        """
        Save final analysis report.

        Args:
            analysis_id: Analysis ID
            report: Final report data
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        file_path = analysis_dir / "final_report.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved final report", extra={"analysis_id": analysis_id})

    def load_final_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Load final analysis report.

        Args:
            analysis_id: Analysis ID

        Returns:
            Report data or None if not found
        """
        analysis_dir = self.get_analysis_dir(analysis_id)
        file_path = analysis_dir / "final_report.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete_analysis(self, analysis_id: str):
        """
        Delete all files for an analysis.

        Args:
            analysis_id: Analysis ID
        """
        import shutil
        analysis_dir = self.base_path / analysis_id

        if analysis_dir.exists():
            shutil.rmtree(analysis_dir)
            logger.info(f"Deleted analysis data", extra={"analysis_id": analysis_id})

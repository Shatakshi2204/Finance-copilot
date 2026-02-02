"""
Dataset generator for creating training data from macro sources.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .config import MetricType, ChatMLSample
from .triangulation import TriangulationEngine
from .formatter import ChatMLFormatter


logger = logging.getLogger(__name__)


class DatasetGenerator:
    """Generates complete training datasets from macro data."""

    def __init__(
        self,
        fred_api_key: Optional[str] = None,
        tolerance_percent: float = 0.5
    ):
        self.engine = TriangulationEngine(
            tolerance_percent=tolerance_percent,
            fred_api_key=fred_api_key
        )
        self.formatter = ChatMLFormatter()

    def generate_dataset(
        self,
        countries: list[str],
        metrics: list[MetricType],
        question_variants: int = 2,
        include_multi_turn: bool = True
    ) -> list[dict]:
        """
        Generate a complete dataset for the given countries and metrics.
        
        Args:
            countries: List of ISO 3-letter country codes
            metrics: List of MetricType to include
            question_variants: Number of question variants per data point
            include_multi_turn: Whether to include multi-turn conversation samples
            
        Returns:
            List of ChatML samples as dictionaries
        """
        samples = []

        for country in countries:
            country_results = []

            for metric in metrics:
                try:
                    result = self.engine.triangulate(metric, country)
                    country_results.append((result, metric))

                    # Generate single-turn samples with question variants
                    for variant in range(question_variants):
                        sample = self.formatter.format_sample(result, metric, variant)
                        samples.append(self._sample_to_dict(sample))

                except Exception as e:
                    logger.error(f"Error processing {metric.value} for {country}: {e}")
                    continue

            # Generate multi-turn sample for this country
            if include_multi_turn and len(country_results) >= 2:
                results = [r[0] for r in country_results]
                metric_list = [r[1] for r in country_results]
                multi_turn_sample = self.formatter.format_multi_turn(results, metric_list)
                samples.append(self._sample_to_dict(multi_turn_sample))

        return samples

    def _sample_to_dict(self, sample: ChatMLSample) -> dict:
        """Convert ChatMLSample to dictionary for JSON serialization."""
        return {
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in sample.messages
            ]
        }

    def save_jsonl(self, samples: list[dict], output_path: str | Path) -> None:
        """Save samples to a .jsonl file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(samples)} samples to {output_path}")

    def save_json(self, samples: list[dict], output_path: str | Path) -> None:
        """Save samples to a formatted .json file (for inspection)."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(samples)} samples to {output_path}")
"""
CLI entry point for the Macro Data Triangulation Pipeline.
"""

import argparse
import logging

from .config import MetricType
from .generator import DatasetGenerator


logger = logging.getLogger(__name__)


def main():
    """Main entry point for the triangulation pipeline."""
    parser = argparse.ArgumentParser(
        description="Macro Data Triangulation Pipeline for Financial LLM Training"
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=["USA", "IND", "EUU", "CHN"],
        help="ISO 3-letter country codes (default: USA IND EUU CHN)"
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["gdp_growth", "inflation", "unemployment", "interest_rate"],
        default=["gdp_growth", "inflation"],
        help="Metrics to include (default: gdp_growth inflation)"
    )
    parser.add_argument(
        "--output",
        default="data_pipeline/training_data.jsonl",
        help="Output file path (default: data_pipeline/training_data.jsonl)"
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional: Also save as formatted JSON for inspection"
    )
    parser.add_argument(
        "--fred-api-key",
        default=None,
        help="FRED API key (or set FRED_API_KEY env var)"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.5,
        help="Percentage tolerance for source agreement (default: 0.5)"
    )
    parser.add_argument(
        "--question-variants",
        type=int,
        default=2,
        help="Number of question variants per data point (default: 2)"
    )
    parser.add_argument(
        "--no-multi-turn",
        action="store_true",
        help="Disable multi-turn conversation samples"
    )

    args = parser.parse_args()

    # Convert metric strings to enums
    metric_map = {
        "gdp_growth": MetricType.GDP_GROWTH,
        "inflation": MetricType.INFLATION,
        "unemployment": MetricType.UNEMPLOYMENT,
        "interest_rate": MetricType.INTEREST_RATE,
    }
    metrics = [metric_map[m] for m in args.metrics]

    # Generate dataset
    generator = DatasetGenerator(
        fred_api_key=args.fred_api_key,
        tolerance_percent=args.tolerance
    )

    logger.info(f"Generating dataset for countries: {args.countries}")
    logger.info(f"Metrics: {args.metrics}")

    samples = generator.generate_dataset(
        countries=args.countries,
        metrics=metrics,
        question_variants=args.question_variants,
        include_multi_turn=not args.no_multi_turn
    )

    # Save outputs
    generator.save_jsonl(samples, args.output)

    if args.output_json:
        generator.save_json(samples, args.output_json)

    logger.info(f"Dataset generation complete. Total samples: {len(samples)}")


if __name__ == "__main__":
    main()
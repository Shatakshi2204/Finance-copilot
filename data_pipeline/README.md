# Macro Data Triangulation Pipeline

Production-grade pipeline for fetching, triangulating, and formatting macroeconomic data from multiple authoritative sources (FRED, World Bank, OECD) into ChatML format for LLM fine-tuning.

## Target Countries

- **USA** - United States
- **IND** - India
- **EUU** - European Union
- **CHN** - China

## Features

- **Multi-source triangulation**: Cross-references FRED, World Bank, and OECD APIs
- **Confidence scoring**: Automatic HIGH/MEDIUM/LOW confidence based on source agreement
- **ChatML formatting**: Ready-to-use `.jsonl` output for Unsloth/QLoRA training
- **Robust error handling**: Retries, rate limiting, and graceful degradation
- **Extensible**: Easy to add new metrics and countries

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

| Source | Key Required | Registration Link |
|--------|--------------|-------------------|
| FRED | ✅ Yes | [Get FRED API Key](https://fred.stlouisfed.org/docs/api/api_key.html) |
| World Bank | ❌ No | Public API |
| OECD | ❌ No | Public API |

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your FRED_API_KEY
```

Or export directly:

```bash
export FRED_API_KEY=your_key_here
```

## Usage

### Basic Usage (Default: USA, India, EU, China)

```bash
python -m data_pipeline.main
```

### Custom Configuration

```bash
python -m data_pipeline.main \
    --countries USA IND EUU CHN \
    --metrics gdp_growth inflation unemployment interest_rate \
    --output training_data.jsonl \
    --output-json training_data.json \
    --question-variants 3 \
    --tolerance 0.5
```

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--countries` | USA IND EUU CHN | ISO 3-letter country codes |
| `--metrics` | gdp_growth inflation | Metrics to include |
| `--output` | training_data.jsonl | Output JSONL path |
| `--output-json` | None | Optional JSON output for inspection |
| `--fred-api-key` | env var | FRED API key |
| `--tolerance` | 0.5 | % tolerance for agreement |
| `--question-variants` | 2 | Question variants per sample |
| `--no-multi-turn` | False | Disable multi-turn samples |

## Output Format

### ChatML Structure

```json
{
  "messages": [
    {"role": "system", "content": "You are a financial risk assistant..."},
    {"role": "user", "content": "What is the inflation rate in India?"},
    {"role": "assistant", "content": "Based on FRED (4.5%), World Bank (4.3%)..."}
  ]
}
```

### Confidence Levels

| Level | Meaning |
|-------|---------|
| HIGH | All 3 sources agree within tolerance |
| MEDIUM | 2 sources agree, or 2 available and agree |
| LOW | All sources disagree significantly |
| SINGLE_SOURCE | Only 1 source returned data |
| NO_DATA | No sources returned valid data |

## Supported Metrics

- `gdp_growth` - Real GDP Growth Rate
- `inflation` - Consumer Price Index (CPI) Inflation
- `unemployment` - Unemployment Rate
- `interest_rate` - Policy/Central Bank Interest Rate

## Project Structure

```
data_pipeline/
├── __init__.py          # Package exports
├── config.py            # Enums and dataclasses
├── mappings.py          # Country & metric mappings
├── http_client.py       # HTTP client with retry logic
├── clients/
│   ├── __init__.py
│   ├── base.py          # Abstract base client
│   ├── fred.py          # FRED API client
│   ├── worldbank.py     # World Bank API client
│   └── oecd.py          # OECD API client
├── triangulation.py     # Triangulation engine
├── formatter.py         # ChatML formatter
├── generator.py         # Dataset generator
├── main.py              # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Programmatic Usage

```python
from data_pipeline import DatasetGenerator, MetricType

generator = DatasetGenerator(fred_api_key="your_key")

samples = generator.generate_dataset(
    countries=["USA", "IND", "EUU", "CHN"],
    metrics=[MetricType.GDP_GROWTH, MetricType.INFLATION],
    question_variants=2,
    include_multi_turn=True
)

generator.save_jsonl(samples, "output/training_data.jsonl")
```
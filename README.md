# 📊 Financial LLM Copilot

An AI-powered macroeconomic analysis assistant that provides real-time financial insights using multi-source data triangulation and a fine-tuned Large Language Model.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

✅ **Real-Time Data** - Live economic data from FRED, World Bank, and OECD APIs  
✅ **Data Triangulation** - Cross-references multiple sources for confidence scoring  
✅ **AI-Powered Chat** - Fine-tuned Mistral 7B model for financial Q&A  
✅ **Interactive Dashboard** - Charts, gauges, and risk heatmaps  
✅ **Multi-Country Analysis** - USA, India, European Union, China  
✅ **Stable Performance** - Handles multiple consecutive requests without crashes  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
├─────────────────────────────────────────────────────────────┤
│  💬 Chat    │    📊 Data Panel    │    📈 Analytics         │
└──────┬──────┴─────────┬───────────┴──────────┬──────────────┘
       │                │                      │
       ▼                ▼                      ▼
┌──────────────┐  ┌─────────────┐  ┌───────────────────────┐
│  LLM Engine  │  │Data Fetcher │  │   Visualizations      │
│  (Mistral)   │  │(Triangulate)│  │   (Plotly Charts)     │
└──────────────┘  └──────┬──────┘  └───────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐    ┌───────────┐    ┌──────────┐
   │  FRED   │    │World Bank │    │   OECD   │
   │   API   │    │    API    │    │   API    │
   └─────────┘    └───────────┘    └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM (for running the LLM)
- 4.1GB disk space (for model)
- FRED API Key ([Get it free here](https://fred.stlouisfed.org/docs/api/api_key.html))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shatakshi2204/Finance-copilot.git
   cd Finance-copilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the template
   copy .env.example .env
   
   # Edit .env and add your API keys
   ```
   
   Required keys in `.env`:
   ```
   FRED_API_KEY=your_fred_api_key_here
   HF_TOKEN=your_huggingface_token_here
   HF_USERNAME=your_huggingface_username
   ```

4. **Download the model** (First time only, ~4GB)
   ```bash
   cd app
   python download_model.py
   ```

5. **Launch the application**
   ```bash
   python -m streamlit run app.py
   ```

6. **Open in your browser**
   ```
   http://localhost:8501
   ```

## 📋 Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `python -m streamlit run app.py` | Launch the web app |
| `python app/download_model.py` | Download LLM model |
| `git push origin main` | Push to GitHub |

## 📁 Project Structure

```
Finance-copilot/
├── app/                          # 🎨 Streamlit Application
│   ├── app.py                    # Main application entry point
│   ├── chat_engine.py            # Chat orchestration & intent detection
│   ├── config.py                 # Configuration (conservative settings)
│   ├── data_fetcher.py           # Real-time data from FRED, WB, OECD
│   ├── model_loader.py           # LLM loading & inference engine
│   ├── visualizations.py         # Interactive Plotly charts
│   ├── utils.py                  # Utility & formatting functions
│   ├── download_model.py         # Model downloader
│   ├── requirements.txt          # Python dependencies
│   └── packages.txt              # System packages
│
├── data_pipeline/                # 📊 Data Pipeline for Training
│   ├── clients/
│   │   ├── fred.py               # FRED API client
│   │   ├── worldbank.py          # World Bank client
│   │   ├── oecd.py               # OECD API client
│   │   └── base.py               # Base client class
│   ├── generator.py              # Training data generator
│   ├── triangulation.py          # Multi-source triangulation
│   ├── formatter.py              # Data formatting
│   ├── config.py                 # Pipeline config
│   ├── main.py                   # Pipeline entry point
│   └── requirements.txt          # Pipeline dependencies
│
├── finance_copilot.py            # Core implementation
├── finance_copilot.ipynb         # Jupyter notebook
├── .env                          # ⚠️ Environment variables (NOT in git)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 📊 Data Sources

| Source | Metrics | Coverage | API Key |
|--------|---------|----------|---------|
| **FRED** | US GDP, Inflation, Unemployment, Interest Rates | USA | ✅ Required |
| **World Bank** | All economic indicators | 190+ countries | ❌ None |
| **OECD** | Economic statistics | OECD members | ❌ None |

## 🤖 LLM Model Details

| Property | Value |
|----------|-------|
| **Base Model** | Mistral 7B Instruct v0.3 |
| **Fine-tuning** | QLoRA (4-bit quantization) |
| **Format** | GGUF (Q4_K_M) |
| **Size** | ~4.1 GB |
| **Context** | 256 tokens (optimized) |
| **Max Output** | 100 tokens per response |
| **Temperature** | 0.2 (deterministic) |

## 💻 System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8 GB
- Disk: 5 GB free
- OS: Windows, macOS, Linux

### Recommended
- CPU: 8+ cores
- RAM: 16 GB
- Disk: 10 GB SSD
- GPU: Optional (for faster inference)

## 🎯 How It Works

### 1. User Asks a Question
```
"What is the current US inflation rate?"
```

### 2. Intent Detection
- Detects country: USA
- Detects metric: Inflation
- Builds context prompt with live data

### 3. Data Triangulation
```
FRED API       → 3.4%
World Bank API → 3.2%
OECD API       → 3.3%
─────────────────────
Consensus: 3.3% (HIGH confidence)
```

### 4. LLM Response Generation
- Uses fine-tuned Mistral 7B model
- Generates concise, data-driven response
- Cites specific sources

### 5. Display Results
- Shows response with data sources
- Charts comparing data sources
- Confidence gauge

## 📈 Supported Metrics

| Metric | Unit | Available For |
|--------|------|---|
| GDP Growth | % | USA, IND, EUU, CHN |
| Inflation | % | USA, IND, CHN, EUU |
| Unemployment | % | USA, EUU |
| Interest Rate | % | USA, IND, CHN, EUU |

## 🔧 Configuration

### Model Settings (in `app/config.py`)

```python
ModelConfig:
    n_ctx: 256           # Context window
    n_threads: 2         # CPU threads
    max_tokens: 100      # Response length
    temperature: 0.2     # Determinism (0.0-1.0)
```

### API Timeouts (in `app/config.py`)

```python
APIConfig:
    timeout: 10          # Seconds per API call
    max_retries: 2       # Retry attempts
```

## 🐛 Troubleshooting

### App Crashes After First Response

**Solution**: Increase available RAM or reduce `n_ctx` in `config.py`
```python
# In app/config.py
n_ctx: int = 256  # Reduce from 512 to 256
```

### FRED API Returns 400 Error

**Reason**: Invalid series ID or API key issue
**Solution**: 
- Verify API key in `.env`
- App automatically falls back to cached data

### Model Download Takes Too Long

**Reason**: Large file (4.1 GB) and network speed
**Solution**: 
- Use WiFi instead of mobile hotspot
- Run: `pip install hf_xet` for faster downloads

### Port 8501 Already in Use

**Solution**:
```bash
python -m streamlit run app.py --server.port 8502
```

## 🔐 Security

### Environment Variables
- ⚠️ **Never commit `.env` file** - it contains API keys
- `.env` is in `.gitignore` for safety
- All credentials should be in `.env` only

### Secrets in Code
- HuggingFace tokens removed from source
- No API keys in commits
- Use `.env` template provided

## 📝 Usage Examples

### Example 1: Check US Inflation
```
Q: What is the current US inflation?
A: Current US inflation is 3.4%, based on latest CPI data from FRED.
   Confidence: HIGH (verified by World Bank data)
```

### Example 2: Compare Countries
```
Q: How does China's GDP compare to India?
A: China GDP: 5.2% vs India GDP: 6.8%
   India showing stronger growth. Sources: World Bank + OECD
```

### Example 3: Risk Assessment
```
Q: Is US unemployment a concern?
A: US unemployment at 3.7% is relatively low.
   Risk Level: LOW. Confidence: HIGH (3-source agreement)
```

## 📊 Data Caching

- Data cached for **1 hour** to reduce API calls
- Fallback data used if all APIs fail
- Automatic refresh available in UI

## 🚢 Performance Optimizations

✅ Global model singleton - loaded once  
✅ Streamlit caching - 1 hour TTL  
✅ Garbage collection after each request  
✅ Conservative model parameters  
✅ Parallel API requests  
✅ Input length validation  

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `data_pipeline/README.md` | Data pipeline documentation |
| `finance_copilot.ipynb` | Interactive notebook walkthrough |
| `.env.example` | Environment variables template |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support

For issues or questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [GitHub Issue](https://github.com/Shatakshi2204/Finance-copilot/issues)
3. Review the Jupyter notebook for detailed examples

## 📞 Contact

- **Author**: Financial LLM Copilot Team
- **GitHub**: [Shatakshi2204/Finance-copilot](https://github.com/Shatakshi2204/Finance-copilot)
- **Issues**: [Report a bug](https://github.com/Shatakshi2204/Finance-copilot/issues)

## 🙏 Acknowledgments

- **Mistral AI** - For the excellent Mistral 7B model
- **FRED** - Federal Reserve Economic Data
- **World Bank** - Open data access
- **OECD** - Economic statistics
- **Streamlit** - Amazing web framework
- **HuggingFace** - Model hosting and tools

## 📊 Project Statistics

- **Lines of Code**: 5,000+
- **Data Sources**: 3 (FRED, World Bank, OECD)
- **Countries Supported**: 4
- **Metrics Tracked**: 4
- **Model Size**: 4.1 GB
- **Response Time**: <5 seconds

## 🗺️ Roadmap

### Completed ✅
- [x] Streamlit web application
- [x] FRED API integration
- [x] World Bank API integration
- [x] OECD API integration
- [x] Data triangulation
- [x] LLM fine-tuning
- [x] Real-time response generation
- [x] Interactive visualizations
- [x] GitHub deployment

### Upcoming 🚀
- [ ] Stock market data integration
- [ ] Historical trend analysis
- [ ] Forecasting models
- [ ] Multi-language support
- [ ] API endpoint for backend
- [ ] Docker containerization
- [ ] Advanced risk analytics
- [ ] Mobile app

---

**Last Updated**: February 2, 2026  
**Status**: ✅ Production Ready

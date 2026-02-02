"""
Financial LLM Copilot - Streamlit Application
=============================================
Stable version - handles multiple requests properly.
"""

import streamlit as st
import logging
from datetime import datetime
import gc

# Page config MUST be first
st.set_page_config(
    page_title="Financial LLM Copilot",
    page_icon="📊",
    layout="wide"
)

# Imports
from config import app_config, validate_config
from model_loader import load_llm_model, generate_response, is_model_loaded
from data_fetcher import get_data
from visualizations import (
    create_source_comparison_chart,
    create_confidence_gauge,
    create_country_comparison_chart,
    create_metrics_overview_chart,
    create_risk_heatmap
)
from utils import (
    format_percentage,
    get_confidence_emoji,
    get_confidence_description,
    get_risk_level,
    sanitize_input,
    setup_logging
)

setup_logging()
logger = logging.getLogger(__name__)

# Minimal CSS
st.markdown("<style>.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)


def init_state():
    """Initialize session state."""
    defaults = {
        "messages": [],
        "model_ready": False,
        "country": "USA",
        "metric": "gdp_growth"
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sidebar():
    """Render sidebar."""
    with st.sidebar:
        st.title("📊 Fin Copilot")
        
        # Model section
        st.subheader("AI Model")
        if st.session_state.model_ready:
            st.success("✅ Ready")
        else:
            if st.button("🚀 Load Model", type="primary"):
                with st.spinner("Loading (~30s)..."):
                    try:
                        load_llm_model()
                        st.session_state.model_ready = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.divider()
        
        # Data selection
        st.subheader("Data")
        st.session_state.country = st.selectbox(
            "Country",
            list(app_config.countries.keys()),
            format_func=lambda x: app_config.countries[x]
        )
        st.session_state.metric = st.selectbox(
            "Metric", 
            list(app_config.metrics.keys()),
            format_func=lambda x: app_config.metrics[x]
        )
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            gc.collect()
            st.rerun()


def get_context_data(question: str) -> str:
    """Build context from economic data."""
    q = question.lower()
    
    # Detect country
    country = st.session_state.country
    for code, words in {"USA": ["us", "america"], "IND": ["india"], "EUU": ["eu", "europe"], "CHN": ["china"]}.items():
        if any(w in q for w in words):
            country = code
            break
    
    # Detect metric
    metric = st.session_state.metric
    for key, words in {"gdp_growth": ["gdp"], "inflation": ["inflation"], "unemployment": ["unemploy", "job"], "interest_rate": ["interest", "rate"]}.items():
        if any(w in q for w in words):
            metric = key
            break
    
    try:
        data = get_data(metric, country)
        if data.consensus_value:
            return f"""Data: {data.country} {app_config.metrics[metric]}
Value: {data.consensus_value:.1f}%
Period: {data.period}
Confidence: {data.confidence}

Question: {question}
Answer briefly with the data above:"""
    except:
        pass
    
    return question


def chat_tab():
    """Chat interface."""
    st.subheader("💬 Chat")
    
    if not st.session_state.model_ready:
        st.info("👈 Load the AI model first")
        return
    
    # Show history
    for msg in st.session_state.messages[-6:]:  # Only show last 6
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input
    if prompt := st.chat_input("Ask about economics..."):
        prompt = sanitize_input(prompt)[:500]  # Limit input length
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    context = get_context_data(prompt)
                    response = generate_response(context)
                    gc.collect()  # Clean up after generation
                except Exception as e:
                    logger.error(f"Error: {e}")
                    response = "Sorry, an error occurred. Please try again."
            
            st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Keep only recent messages to save memory
        if len(st.session_state.messages) > 10:
            st.session_state.messages = st.session_state.messages[-10:]


def data_tab():
    """Data panel."""
    st.subheader("📊 Economic Data")
    
    country = st.session_state.country
    metric = st.session_state.metric
    
    try:
        data = get_data(metric, country)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {app_config.metrics[metric]} - {app_config.countries[country]}")
            
            if data.consensus_value:
                st.metric("Value", format_percentage(data.consensus_value))
                
                c1, c2, c3 = st.columns(3)
                c1.metric("FRED", format_percentage(data.fred_value))
                c2.metric("World Bank", format_percentage(data.worldbank_value))
                c3.metric("Confidence", data.confidence.upper())
        
        with col2:
            try:
                st.plotly_chart(create_confidence_gauge(data.confidence), use_container_width=True)
            except:
                pass
        
        if data.consensus_value:
            try:
                st.plotly_chart(create_source_comparison_chart(data), use_container_width=True)
            except:
                pass
                
    except Exception as e:
        st.error(f"Could not load data: {e}")


def analytics_tab():
    """Analytics dashboard."""
    st.subheader("📈 Analytics")
    
    t1, t2, t3 = st.tabs(["Overview", "Compare", "Risk"])
    
    with t1:
        try:
            st.plotly_chart(create_metrics_overview_chart(st.session_state.country), use_container_width=True)
        except:
            st.info("Chart unavailable")
    
    with t2:
        try:
            st.plotly_chart(create_country_comparison_chart(st.session_state.metric), use_container_width=True)
        except:
            st.info("Chart unavailable")
    
    with t3:
        try:
            st.plotly_chart(create_risk_heatmap(), use_container_width=True)
        except:
            st.info("Chart unavailable")


def main():
    init_state()
    sidebar()
    
    st.title("📊 Financial LLM Copilot")
    
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Data", "📈 Analytics"])
    
    with tab1:
        chat_tab()
    with tab2:
        data_tab()
    with tab3:
        analytics_tab()


if __name__ == "__main__":
    main()

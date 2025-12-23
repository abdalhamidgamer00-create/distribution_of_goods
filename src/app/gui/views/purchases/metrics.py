"""Purchases view metrics component."""
import os
import streamlit as st

def show_metrics() -> None:
    """Display quick metrics about files and branches."""
    col1, col2 = st.columns(2)
    output_dir = os.path.join("data", "output")
    
    file_count = 0
    if os.path.exists(output_dir):
        file_count = sum(len(f) for _, _, f in os.walk(output_dir))
        
    col1.metric("عدد الملفات", file_count)
    col2.metric("عدد الفروع", 6)

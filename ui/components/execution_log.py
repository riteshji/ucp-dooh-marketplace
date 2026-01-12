"""
Execution Log Component

Displays a rolling log of UCP API calls with expandable request/response details.
"""

import streamlit as st
from typing import Optional
import json


def render_execution_log(log_entries: list, title: str = "UCP Execution Log"):
    """
    Render the rolling UCP execution log.
    
    Args:
        log_entries: List of LogEntry objects from the UCP client
        title: Title for the log section
    """
    st.subheader(f"📋 {title}")
    
    if not log_entries:
        st.info("Execute a checkout flow to see the UCP API calls here.")
        return
    
    # Create a container for the log
    log_container = st.container()
    
    with log_container:
        for entry in log_entries:
            # Determine icon based on status
            icon = {
                "pending": "⏸️",
                "running": "⏳",
                "success": "✅",
                "error": "❌"
            }.get(entry.status, "❓")
            
            # Determine border color based on status
            if entry.status == "success":
                border_style = "border-left: 4px solid #28a745;"
            elif entry.status == "error":
                border_style = "border-left: 4px solid #dc3545;"
            elif entry.status == "running":
                border_style = "border-left: 4px solid #ffc107;"
            else:
                border_style = "border-left: 4px solid #6c757d;"
            
            # Create styled container
            with st.container():
                st.markdown(
                    f"""
                    <div style="{border_style} padding-left: 10px; margin-bottom: 10px;">
                        <strong>{icon} Step {entry.step}: {entry.title}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Show HTTP method and endpoint
                col1, col2 = st.columns([1, 4])
                with col1:
                    method_color = {
                        "GET": "#61affe",
                        "POST": "#49cc90",
                        "PUT": "#fca130",
                        "DELETE": "#f93e3e"
                    }.get(entry.method, "#6c757d")
                    st.markdown(
                        f'<span style="background-color: {method_color}; color: white; '
                        f'padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold;">'
                        f'{entry.method}</span>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.code(entry.endpoint, language=None)
                
                # Show message/result
                if entry.message:
                    if entry.status == "success":
                        st.success(entry.message)
                    elif entry.status == "error":
                        st.error(entry.message)
                    else:
                        st.info(entry.message)
                
                # Show duration if available
                if entry.duration_ms:
                    st.caption(f"⏱️ {entry.duration_ms:.0f}ms")
                
                # Expandable request/response details
                if entry.request_body or entry.response_body:
                    with st.expander("🔍 View Request/Response Details"):
                        if entry.request_body:
                            st.markdown("**📤 Request Body:**")
                            st.json(entry.request_body)
                        
                        if entry.response_body:
                            st.markdown(f"**📥 Response ({entry.response_status}):**")
                            # Limit response size for display
                            response_str = json.dumps(entry.response_body, indent=2)
                            if len(response_str) > 3000:
                                st.json(entry.response_body)
                            else:
                                st.json(entry.response_body)
                
                st.divider()


def render_live_status(current_step: str, is_running: bool = False):
    """
    Render a live status indicator for the current operation.
    
    Args:
        current_step: Description of current step
        is_running: Whether the operation is currently running
    """
    if is_running:
        with st.status(current_step, expanded=True) as status:
            st.write("Processing...")
            return status
    return None

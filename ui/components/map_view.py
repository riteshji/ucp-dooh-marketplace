"""
Map View Component

Displays DOOH screen locations on an interactive map.
"""

import streamlit as st
import pandas as pd
from typing import Optional


def parse_coordinates(screens: list[dict]) -> pd.DataFrame:
    """
    Parse GPS coordinates from screen data into a DataFrame for mapping.
    
    Args:
        screens: List of screen dictionaries with gps_coordinates field
    
    Returns:
        DataFrame with lat, lon, and screen info columns
    """
    data = []
    
    for screen in screens:
        coords = screen.get("gps_coordinates", "")
        if coords:
            try:
                lat, lon = coords.split(", ")
                data.append({
                    "lat": float(lat),
                    "lon": float(lon),
                    "name": screen.get("title", "Unknown"),
                    "venue_type": screen.get("venue_type", "Unknown"),
                    "city": screen.get("city", "Unknown"),
                    "price": screen.get("price", 0),
                    "id": screen.get("id", "")
                })
            except (ValueError, AttributeError):
                continue
    
    return pd.DataFrame(data)


def render_map(
    screens: list[dict],
    selected_ids: Optional[list[str]] = None,
    height: int = 400
):
    """
    Render an interactive map showing screen locations.
    
    Args:
        screens: List of screen dictionaries
        selected_ids: List of selected screen IDs to highlight
        height: Map height in pixels
    """
    st.subheader("🗺️ Screen Locations")
    
    if not screens:
        st.info("No screens to display on map.")
        return
    
    # Parse coordinates
    df = parse_coordinates(screens)
    
    if df.empty:
        st.warning("No valid coordinates found in screen data.")
        return
    
    # Add selection indicator
    if selected_ids:
        df["selected"] = df["id"].isin(selected_ids)
    else:
        df["selected"] = False
    
    # Display map
    st.map(
        df,
        latitude="lat",
        longitude="lon",
        size=20,
        color="#FF4B4B"
    )
    
    # Legend
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🟢 **Billboard**")
    with col2:
        st.markdown("🔵 **Transit**")
    with col3:
        st.markdown("🟡 **Retail**")
    with col4:
        st.markdown("🟣 **Airport**")
    
    # Screen count by city
    if not df.empty:
        st.caption(f"Showing {len(df)} screens across {df['city'].nunique()} cities")


def render_mini_map(screens: list[dict], selected_ids: list[str]):
    """
    Render a compact map for the sidebar.
    
    Args:
        screens: List of screen dictionaries
        selected_ids: List of selected screen IDs
    """
    df = parse_coordinates(screens)
    
    if df.empty:
        return
    
    # Filter to selected only if any selected
    if selected_ids:
        selected_df = df[df["id"].isin(selected_ids)]
        if not selected_df.empty:
            st.map(selected_df, latitude="lat", longitude="lon", size=30)
            st.caption(f"{len(selected_df)} screens selected")
        else:
            st.map(df, latitude="lat", longitude="lon", size=10)
    else:
        st.map(df, latitude="lat", longitude="lon", size=10)

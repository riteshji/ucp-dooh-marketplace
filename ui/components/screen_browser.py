"""
Screen Browser Component

Displays DOOH screen inventory with filtering and selection capabilities.
"""

import streamlit as st
from typing import Callable, Optional


# Sample DOOH screen data (would be loaded from API in production)
DOOH_SCREENS = [
    {
        "id": "BB-NYC-001",
        "title": "Times Square Digital Billboard #12",
        "description": "Premium high-traffic billboard facing Broadway in NYC. 48x14ft LED 4K Outdoor. Ideal for brand awareness.",
        "venue_type": "Billboard",
        "city": "New York",
        "state": "NY",
        "gps_coordinates": "40.7580, -73.9855",
        "environment": "Outdoor",
        "daily_impressions": 125000,
        "price": 50000,  # cents
        "image_url": "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=400",
    },
    {
        "id": "BB-LA-001",
        "title": "Sunset Blvd Digital West",
        "description": "Iconic Sunset Strip location near entertainment venues. 40x12ft LED 4K Outdoor.",
        "venue_type": "Billboard",
        "city": "Los Angeles",
        "state": "CA",
        "gps_coordinates": "34.0982, -118.3868",
        "environment": "Outdoor",
        "daily_impressions": 95000,
        "price": 35000,
        "image_url": "https://images.unsplash.com/photo-1617953141905-b27fb1f17d88?w=400",
    },
    {
        "id": "BB-CHI-001",
        "title": "Michigan Ave Billboard",
        "description": "Prime location on Magnificent Mile Chicago. 36x10ft LED 4K Outdoor.",
        "venue_type": "Billboard",
        "city": "Chicago",
        "state": "IL",
        "gps_coordinates": "41.8902, -87.6244",
        "environment": "Outdoor",
        "daily_impressions": 85000,
        "price": 32000,
        "image_url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400",
    },
    {
        "id": "TR-NYC-001",
        "title": "Grand Central Kiosk A",
        "description": "Portrait screen in main concourse NYC. Captive commuter audience. 4x6ft LCD 1080p Indoor.",
        "venue_type": "Transit",
        "city": "New York",
        "state": "NY",
        "gps_coordinates": "40.7527, -73.9772",
        "environment": "Indoor",
        "daily_impressions": 45000,
        "price": 15000,
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=400",
    },
    {
        "id": "TR-CHI-001",
        "title": "O'Hare Terminal 1 Gate B12",
        "description": "Gate-area screen with 15+ min dwell time. Business travelers. 10x6ft LED 4K Indoor.",
        "venue_type": "Airport",
        "city": "Chicago",
        "state": "IL",
        "gps_coordinates": "41.9742, -87.9073",
        "environment": "Indoor",
        "daily_impressions": 65000,
        "price": 20000,
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400",
    },
    {
        "id": "RT-NYC-001",
        "title": "Westfield WTC Mall Entrance",
        "description": "Prime entrance at World Trade Center mall NYC. 8x5ft LCD 1080p Indoor.",
        "venue_type": "Retail",
        "city": "New York",
        "state": "NY",
        "gps_coordinates": "40.7115, -74.0125",
        "environment": "Indoor",
        "daily_impressions": 38000,
        "price": 8500,
        "image_url": "https://images.unsplash.com/photo-1519567241046-7f570f9b5937?w=400",
    },
    {
        "id": "RT-MIA-001",
        "title": "Aventura Mall Food Court",
        "description": "Family-friendly food court location Miami. Weekend traffic spike. 8x5ft LCD 1080p Indoor.",
        "venue_type": "Retail",
        "city": "Miami",
        "state": "FL",
        "gps_coordinates": "25.9567, -80.1423",
        "environment": "Indoor",
        "daily_impressions": 28000,
        "price": 6000,
        "image_url": "https://images.unsplash.com/photo-1567449303183-ae0d6ed1498e?w=400",
    },
    {
        "id": "AP-JFK-001",
        "title": "JFK Terminal 4 Departures",
        "description": "International departures hall. Premium traveler audience. 15x10ft LED 4K Indoor.",
        "venue_type": "Airport",
        "city": "New York",
        "state": "NY",
        "gps_coordinates": "40.6413, -73.7781",
        "environment": "Indoor",
        "daily_impressions": 80000,
        "price": 25000,
        "image_url": "https://images.unsplash.com/photo-1474302770737-173ee21bab63?w=400",
    },
]


def get_venue_types() -> list[str]:
    """Get unique venue types from screen data."""
    return sorted(list(set(s["venue_type"] for s in DOOH_SCREENS)))


def get_cities() -> list[str]:
    """Get unique cities from screen data."""
    return sorted(list(set(s["city"] for s in DOOH_SCREENS)))


def filter_screens(
    venue_type: Optional[str] = None,
    city: Optional[str] = None,
    max_price: Optional[int] = None
) -> list[dict]:
    """Filter screens based on criteria."""
    filtered = DOOH_SCREENS.copy()
    
    if venue_type and venue_type != "All":
        filtered = [s for s in filtered if s["venue_type"] == venue_type]
    
    if city and city != "All":
        filtered = [s for s in filtered if s["city"] == city]
    
    if max_price:
        filtered = [s for s in filtered if s["price"] <= max_price * 100]
    
    return filtered


def render_screen_card(screen: dict, on_add: Callable, cart_ids: list[str]):
    """
    Render a single screen card.
    
    Args:
        screen: Screen data dictionary
        on_add: Callback when "Add to Campaign" is clicked
        cart_ids: List of screen IDs already in cart
    """
    is_in_cart = screen["id"] in cart_ids
    
    with st.container(border=True):
        # Image and basic info
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(screen["image_url"], use_container_width=True)
        
        with col2:
            st.markdown(f"### {screen['title']}")
            
            # Tags
            venue_color = {
                "Billboard": "🟢",
                "Transit": "🔵",
                "Retail": "🟡",
                "Airport": "🟣"
            }.get(screen["venue_type"], "⚪")
            
            st.markdown(
                f"{venue_color} **{screen['venue_type']}** | "
                f"📍 {screen['city']}, {screen['state']} | "
                f"{'🌳 Outdoor' if screen['environment'] == 'Outdoor' else '🏢 Indoor'}"
            )
            
            st.caption(screen["description"])
            
            # Stats
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Daily Impressions", f"{screen['daily_impressions']:,}")
            with col_b:
                st.metric("Price/Day", f"${screen['price']/100:,.2f}")
        
        # Add button
        col_btn, col_days = st.columns([2, 1])
        with col_days:
            days = st.number_input(
                "Days",
                min_value=1,
                max_value=30,
                value=7,
                key=f"days_{screen['id']}"
            )
        with col_btn:
            if is_in_cart:
                st.button(
                    "✓ In Campaign",
                    key=f"add_{screen['id']}",
                    disabled=True,
                    use_container_width=True
                )
            else:
                if st.button(
                    "➕ Add to Campaign",
                    key=f"add_{screen['id']}",
                    type="primary",
                    use_container_width=True
                ):
                    screen_with_days = screen.copy()
                    screen_with_days["days"] = days
                    on_add(screen_with_days)


def render_screen_browser(on_add: Callable, cart_ids: list[str]):
    """
    Render the full screen browser with filters.
    
    Args:
        on_add: Callback when a screen is added to cart
        cart_ids: List of screen IDs already in cart
    """
    st.subheader("📺 DOOH Screen Inventory")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        venue_filter = st.selectbox(
            "Venue Type",
            ["All"] + get_venue_types(),
            key="venue_filter"
        )
    
    with col2:
        city_filter = st.selectbox(
            "City",
            ["All"] + get_cities(),
            key="city_filter"
        )
    
    with col3:
        max_price = st.slider(
            "Max Price/Day ($)",
            min_value=50,
            max_value=600,
            value=600,
            step=50,
            key="price_filter"
        )
    
    # Filter and display screens
    filtered_screens = filter_screens(
        venue_type=venue_filter if venue_filter != "All" else None,
        city=city_filter if city_filter != "All" else None,
        max_price=max_price
    )
    
    st.caption(f"Showing {len(filtered_screens)} screens")
    
    # Display screens in a grid
    for screen in filtered_screens:
        render_screen_card(screen, on_add, cart_ids)

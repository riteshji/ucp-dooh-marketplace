"""
DOOH Screen Marketplace - UCP Demo

A Streamlit application demonstrating DOOH (Digital Out-of-Home) screen 
buying using the Universal Commerce Protocol (UCP).

Run with: streamlit run app.py
"""

import streamlit as st
from typing import Optional
import time

# Import components
from components.screen_browser import render_screen_browser, DOOH_SCREENS
from components.cart import render_cart, render_order_confirmation
from components.execution_log import render_execution_log
from components.map_view import render_map
from services.ucp_client import UCPClient, LogEntry


# Page config
st.set_page_config(
    page_title="Using UCP for DOOH Marketplace",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if "cart" not in st.session_state:
        st.session_state.cart = []
    
    if "log_entries" not in st.session_state:
        st.session_state.log_entries = []
    
    if "discount_code" not in st.session_state:
        st.session_state.discount_code = ""
    
    if "applied_discount" not in st.session_state:
        st.session_state.applied_discount = 0
    
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    if "order_complete" not in st.session_state:
        st.session_state.order_complete = False
    
    if "order_data" not in st.session_state:
        st.session_state.order_data = None
    
    if "ucp_client" not in st.session_state:
        st.session_state.ucp_client = None


def add_log_entry(entry: LogEntry):
    """Callback to add log entry to session state."""
    # Update existing entry if same step, otherwise add new
    for i, existing in enumerate(st.session_state.log_entries):
        if existing.step == entry.step:
            st.session_state.log_entries[i] = entry
            return
    st.session_state.log_entries.append(entry)


def add_to_cart(screen: dict):
    """Add a screen to the cart."""
    # Check if already in cart
    cart_ids = [item["id"] for item in st.session_state.cart]
    if screen["id"] not in cart_ids:
        st.session_state.cart.append(screen)
        st.success(f"Added {screen['title'][:30]}... to campaign!")
    st.rerun()


def remove_from_cart(index: int):
    """Remove a screen from the cart by index."""
    if 0 <= index < len(st.session_state.cart):
        removed = st.session_state.cart.pop(index)
        st.info(f"Removed {removed['title'][:30]}... from campaign")
    st.rerun()


def apply_discount(code: str):
    """Apply a discount code."""
    st.session_state.discount_code = code
    
    # Map discount codes to percentages
    discount_map = {
        "LAUNCH20": 20,
        "BULK10": 10,
        "AGENCY15": 15,
        "FIRST500": 0  # Fixed amount handled differently
    }
    
    code_upper = code.upper()
    if code_upper in discount_map:
        st.session_state.applied_discount = discount_map[code_upper]
        st.success(f"Discount code {code_upper} applied!")
    else:
        st.error(f"Invalid discount code: {code}")
    st.rerun()


def run_checkout():
    """Execute the full UCP checkout flow."""
    st.session_state.is_processing = True
    st.session_state.log_entries = []  # Clear previous logs
    st.session_state.order_complete = False
    st.session_state.order_data = None
    
    # Create UCP client with logging callback
    client = UCPClient(
        base_url="http://localhost:8182",
        on_log=add_log_entry
    )
    st.session_state.ucp_client = client
    
    try:
        # Step 1: Discovery
        client.discover()
        st.rerun()
        
    except Exception as e:
        st.error(f"Checkout failed: {e}")
        st.session_state.is_processing = False


def continue_checkout():
    """Continue the checkout process after discovery."""
    client = st.session_state.ucp_client
    if not client:
        return
    
    cart = st.session_state.cart
    
    try:
        # Step 2: Create checkout with cart items
        client.create_checkout(
            screens=cart,
            buyer_name="Sarah Johnson",
            buyer_email="sarah.johnson@mediaagency.com"
        )
        
        # Step 3: Apply discount if any
        if st.session_state.discount_code:
            client.apply_discount(st.session_state.discount_code.upper())
        
        # Step 4: Setup fulfillment
        client.setup_fulfillment()
        
        # Step 5: Complete checkout
        result = client.complete_checkout()
        
        st.session_state.order_complete = True
        st.session_state.order_data = result
        st.session_state.is_processing = False
        
    except Exception as e:
        st.error(f"Checkout failed: {e}")
        st.session_state.is_processing = False
    
    finally:
        client.close()
        st.session_state.ucp_client = None


def reset_demo():
    """Reset the demo to start fresh."""
    st.session_state.cart = []
    st.session_state.log_entries = []
    st.session_state.discount_code = ""
    st.session_state.applied_discount = 0
    st.session_state.is_processing = False
    st.session_state.order_complete = False
    st.session_state.order_data = None
    st.rerun()


def main():
    """Main application."""
    init_session_state()
    
    # Header
    st.title("📺 DOOH Screen Marketplace")
    st.markdown("*Powered by Universal Commerce Protocol (UCP)*")
    
    # Server status check
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        server_url = st.text_input(
            "UCP Server URL",
            value="http://localhost:8182",
            help="URL of the UCP merchant server"
        )
        
        st.divider()
        
        # Quick stats
        st.markdown("### 📊 Campaign Summary")
        cart_ids = [item["id"] for item in st.session_state.cart]
        st.metric("Screens Selected", len(st.session_state.cart))
        
        total_days = sum(item.get("days", 1) for item in st.session_state.cart)
        st.metric("Total Days", total_days)
        
        subtotal = sum(item["price"] * item.get("days", 1) for item in st.session_state.cart)
        st.metric("Subtotal", f"${subtotal/100:,.2f}")
        
        st.divider()
        
        # Reset button
        if st.button("🔄 Reset Demo", use_container_width=True):
            reset_demo()
        
        st.divider()
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        This demo showcases the **Universal Commerce Protocol (UCP)** 
        for DOOH screen buying.
        
        [UCP Documentation](https://ucp.dev)
        
        [GitHub Repository](https://github.com/Universal-Commerce-Protocol)
        """)
    
    # Main content area
    if st.session_state.order_complete and st.session_state.order_data:
        # Show order confirmation
        render_order_confirmation(st.session_state.order_data)
        
        st.divider()
        
        # Show execution log
        render_execution_log(st.session_state.log_entries)
        
        if st.button("🔄 Start New Campaign", type="primary"):
            reset_demo()
    
    else:
        # Normal shopping flow
        col_main, col_cart = st.columns([2, 1])
        
        with col_main:
            # Tabs for different views
            tab_browse, tab_map = st.tabs(["📋 Browse Screens", "🗺️ Map View"])
            
            with tab_browse:
                cart_ids = [item["id"] for item in st.session_state.cart]
                render_screen_browser(add_to_cart, cart_ids)
            
            with tab_map:
                render_map(DOOH_SCREENS, cart_ids)
        
        with col_cart:
            render_cart(
                cart_items=st.session_state.cart,
                on_remove=remove_from_cart,
                on_apply_discount=apply_discount,
                on_checkout=run_checkout,
                discount_code=st.session_state.discount_code,
                applied_discount=st.session_state.applied_discount,
                is_processing=st.session_state.is_processing
            )
        
        # Execution Log (always visible at bottom during checkout)
        if st.session_state.log_entries or st.session_state.is_processing:
            st.divider()
            render_execution_log(st.session_state.log_entries)
            
            # Auto-continue checkout after discovery
            if st.session_state.is_processing and len(st.session_state.log_entries) == 1:
                continue_checkout()
                st.rerun()


if __name__ == "__main__":
    main()

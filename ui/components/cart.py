"""
Shopping Cart Component

Displays the campaign cart with selected screens and checkout controls.
"""

import streamlit as st
from typing import Callable, Optional


def calculate_totals(cart_items: list[dict], discount_percent: float = 0) -> dict:
    """
    Calculate cart totals.
    
    Args:
        cart_items: List of screen items in cart
        discount_percent: Discount percentage to apply (0-100)
    
    Returns:
        Dictionary with subtotal, discount, and total amounts
    """
    subtotal = sum(item["price"] * item.get("days", 1) for item in cart_items)
    discount_amount = int(subtotal * (discount_percent / 100))
    total = subtotal - discount_amount
    
    return {
        "subtotal": subtotal,
        "discount": discount_amount,
        "discount_percent": discount_percent,
        "total": total
    }


def render_cart_item(item: dict, on_remove: Callable, index: int):
    """
    Render a single cart item.
    
    Args:
        item: Screen item in cart
        on_remove: Callback to remove item
        index: Item index for unique keys
    """
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"**{item['title'][:35]}...**" if len(item['title']) > 35 else f"**{item['title']}**")
        st.caption(f"{item['venue_type']} | {item['city']}")
    
    with col2:
        st.markdown(f"**{item.get('days', 1)} days**")
        st.caption(f"${item['price']/100:.0f}/day")
    
    with col3:
        item_total = item["price"] * item.get("days", 1)
        st.markdown(f"**${item_total/100:,.2f}**")
        if st.button("🗑️", key=f"remove_{index}_{item['id']}", help="Remove from cart"):
            on_remove(index)


def render_cart(
    cart_items: list[dict],
    on_remove: Callable,
    on_apply_discount: Callable,
    on_checkout: Callable,
    discount_code: str = "",
    applied_discount: float = 0,
    is_checkout_ready: bool = False,
    is_processing: bool = False
):
    """
    Render the shopping cart.
    
    Args:
        cart_items: List of screen items in cart
        on_remove: Callback to remove an item (receives index)
        on_apply_discount: Callback to apply discount (receives code)
        on_checkout: Callback to start checkout
        discount_code: Current discount code input
        applied_discount: Applied discount percentage
        is_checkout_ready: Whether checkout can proceed
        is_processing: Whether checkout is in progress
    """
    st.subheader("🛒 Campaign Cart")
    
    if not cart_items:
        st.info("Your campaign cart is empty. Add screens from the inventory to get started.")
        return
    
    # Cart items
    for i, item in enumerate(cart_items):
        render_cart_item(item, on_remove, i)
        if i < len(cart_items) - 1:
            st.divider()
    
    st.divider()
    
    # Calculate totals
    totals = calculate_totals(cart_items, applied_discount)
    
    # Totals display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Subtotal:**")
    with col2:
        st.markdown(f"**${totals['subtotal']/100:,.2f}**")
    
    if totals["discount"] > 0:
        with col1:
            st.markdown(f"*Discount ({totals['discount_percent']:.0f}%):*")
        with col2:
            st.markdown(f"*-${totals['discount']/100:,.2f}*")
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Total:")
    with col2:
        st.markdown(f"### ${totals['total']/100:,.2f}")
    
    st.divider()
    
    # Discount code input
    st.markdown("**Apply Discount Code:**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code = st.text_input(
            "Discount Code",
            value=discount_code,
            placeholder="Enter code (e.g., AGENCY15)",
            label_visibility="collapsed",
            key="discount_code_input"
        )
    with col2:
        if st.button("Apply", use_container_width=True, disabled=is_processing):
            if code:
                on_apply_discount(code)
    
    # Available codes hint
    with st.expander("💡 Available discount codes"):
        st.markdown("""
        - **LAUNCH20** - 20% Launch Discount
        - **BULK10** - 10% Multi-Screen Discount  
        - **AGENCY15** - 15% Agency Partner Discount
        - **FIRST500** - $500 First Campaign Credit
        """)
    
    st.divider()
    
    # Checkout button
    if st.button(
        "🛍️ Complete Checkout via UCP",
        type="primary",
        use_container_width=True,
        disabled=is_processing or len(cart_items) == 0
    ):
        on_checkout()
    
    if is_processing:
        st.info("Processing checkout... Watch the execution log below.")


def render_order_confirmation(order_data: dict):
    """
    Render the order confirmation.
    
    Args:
        order_data: Completed order data from UCP
    """
    st.success("🎉 Order Confirmed!")
    
    order = order_data.get("order", {})
    order_id = order.get("id", "N/A")
    
    st.markdown(f"""
    ### Order Details
    
    - **Order ID:** `{order_id}`
    - **Status:** {order_data.get('status', 'completed').upper()}
    - **Order URL:** {order.get('permalink_url', 'N/A')}
    """)
    
    # Line items
    st.markdown("### Campaign Screens")
    for item in order_data.get("line_items", []):
        item_total = item.get("totals", [{}])[-1].get("amount", 0)
        st.markdown(f"""
        - **{item['item']['title']}**
          - Duration: {item['quantity']} days
          - Total: ${item_total/100:,.2f}
        """)
    
    # Final total
    final_total = order_data.get("totals", [{}])[-1].get("amount", 0)
    st.markdown(f"### Final Total: ${final_total/100:,.2f}")
    
    st.balloons()

#!/usr/bin/env python3
"""
DOOH Screen Buying Demo - UCP Happy Path Client

This script demonstrates purchasing DOOH (Digital Out-of-Home) screen 
advertising inventory through the Universal Commerce Protocol (UCP).
"""

import logging
import uuid
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVER_URL = "http://localhost:8182"


def get_headers():
    """Generate fresh headers with unique idempotency key."""
    return {
        "Content-Type": "application/json",
        "UCP-Agent": 'profile="https://dooh-platform.example/profile"',
        "request-signature": "demo",
        "idempotency-key": str(uuid.uuid4()),
        "request-id": str(uuid.uuid4()),
    }


def main():
    """Run the DOOH checkout demo."""
    
    print("\n" + "="*60)
    print("   DOOH SCREEN BUYING DEMO - Universal Commerce Protocol")
    print("="*60 + "\n")
    
    with httpx.Client(timeout=30.0) as client:
        
        # STEP 0: Discovery
        logger.info("STEP 0: Discovering merchant capabilities...")
        response = client.get(f"{SERVER_URL}/.well-known/ucp")
        discovery = response.json()
        
        handlers = discovery.get("payment", {}).get("handlers", [])
        logger.info(f"Found {len(handlers)} payment handlers")
        for h in handlers:
            logger.info(f"  - {h['id']} ({h['name']})")
        
        # STEP 1: Create checkout with a Billboard
        logger.info("\n" + "-"*50)
        logger.info("STEP 1: Creating checkout with Times Square Billboard...")
        
        checkout_request = {
            "line_items": [
                {
                    "item": {
                        "id": "BB-NYC-001",
                        "title": "Times Square Digital Billboard #12"
                    },
                    "quantity": 7  # 7 days campaign
                }
            ],
            "buyer": {
                "full_name": "Sarah Johnson",
                "email": "sarah.johnson@mediaagency.com"
            },
            "currency": "USD",
            "payment": {
                "instruments": [],
                "handlers": handlers  # Pass discovered handlers
            }
        }
        
        response = client.post(
            f"{SERVER_URL}/checkout-sessions",
            json=checkout_request,
            headers=get_headers()
        )
        
        if response.status_code not in [200, 201]:
            logger.error(f"Failed to create checkout: {response.text}")
            return
            
        checkout = response.json()
        session_id = checkout["id"]
        
        total_cents = checkout.get("totals", [{}])[-1].get("amount", 0)
        logger.info(f"Checkout created: {session_id}")
        logger.info(f"Item: Times Square Billboard x 7 days")
        logger.info(f"Current Total: ${total_cents/100:,.2f}")
        
        # STEP 2: Add Transit Screen
        logger.info("\n" + "-"*50)
        logger.info("STEP 2: Adding Grand Central Transit Screen to campaign...")
        
        # Build update with existing items + new item
        line_items_update = []
        for item in checkout.get("line_items", []):
            line_items_update.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        # Add new screen
        line_items_update.append({
            "item": {
                "id": "TR-NYC-001",
                "title": "Grand Central Kiosk A"
            },
            "quantity": 7  # 7 days
        })
        
        update_request = {
            "id": session_id,
            "line_items": line_items_update,
            "currency": "USD",
            "payment": checkout.get("payment", {"instruments": [], "handlers": []})
        }
        
        response = client.put(
            f"{SERVER_URL}/checkout-sessions/{session_id}",
            json=update_request,
            headers=get_headers()
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to add items: {response.text}")
            return
            
        checkout = response.json()
        
        total_cents = checkout.get("totals", [{}])[-1].get("amount", 0)
        logger.info(f"Added: Grand Central Kiosk x 7 days")
        logger.info(f"New Total: ${total_cents/100:,.2f}")
        logger.info(f"Screens in campaign: {len(checkout.get('line_items', []))}")
        
        # STEP 3: Apply Agency Discount
        logger.info("\n" + "-"*50)
        logger.info("STEP 3: Applying AGENCY15 discount code...")
        
        # Build line items for update
        line_items_update = []
        for item in checkout.get("line_items", []):
            line_items_update.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        discount_request = {
            "id": session_id,
            "line_items": line_items_update,
            "currency": "USD",
            "payment": checkout.get("payment", {"instruments": [], "handlers": []}),
            "discounts": {
                "codes": ["AGENCY15"]
            }
        }
        
        response = client.put(
            f"{SERVER_URL}/checkout-sessions/{session_id}",
            json=discount_request,
            headers=get_headers()
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to apply discount: {response.text}")
            return
            
        checkout = response.json()
        
        total_cents = checkout.get("totals", [{}])[-1].get("amount", 0)
        discount_total = next(
            (t["amount"] for t in checkout.get("totals", []) if t["type"] == "discount"),
            0
        )
        
        applied = checkout.get("discounts", {}).get("applied", [])
        logger.info(f"Discount Applied: {[d['code'] for d in applied]}")
        logger.info(f"Discount Amount: ${discount_total/100:,.2f}")
        logger.info(f"New Total: ${total_cents/100:,.2f}")
        
        # STEP 4: Select Fulfillment (Instant Activation)
        logger.info("\n" + "-"*50)
        logger.info("STEP 4: Selecting fulfillment option...")
        
        # Build line items for update
        line_items_update = []
        for item in checkout.get("line_items", []):
            line_items_update.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        # Trigger fulfillment options
        fulfillment_request = {
            "id": session_id,
            "line_items": line_items_update,
            "currency": "USD",
            "payment": checkout.get("payment", {"instruments": [], "handlers": []}),
            "discounts": checkout.get("discounts"),
            "fulfillment": {
                "methods": [{"type": "shipping"}]
            }
        }
        
        response = client.put(
            f"{SERVER_URL}/checkout-sessions/{session_id}",
            json=fulfillment_request,
            headers=get_headers()
        )
        
        if response.status_code != 200:
            logger.warning(f"Fulfillment trigger: {response.status_code}")
        
        checkout = response.json()
        
        # Select destination if available
        fulfillment = checkout.get("fulfillment", {})
        methods = fulfillment.get("methods", [])
        
        if methods and methods[0].get("destinations"):
            dest_id = methods[0]["destinations"][0]["id"]
            logger.info(f"Selecting destination: {dest_id}")
            
            fulfillment_request["fulfillment"] = {
                "methods": [{"type": "shipping", "selected_destination_id": dest_id}]
            }
            
            response = client.put(
                f"{SERVER_URL}/checkout-sessions/{session_id}",
                json=fulfillment_request,
                headers=get_headers()
            )
            checkout = response.json()
            
            # Select shipping option
            methods = checkout.get("fulfillment", {}).get("methods", [])
            if methods and methods[0].get("groups"):
                groups = methods[0]["groups"]
                if groups and groups[0].get("options"):
                    option_id = groups[0]["options"][0]["id"]
                    logger.info(f"Selecting option: {option_id}")
                    
                    fulfillment_request["fulfillment"] = {
                        "methods": [{
                            "type": "shipping",
                            "selected_destination_id": dest_id,
                            "groups": [{"selected_option_id": option_id}]
                        }]
                    }
                    
                    response = client.put(
                        f"{SERVER_URL}/checkout-sessions/{session_id}",
                        json=fulfillment_request,
                        headers=get_headers()
                    )
                    checkout = response.json()
        
        logger.info("Fulfillment configured: Instant Digital Activation")
        
        # STEP 5: Complete Payment
        logger.info("\n" + "-"*50)
        logger.info("STEP 5: Processing payment...")
        
        complete_request = {
            "payment_data": {
                "id": "instr_dooh_card",
                "handler_id": "mock_payment_handler",
                "handler_name": "mock_payment_handler",
                "type": "card",
                "brand": "Visa",
                "last_digits": "4242",
                "credential": {
                    "type": "token",
                    "token": "success_token"
                },
                "billing_address": {
                    "street_address": "350 Fifth Avenue",
                    "address_locality": "New York",
                    "address_region": "NY",
                    "address_country": "US",
                    "postal_code": "10118"
                }
            },
            "risk_signals": {
                "ip": "127.0.0.1",
                "browser": "dooh-demo-client"
            }
        }
        
        response = client.post(
            f"{SERVER_URL}/checkout-sessions/{session_id}/complete",
            json=complete_request,
            headers=get_headers()
        )
        
        if response.status_code != 200:
            logger.error(f"Payment failed: {response.text}")
            return
            
        checkout = response.json()
        
        logger.info(f"Payment Status: {checkout.get('status', 'unknown')}")
        
        order = checkout.get("order", {})
        order_id = order.get("id", "N/A")
        order_url = order.get("permalink_url", "N/A")
        
        logger.info(f"Order ID: {order_id}")
        
        # Summary
        print("\n" + "="*60)
        print("   DOOH CAMPAIGN ORDER CONFIRMED!")
        print("="*60)
        print(f"\n  Order ID: {order_id}")
        print(f"  Status: {checkout.get('status')}")
        print(f"\n  Campaign Details:")
        
        for item in checkout.get("line_items", []):
            print(f"    - {item['item']['title']}")
            print(f"      Duration: {item['quantity']} days")
            item_total = item.get("totals", [{}])[-1].get("amount", 0)
            print(f"      Subtotal: ${item_total/100:,.2f}")
        
        final_total = checkout.get("totals", [{}])[-1].get("amount", 0)
        print(f"\n  Final Total: ${final_total/100:,.2f}")
        print(f"  Order URL: {order_url}")
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

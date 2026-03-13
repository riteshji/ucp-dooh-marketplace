"""
UCP Client with Logging Support for Streamlit UI

This client wraps UCP API calls and provides logging callbacks
for displaying execution steps in the UI. 
"""

import uuid
import httpx
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from datetime import datetime 


@dataclass
class LogEntry:
    """Represents a single log entry in the execution log."""
    step: int
    title: str
    method: str
    endpoint: str
    status: str  # "pending", "running", "success", "error"
    timestamp: datetime = field(default_factory=datetime.now)
    request_body: Optional[dict] = None
    response_body: Optional[dict] = None
    response_status: Optional[int] = None
    message: Optional[str] = None
    duration_ms: Optional[float] = None


class UCPClient:
    """UCP API Client with logging support."""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8182",
        on_log: Optional[Callable[[LogEntry], None]] = None
    ):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
        self.on_log = on_log
        self.step_counter = 0
        self.session_id: Optional[str] = None
        self.checkout_data: Optional[dict] = None
        self.discovery_data: Optional[dict] = None
        
    def _get_headers(self) -> dict:
        """Generate fresh headers with unique idempotency key."""
        return {
            "Content-Type": "application/json",
            "UCP-Agent": 'profile="https://dooh-platform.example/profile"',
            "request-signature": "demo",
            "idempotency-key": str(uuid.uuid4()),
            "request-id": str(uuid.uuid4()),
        }
    
    def _log(self, entry: LogEntry):
        """Send log entry to callback if registered."""
        if self.on_log:
            self.on_log(entry)
    
    def _next_step(self) -> int:
        """Increment and return the next step number."""
        self.step_counter += 1
        return self.step_counter
    
    def reset(self):
        """Reset the client state for a new checkout flow."""
        self.step_counter = 0
        self.session_id = None
        self.checkout_data = None
    
    def discover(self) -> dict:
        """
        Step 0: Discovery - Query merchant capabilities.
        """
        step = self._next_step()
        endpoint = "/.well-known/ucp"
        
        # Log start
        entry = LogEntry(
            step=step,
            title="Discovery - Query Merchant Capabilities",
            method="GET",
            endpoint=endpoint,
            status="running"
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.get(endpoint)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.discovery_data = response.json()
            handlers = self.discovery_data.get("payment", {}).get("handlers", [])
            
            entry.status = "success"
            entry.response_status = response.status_code
            entry.response_body = self.discovery_data
            entry.duration_ms = duration
            entry.message = f"Found {len(handlers)} payment handlers"
            self._log(entry)
            
            return self.discovery_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def create_checkout(self, screens: list[dict], buyer_name: str, buyer_email: str) -> dict:
        """
        Step 1: Create Checkout Session with selected screens.
        """
        step = self._next_step()
        endpoint = "/checkout-sessions"
        
        # Build line items from selected screens
        line_items = []
        for screen in screens:
            line_items.append({
                "item": {
                    "id": screen["id"],
                    "title": screen["title"]
                },
                "quantity": screen.get("days", 1)
            })
        
        # Get handlers from discovery
        handlers = self.discovery_data.get("payment", {}).get("handlers", []) if self.discovery_data else []
        
        payload = {
            "line_items": line_items,
            "buyer": {
                "full_name": buyer_name,
                "email": buyer_email
            },
            "currency": "USD",
            "payment": {
                "instruments": [],
                "handlers": handlers
            }
        }
        
        # Log start
        entry = LogEntry(
            step=step,
            title="Create Checkout Session",
            method="POST",
            endpoint=endpoint,
            status="running",
            request_body=payload
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.post(endpoint, json=payload, headers=self._get_headers())
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.checkout_data = response.json()
            self.session_id = self.checkout_data.get("id")
            
            total = self.checkout_data.get("totals", [{}])[-1].get("amount", 0)
            
            entry.status = "success" if response.status_code in [200, 201] else "error"
            entry.response_status = response.status_code
            entry.response_body = self.checkout_data
            entry.duration_ms = duration
            entry.message = f"Session: {self.session_id[:8]}... | Total: ${total/100:,.2f}"
            self._log(entry)
            
            return self.checkout_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def add_screen(self, screen: dict) -> dict:
        """
        Add a screen to the existing checkout session.
        """
        if not self.session_id or not self.checkout_data:
            raise ValueError("No active checkout session")
        
        step = self._next_step()
        endpoint = f"/checkout-sessions/{self.session_id}"
        
        # Build updated line items
        line_items = []
        for item in self.checkout_data.get("line_items", []):
            line_items.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        # Add new screen
        line_items.append({
            "item": {
                "id": screen["id"],
                "title": screen["title"]
            },
            "quantity": screen.get("days", 1)
        })
        
        payload = {
            "id": self.session_id,
            "line_items": line_items,
            "currency": "USD",
            "payment": self.checkout_data.get("payment", {"instruments": [], "handlers": []})
        }
        
        entry = LogEntry(
            step=step,
            title=f"Add Screen: {screen['title'][:30]}...",
            method="PUT",
            endpoint=endpoint,
            status="running",
            request_body=payload
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.put(endpoint, json=payload, headers=self._get_headers())
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.checkout_data = response.json()
            total = self.checkout_data.get("totals", [{}])[-1].get("amount", 0)
            item_count = len(self.checkout_data.get("line_items", []))
            
            entry.status = "success" if response.status_code == 200 else "error"
            entry.response_status = response.status_code
            entry.response_body = self.checkout_data
            entry.duration_ms = duration
            entry.message = f"{item_count} screens | Total: ${total/100:,.2f}"
            self._log(entry)
            
            return self.checkout_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def apply_discount(self, code: str) -> dict:
        """
        Apply a discount code to the checkout session.
        """
        if not self.session_id or not self.checkout_data:
            raise ValueError("No active checkout session")
        
        step = self._next_step()
        endpoint = f"/checkout-sessions/{self.session_id}"
        
        # Build line items
        line_items = []
        for item in self.checkout_data.get("line_items", []):
            line_items.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        payload = {
            "id": self.session_id,
            "line_items": line_items,
            "currency": "USD",
            "payment": self.checkout_data.get("payment", {"instruments": [], "handlers": []}),
            "discounts": {
                "codes": [code]
            }
        }
        
        entry = LogEntry(
            step=step,
            title=f"Apply Discount Code: {code}",
            method="PUT",
            endpoint=endpoint,
            status="running",
            request_body=payload
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.put(endpoint, json=payload, headers=self._get_headers())
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.checkout_data = response.json()
            
            applied = self.checkout_data.get("discounts", {}).get("applied", [])
            discount_amount = next(
                (t["amount"] for t in self.checkout_data.get("totals", []) if t["type"] == "discount"),
                0
            )
            total = self.checkout_data.get("totals", [{}])[-1].get("amount", 0)
            
            if applied:
                entry.status = "success"
                entry.message = f"Discount: -${discount_amount/100:,.2f} | New Total: ${total/100:,.2f}"
            else:
                entry.status = "error"
                entry.message = "Discount code not applied"
            
            entry.response_status = response.status_code
            entry.response_body = self.checkout_data
            entry.duration_ms = duration
            self._log(entry)
            
            return self.checkout_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def setup_fulfillment(self) -> dict:
        """
        Set up fulfillment options (digital delivery for DOOH).
        """
        if not self.session_id or not self.checkout_data:
            raise ValueError("No active checkout session")
        
        step = self._next_step()
        endpoint = f"/checkout-sessions/{self.session_id}"
        
        # Build line items
        line_items = []
        for item in self.checkout_data.get("line_items", []):
            line_items.append({
                "id": item["id"],
                "item": {"id": item["item"]["id"], "title": item["item"]["title"]},
                "quantity": item["quantity"]
            })
        
        # Step 1: Trigger fulfillment
        payload = {
            "id": self.session_id,
            "line_items": line_items,
            "currency": "USD",
            "payment": self.checkout_data.get("payment", {"instruments": [], "handlers": []}),
            "discounts": self.checkout_data.get("discounts"),
            "fulfillment": {
                "methods": [{"type": "shipping"}]
            }
        }
        
        entry = LogEntry(
            step=step,
            title="Configure Fulfillment (Digital Delivery)",
            method="PUT",
            endpoint=endpoint,
            status="running",
            request_body=payload
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.put(endpoint, json=payload, headers=self._get_headers())
            self.checkout_data = response.json()
            
            # Select destination if available
            methods = self.checkout_data.get("fulfillment", {}).get("methods", [])
            if methods and methods[0].get("destinations"):
                dest_id = methods[0]["destinations"][0]["id"]
                payload["fulfillment"] = {
                    "methods": [{"type": "shipping", "selected_destination_id": dest_id}]
                }
                response = self.client.put(endpoint, json=payload, headers=self._get_headers())
                self.checkout_data = response.json()
                
                # Select shipping option
                methods = self.checkout_data.get("fulfillment", {}).get("methods", [])
                if methods and methods[0].get("groups"):
                    groups = methods[0]["groups"]
                    if groups and groups[0].get("options"):
                        option_id = groups[0]["options"][0]["id"]
                        option_title = groups[0]["options"][0].get("title", "Instant Activation")
                        payload["fulfillment"] = {
                            "methods": [{
                                "type": "shipping",
                                "selected_destination_id": dest_id,
                                "groups": [{"selected_option_id": option_id}]
                            }]
                        }
                        response = self.client.put(endpoint, json=payload, headers=self._get_headers())
                        self.checkout_data = response.json()
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            entry.status = "success"
            entry.response_status = response.status_code
            entry.response_body = self.checkout_data
            entry.duration_ms = duration
            entry.message = "Fulfillment: Instant Digital Activation"
            self._log(entry)
            
            return self.checkout_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def complete_checkout(self) -> dict:
        """
        Complete the checkout with payment.
        """
        if not self.session_id:
            raise ValueError("No active checkout session")
        
        step = self._next_step()
        endpoint = f"/checkout-sessions/{self.session_id}/complete"
        
        payload = {
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
                "browser": "streamlit-dooh-demo"
            }
        }
        
        entry = LogEntry(
            step=step,
            title="Complete Checkout - Process Payment",
            method="POST",
            endpoint=endpoint,
            status="running",
            request_body=payload
        )
        self._log(entry)
        
        start_time = datetime.now()
        try:
            response = self.client.post(endpoint, json=payload, headers=self._get_headers())
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            self.checkout_data = response.json()
            
            order = self.checkout_data.get("order", {})
            order_id = order.get("id", "N/A")
            status = self.checkout_data.get("status", "unknown")
            
            entry.status = "success" if status == "completed" else "error"
            entry.response_status = response.status_code
            entry.response_body = self.checkout_data
            entry.duration_ms = duration
            entry.message = f"Order: {order_id[:8]}... | Status: {status}"
            self._log(entry)
            
            return self.checkout_data
            
        except Exception as e:
            entry.status = "error"
            entry.message = str(e)
            self._log(entry)
            raise
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()

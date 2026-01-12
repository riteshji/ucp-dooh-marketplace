# DOOH Screen Marketplace - Streamlit UI

A web-based demo for purchasing Digital Out-of-Home (DOOH) advertising screen inventory using the Universal Commerce Protocol (UCP).

## Features

- 📺 **Screen Browser** - Browse and filter DOOH screens by venue type, city, and price
- 🛒 **Shopping Cart** - Build multi-screen advertising campaigns
- 💰 **Discount Codes** - Apply promotional discounts
- 🗺️ **Map View** - See screen locations on an interactive map
- 📋 **Execution Log** - Watch UCP API calls in real-time with expandable request/response details

## Prerequisites

- Python 3.10+
- UCP Merchant Server running on `http://localhost:8182`
- DOOH product data imported (see main project README)

## Quick Start

1. **Ensure the UCP server is running:**
   ```bash
   cd samples/rest/python/server
   uv run server.py --products_db_path=<path>/products.db --transactions_db_path=<path>/transactions.db --port=8182
   ```

2. **Install UI dependencies:**
   ```bash
   cd ui
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser:** http://localhost:8501

## Usage

1. **Browse Screens** - Filter by venue type (Billboard, Transit, Retail, Airport), city, or max price
2. **Add to Campaign** - Select duration (days) and click "Add to Campaign"
3. **Apply Discount** - Enter a code like `AGENCY15` for 15% off
4. **Checkout** - Click "Complete Checkout via UCP" to execute the full UCP flow
5. **Watch the Log** - See each API call (Discovery, Create, Update, Complete) in real-time

## Available Discount Codes

| Code | Discount |
|------|----------|
| LAUNCH20 | 20% off |
| BULK10 | 10% off |
| AGENCY15 | 15% off |
| FIRST500 | $500 credit |

## Project Structure

```
ui/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── components/
│   ├── screen_browser.py     # Screen inventory display
│   ├── cart.py               # Shopping cart
│   ├── execution_log.py      # UCP API call log
│   └── map_view.py           # Map visualization
└── services/
    └── ucp_client.py         # UCP API client with logging
```

## Screenshots

### Screen Browser
Browse DOOH inventory with filters for venue type, city, and price.

### Execution Log
Watch UCP API calls execute in real-time with expandable request/response details.

### Map View
See screen locations across different cities.

## License

Apache 2.0

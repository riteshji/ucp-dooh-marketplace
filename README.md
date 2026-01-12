# UCP DOOH Marketplace

A sample implementation of a **Digital Out-of-Home (DOOH)** screen buying marketplace using the [Universal Commerce Protocol (UCP)](https://ucp.dev).

This project demonstrates how UCP can be applied to the digital advertising industry, enabling programmatic buying of billboard, transit, retail, and airport screen inventory.

## Features

- **Screen Inventory Browser** - Browse and filter DOOH screens by venue type, city, and price
- **Campaign Builder** - Build multi-screen advertising campaigns with duration selection
- **Discount System** - Apply promotional discount codes
- **Interactive Map** - View screen locations geographically
- **UCP Execution Log** - Watch UCP API calls execute in real-time with full request/response details
- **Complete Checkout Flow** - Full UCP checkout including discovery, session management, fulfillment, and payment

## Screenshots

### Screen Browser
Browse DOOH inventory with filters for venue type (Billboard, Transit, Retail, Airport), city, and maximum price per day.

### Execution Log
Watch each UCP API call as it happens - Discovery, Create Checkout, Apply Discount, Configure Fulfillment, Complete Payment.

## Quick Start

### Prerequisites

- Python 3.10+
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/riteshji/ucp-dooh-marketplace.git
   cd ucp-dooh-marketplace
   ```

2. **Clone the UCP Python SDK:**
   ```bash
   mkdir sdk
   git clone https://github.com/Universal-Commerce-Protocol/python-sdk.git sdk/python
   cd sdk/python && uv sync && cd ../..
   ```

3. **Set up the UCP server:**
   ```bash
   cd samples/rest/python/server
   uv sync
   ```

4. **Import DOOH product data:**
   ```bash
   uv run import_csv.py \
       --products_db_path=../../../../ucp_test/products.db \
       --transactions_db_path=../../../../ucp_test/transactions.db \
       --data_dir=../test_data/dooh_screens
   ```

5. **Start the UCP server:**
   ```bash
   uv run server.py \
       --products_db_path=../../../../ucp_test/products.db \
       --transactions_db_path=../../../../ucp_test/transactions.db \
       --port=8182
   ```

6. **In a new terminal, start the UI:**
   ```bash
   cd ui
   pip install -r requirements.txt
   streamlit run app.py
   ```

7. **Open http://localhost:8501** in your browser

## DOOH Screen Inventory

The demo includes 15 sample screens across 5 venue types:

| Type | Locations | Price Range |
|------|-----------|-------------|
| Billboard | NYC, LA, Chicago | $320-$500/day |
| Transit | NYC, Chicago, LAX | $150-$220/day |
| Retail | NYC, Miami, LA, SF | $60-$85/day |
| Airport | JFK, SFO, ORD | $180-$250/day |
| Gym | NYC | $50/day |

## Discount Codes

| Code | Discount |
|------|----------|
| LAUNCH20 | 20% off |
| BULK10 | 10% off |
| AGENCY15 | 15% off |
| FIRST500 | $500 credit |

## Project Structure

```
ucp-dooh-marketplace/
├── README.md
├── LICENSE                      # Apache 2.0
├── .gitignore
├── sdk/                         # UCP Python SDK (git submodule)
├── samples/
│   └── rest/
│       └── python/
│           ├── server/          # UCP Merchant Server
│           ├── client/
│           │   ├── flower_shop/ # Original sample
│           │   └── dooh_demo/   # DOOH demo client
│           └── test_data/
│               └── dooh_screens/ # DOOH product data
└── ui/                          # Streamlit UI
    ├── app.py                   # Main application
    ├── requirements.txt
    ├── components/              # UI components
    │   ├── screen_browser.py
    │   ├── cart.py
    │   ├── execution_log.py
    │   └── map_view.py
    └── services/
        └── ucp_client.py        # UCP client with logging
```

## UCP Checkout Flow

The demo implements the full UCP checkout flow:

1. **Discovery** (`GET /.well-known/ucp`) - Query merchant capabilities
2. **Create Checkout** (`POST /checkout-sessions`) - Start a checkout session
3. **Update Cart** (`PUT /checkout-sessions/{id}`) - Add screens, apply discounts
4. **Configure Fulfillment** (`PUT /checkout-sessions/{id}`) - Set delivery options
5. **Complete Payment** (`POST /checkout-sessions/{id}/complete`) - Process payment

## Technology Stack

- **Backend**: Python, FastAPI, SQLite
- **Frontend**: Streamlit
- **Protocol**: Universal Commerce Protocol (UCP)
- **Package Management**: uv

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Universal Commerce Protocol](https://ucp.dev) - The protocol specification
- [UCP Samples Repository](https://github.com/Universal-Commerce-Protocol/samples) - Original sample implementations
- [UCP Python SDK](https://github.com/Universal-Commerce-Protocol/python-sdk) - Python SDK

## Related Links

- [UCP Documentation](https://ucp.dev/documentation/)
- [UCP Specification](https://ucp.dev/specification/overview/)
- [UCP Playground](https://ucp.dev/playground/)

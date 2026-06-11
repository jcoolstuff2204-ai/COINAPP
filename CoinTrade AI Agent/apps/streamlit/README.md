# QuanTrade Streamlit Test Harness

This is a temporary hands-on testing path while the production React/FastAPI stack is still under construction.

It uses the same deterministic service layer as the API:

- Fixture scanner signal
- Signal explanation
- Fixture replay and order-book data health
- Paper order, position, portfolio, journal, and performance payloads

## Run

```bash
make streamlit
```

Default local URL: `http://localhost:8502`

If Streamlit is not installed yet:

```bash
python3 -m pip install --target .streamlit_deps streamlit
make streamlit
```

The harness is paper/demo only. It does not place live trades.

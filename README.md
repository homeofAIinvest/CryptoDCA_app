# CryptoDCA.ai — Deployable Starter Package

## Overview
This is a deploy-ready starter for the CryptoDCA.ai web app (simulation-only, AI model included). It contains a FastAPI backend and a React frontend with Vite.

## Local quickstart (Docker)
Requirements: Docker & Docker Compose

1. Extract this package to a folder.
2. Build and run:
   ```bash
   docker-compose up --build
   ```
3. Frontend: http://localhost:3000
   Backend: http://localhost:8000

## API
- `POST /signup` {email, password}
- `POST /login` {email, password} -> {access_token}
- `POST /simulate` Authorization: Bearer <token> {tickers:[], monthly:50, start:'2019-01-01'}

## Notes
- The backend uses CoinGecko when available; fallback to yfinance for price data.
- LightGBM is used if installed; otherwise RandomForest is used.
- This starter is for demo and educational purposes only. Replace secrets and configure a proper DB for production.

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from database import run_query

app = FastAPI(title="HNS Dashboard API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HNS Dashboard API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/branches")
async def get_branches():
    """Get list of branches from tblDefShops"""
    query = "SELECT shop_id AS Shop_id, shop_name AS Shop_name FROM tblDefShops WITH (NOLOCK) WHERE shop_id IS NOT NULL ORDER BY shop_name"
    try:
        df = run_query(query)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for future routes
from routers import auth, overview, qr_commission, chef_sales, order_takers, trends_analytics, ramzan_deals, category_coverage, material_cost, pivot, diagnostics, system
app.include_router(auth.router)
app.include_router(overview.router)
app.include_router(qr_commission.router)
app.include_router(chef_sales.router)
app.include_router(order_takers.router)
app.include_router(trends_analytics.router)
app.include_router(ramzan_deals.router)
app.include_router(category_coverage.router)
app.include_router(material_cost.router)
app.include_router(pivot.router)
app.include_router(diagnostics.router)
app.include_router(system.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

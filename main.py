from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MM Chart Data Series API",
    description="API to fetch chart data from external CHARTS_DATA_API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHARTS_DATA_API = os.getenv("CHARTS_DATA_API")

@app.get("/")
async def root():
    return {"message": "MM Chart Data Series API", "status": "running"}

@app.get("/series")
async def get_chart_data_series(chart_id: str):
    if not CHARTS_DATA_API:
        raise HTTPException(status_code=500, detail="CHARTS_DATA_API environment variable not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            chart_data_api = f'{CHARTS_DATA_API}/{chart_id}'
            print(chart_data_api)
            response = await client.get(chart_data_api)
            response.raise_for_status()
            series = response.json()['data'][f'c:{chart_id}']['series']
            return series
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "charts_api_configured": bool(CHARTS_DATA_API)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="FastAPI GitOps Starter",
    description="A starter template for learning GitOps with FastAPI",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", "/GitOps-Starter"),
)

ITEMS: dict[int, dict] = {
    1: {"id": 1, "name": "Item 1", "description": "First item"},
    2: {"id": 2, "name": "Item 2", "description": "Second item"},
    3: {"id": 3, "name": "Item 3", "description": "Third item"},
}


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to FastAPI GitOps Starter!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "fastapi-gitops-starter"},
    )


@app.get("/api/items")
async def list_items():
    """Example endpoint to list items."""
    return {"items": list(ITEMS.values())}


@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    """Example endpoint to get a specific item by ID."""
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return ITEMS[item_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

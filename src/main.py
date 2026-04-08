import uvicorn
from fastapi import FastAPI

from routers import categories_router, positions_router, stats_router, settings_router

app = FastAPI(title="Классификатор продуктов")

app.include_router(categories_router)
app.include_router(positions_router)
app.include_router(stats_router)
app.include_router(settings_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

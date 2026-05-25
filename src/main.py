import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import categories_router, positions_router, stats_router, settings_router, units_router, enum_router, parameters_router, category_parameters_router, position_parameters_router

app = FastAPI(title="Классификатор продуктов")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # или ["*"] для разработки
    allow_credentials=True,  # Важно для кук/авторизации
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Явно включаем OPTIONS
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Все нужные заголовки
)

app.include_router(categories_router)
app.include_router(positions_router)
app.include_router(stats_router)
app.include_router(settings_router)
app.include_router(units_router)
app.include_router(enum_router)
# app.include_router(position_enum_router)
app.include_router(parameters_router)
app.include_router(category_parameters_router)
app.include_router(position_parameters_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

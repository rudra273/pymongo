from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import items, clock_in

app = FastAPI(title="FastAPI MongoDB CRUD", description="API for managing Items and Clock-In Records")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(clock_in.router, prefix="/clock-in", tags=["Clock-In"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

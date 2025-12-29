from fastapi import FastAPI
from app.api.v1 import schools, students, invoices, payments, statements
from app.config import settings
from app.infrastructure.logging import setup_logging
from app.exceptions import AppException, app_exception_handler

setup_logging(log_level=settings.LOG_LEVEL)

app = FastAPI(
    title="Mattilda Billing API",
    description="Sistema de facturación escolar",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(schools.router, prefix=settings.API_V1_PREFIX)
app.include_router(students.router, prefix=settings.API_V1_PREFIX)
app.include_router(invoices.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(statements.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok"}


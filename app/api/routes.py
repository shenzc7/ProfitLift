"""FastAPI route definitions for ProfitLift."""

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.models import (
    BundleResponse,
    MaintenanceActionRequest,
    MaintenanceActionResponse,
    MaintenanceSnapshot,
    RuleFilter,
    RuleResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.api.services import AnalyticsService, get_analytics_service

router = APIRouter()


@router.post(
    "/api/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload a CSV dataset for processing",
)
async def upload_dataset(
    file: UploadFile = File(...),
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict:
    """Upload transactions CSV and populate the ProfitLift dataset."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    try:
        result = await service.import_csv(file)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "rows_imported": result.rows_imported,
        "rejected_rows": result.rejected_rows,
        "items_created": result.items_created,
        "transactions_created": result.transactions_created,
        "errors": result.errors,
    }


@router.get(
    "/api/rules",
    response_model=List[RuleResponse],
    summary="Retrieve context-aware association rules",
)
def get_rules(
    filters: RuleFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[RuleResponse]:
    """Return scored association rules with plain-English explanations."""
    try:
        return service.get_rules(filters)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/api/bundles",
    response_model=List[BundleResponse],
    summary="Retrieve bundle recommendations",
)
def get_bundles(
    filters: RuleFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[BundleResponse]:
    """Return bundle recommendations derived from top rules."""
    try:
        return service.get_bundles(filters)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/api/whatif",
    response_model=WhatIfResponse,
    summary="Simulate a what-if promotion scenario",
)
def run_what_if(
    request: WhatIfRequest,
    service: AnalyticsService = Depends(get_analytics_service),
) -> WhatIfResponse:
    """Simulate an upcoming promotion window using causal uplift estimates."""
    try:
        return service.simulate_what_if(request)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/api/stats",
    summary="Retrieve dashboard statistics",
)
def get_stats(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict:
    """Return real calculated statistics for the dashboard."""
    try:
        return service.get_stats()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/api/settings/overview",
    response_model=MaintenanceSnapshot,
    summary="Operational snapshot for the Settings view",
)
def get_settings_overview(
    service: AnalyticsService = Depends(get_analytics_service),
) -> MaintenanceSnapshot:
    """Return backend status, table counts, and cache info."""
    try:
        return service.get_system_overview()
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/api/settings/clear",
    response_model=MaintenanceActionResponse,
    summary="Clear cached rules, bundles, or ingested data",
)
def clear_data(
    request: MaintenanceActionRequest,
    service: AnalyticsService = Depends(get_analytics_service),
) -> MaintenanceActionResponse:
    """Clear cached rule mining results and optionally uploaded CSV data."""
    try:
        return service.clear_data(request)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc

"""Tools info API router."""

from fastapi import APIRouter
from ..schemas import ToolInfo
from ..tool_adapters import get_all_adapters

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("/", response_model=list[ToolInfo])
def list_tools():
    adapters = get_all_adapters()
    return [a.info() for a in adapters.values()]


@router.get("/{tool_name}", response_model=ToolInfo)
def get_tool(tool_name: str):
    adapters = get_all_adapters()
    adapter = adapters.get(tool_name)
    if not adapter:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    return adapter.info()

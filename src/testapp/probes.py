from fastapi import APIRouter, HTTPException

router = APIRouter()

probes = {
    "health": True,
    "ready": True,
    "startup": True,
}


@router.get("/probe/{probe_name}")
async def probe(probe_name: str):
    if probe_name not in probes:
        raise HTTPException(status_code=404, detail="Probe not found")

    if not probes[probe_name]:
        raise HTTPException(status_code=500, detail="Probe is false")
    return probes[probe_name]


@router.post("/probe/{probe_name}/set")
async def probe_set(probe_name: str):
    if probe_name not in probes:
        raise HTTPException(status_code=404, detail="Probe not found")

    probes[probe_name] = True

    return probes[probe_name]


@router.post("/probe/{probe_name}/unset")
async def probe_unset(probe_name: str):
    if probe_name not in probes:
        raise HTTPException(status_code=404, detail="Probe not found")

    probes[probe_name] = False

    return probes[probe_name]

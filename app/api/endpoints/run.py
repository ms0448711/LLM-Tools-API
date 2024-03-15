from fastapi import APIRouter
from app.schemas.funcs import RunRequest, RunResponse
import subprocess
router = APIRouter()

@router.post("/run",response_model=RunResponse)
def run_func(req_body:RunRequest):
    if req_body.tool_name.lower() not in ["shell","python"]:
        raise Exception("The tool you specified do not support.")
    if req_body.tool_name.lower()=="shell":
        result=subprocess.check_output(req_body.command+"; exit 0",stderr=subprocess.STDOUT,shell=True);
    elif req_body.tool_name.lower()=="python":
        result=subprocess.check_output("python -c '"+req_body.command+"'; exit 0",stderr=subprocess.STDOUT,shell=True)
    return RunResponse(result=result,tool_name=req_body.tool_name.capitalize());
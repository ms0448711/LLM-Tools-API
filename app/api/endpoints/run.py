from fastapi import APIRouter
from app.schemas.funcs import RunRequest, RunResponse
import subprocess
from pathlib import Path
from datetime import datetime
import uuid
import time
router = APIRouter()

@router.post("/run",response_model=RunResponse)
def run_func(req_body:RunRequest):
    if req_body.tool_name.lower() not in ["shell","python"]:
        raise Exception("The tool you specified do not support.")
    try:
        if req_body.tool_name.lower()=="shell":
            result=subprocess.check_output(req_body.command+"; exit 0",stderr=subprocess.STDOUT,shell=True);
        elif req_body.tool_name.lower()=="python":
            script_name=str(datetime.now().strftime('%Y%m%d%H%M')) + '-' + str(uuid.uuid4())[:8] + '.py'
            fp=Path('./python_scripts')/script_name
            with open(fp,'w') as f:
                f.write(req_body.command)
            result=subprocess.check_output("python "+fp.__str__()+"; exit 0",stderr=subprocess.STDOUT,shell=True)
            subprocess.check_output(f"rm {fp};exit 0",stderr=subprocess.STDOUT,shell=True)
    except subprocess.CalledProcessError as e:
        result=e.output

    return RunResponse(result=result,tool_name=req_body.tool_name.capitalize());

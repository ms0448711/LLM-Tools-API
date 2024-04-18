from fastapi import APIRouter
from app.schemas.run import RunRequest, RunResponse
from app.schemas.run_shell import RunShellRequest,RunShellResponse
from app.schemas.clean_session import CleanSessionRequest, CleanSessionResponse
from app.schemas.run_python import RunPythonRequest,RunPythonResponse
import subprocess
from pathlib import Path
from datetime import datetime
import uuid
from app.utils import run_cmd,RunCmd
from app.utils import create_python_file, remove_file, check_bash

router = APIRouter()

@router.post("/run",response_model=RunResponse)
def run(req_body:RunRequest):
    if req_body.tool_name.lower() not in ["shell","python"]:
        raise Exception("The tool you specified do not support.")
    try:
        if req_body.tool_name.lower()=="shell":
            result=subprocess.check_output(rf"{req_body.command}; exit 0",stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True);
        elif req_body.tool_name.lower()=="python":
            fp=create_python_file(req_body.command)
            result=subprocess.check_output(rf"python {fp.__str__()}; exit 0",stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True,text=True)
            remove_file(fp)
    except subprocess.CalledProcessError as e:
        result=e.output

    return RunResponse(result=result,tool_name=req_body.tool_name.capitalize());

@router.post("/run_shell", response_model=RunShellResponse)
def run_shell(req_body:RunShellRequest):
    check_res=check_bash(req_body.command)
    if check_res:
        RunShellResponse(result="Command has encounter following error: "+check_res, session_id=req_body.session_id)
    stdout,stderr= run_cmd(RunCmd(
        session_id=req_body.session_id,
        command=req_body.command,
        output=req_body.output,
        keyword=req_body.keyword,
        timeout=req_body.timeout,
        ))
    return RunShellResponse(result=stdout+'\n'+stderr,session_id=req_body.session_id)

@router.post("/run_python", response_model=RunPythonResponse)
def run_python(req_body:RunPythonRequest):
    fp=create_python_file(req_body.script)
    stdout,stderr = run_cmd(RunCmd(
        session_id=req_body.session_id,
        command=rf"python {fp}",
        output=req_body.output,
        keyword=req_body.keyword,
        timeout=req_body.timeout,
        ))
    remove_file(fp)
    return RunPythonResponse(result=stdout+'\n'+stderr,session_id=req_body.session_id)

@router.post("/clean_session",response_model=CleanSessionResponse)
def clean_session(req_body:CleanSessionRequest):
    try:
        result=subprocess.check_output("tmux ls -f '#{m:"+req_body.prefix+"*,#{session_name}}' -F '#{session_name}'",shell=True,stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,text=True)
        result=str(result).split('\n')
        result.remove('')
        subprocess.run("tmux ls -f '#{m:"+req_body.prefix+"*,#{session_name}}' -F '#{session_name}' | xargs -r -n 1 tmux kill-session -t; exit 0",shell=True)
    except:
        result=[]
    return CleanSessionResponse(result=result)


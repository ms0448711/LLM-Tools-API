from fastapi import APIRouter
from app.schemas.run import RunRequest, RunResponse
from app.schemas.run_shell import RunShellRequest,RunShellResponse
import subprocess
from pathlib import Path
from datetime import datetime
import uuid
import random
import time
import concurrent.futures
router = APIRouter()

@router.post("/run",response_model=RunResponse)
def run(req_body:RunRequest):
    if req_body.tool_name.lower() not in ["shell","python"]:
        raise Exception("The tool you specified do not support.")
    try:
        if req_body.tool_name.lower()=="shell":
            result=subprocess.check_output(req_body.command+"; exit 0",stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True);
        elif req_body.tool_name.lower()=="python":
            script_name=str(datetime.now().strftime('%Y%m%d%H%M')) + '-' + str(uuid.uuid4())[:8] + '.py'
            fp=Path('./python_scripts')/script_name
            with open(fp,'w') as f:
                f.write(req_body.command)
            result=subprocess.check_output("python "+fp.__str__()+"; exit 0",stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True)
            subprocess.check_output(f"rm {fp};exit 0",stderr=subprocess.STDOUT,shell=True)
    except subprocess.CalledProcessError as e:
        result=e.output

    return RunResponse(result=result,tool_name=req_body.tool_name.capitalize());

@router.post("/run_shell", response_model=RunShellResponse)
def run_shell(req_body:RunShellRequest):
    tmp_pipe_fp=str(datetime.now().strftime('%Y%m%d%H%M')) + '-' + str(uuid.uuid4())[:8] + '.pipe'
    tmp_pipe_fp=Path('/tmp')/tmp_pipe_fp

    subprocess.run(f"tmux new -A -s {req_body.session_id} \; detach",shell=True)
    subprocess.run(f"rm -f {tmp_pipe_fp} && mkfifo {tmp_pipe_fp} && tmux pipe-pane -t {req_body.session_id} -o 'cat >{tmp_pipe_fp}'",shell=True)

    stop_with_keyword_fp = Path('shell_scripts')/"stop_with_keywords.sh"
    keyword=random.randint(1e9,1e10-1)
    a=random.randint(1e8,1e9-1)
    b=keyword-a
    time.sleep(1)
    proc=subprocess.Popen(f"cat {tmp_pipe_fp} |sh {stop_with_keyword_fp} {keyword}",stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(proc.communicate)
        subprocess.run(f"tmux send-keys -t {req_body.session_id} C-m",shell=True)
        subprocess.run(f"tmux send-keys -t {req_body.session_id} '{req_body.command}' '; echo $(({a}+{b}))' C-m", shell=True)
        subprocess.run(f"tmux send-keys -t {req_body.session_id} C-m",shell=True)
        stdout, stderr = future.result()
    subprocess.run(f"rm -f {tmp_pipe_fp}",shell=True)
    
    return RunShellResponse(result=stdout,session_id=req_body.session_id)
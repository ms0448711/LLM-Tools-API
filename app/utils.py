import subprocess
from pathlib import Path
from datetime import datetime
import uuid
import random
import time
from pydantic import BaseModel
from typing import Optional
import re

class RunCmd(BaseModel):
    session_id:str
    command:str
    output:bool
    keyword:Optional[str]
    timeout:int
    use_echo_stop:bool=True

whoami=subprocess.check_output('whoami',text=True)
whoami=re.sub('\s','',whoami)
hostname=subprocess.check_output('hostname',text=True)
hostname=re.sub('\s','',hostname)


def clean_output(x):
    res=re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]','',x)
    res=re.sub(rf"{whoami}.{hostname}",'',res)
    return res

def split_command(command):
    res=[""]
    for ac in command:
        if ac=="'":
            res.append("'")
            res.append("")
        else:
            res[-1]+=ac
    if res[-1]=="":del res[-1]
    return res

def create_python_file(script:str)->str:
    return create_file(script=script, ext='.py', directory='./python_scripts')

def create_shell_file(script:str)->str:
    return create_file(script=script, ext='.sh',directory='./shell_scripts')

def create_file(script:str, ext:str, directory:str)->str:
    script_name=str(datetime.now().strftime('%Y%m%d%H%M')) + '-' + str(uuid.uuid4())[:8] + ext
    fp=Path(directory)/script_name
    with open(fp,'w') as f:
        f.write(script)
    return fp.absolute()

def remove_file(fp):
    subprocess.check_output(rf"rm -f {fp};exit 0",stderr=subprocess.STDOUT,shell=True)

def check_bash(script:str):
    fp=create_shell_file(script)
    res = subprocess.check_output(rf"bash -n {fp}", shell=True)
    remove_file(fp)
    return res

def run_cmd(args:RunCmd):
    print(args.json())
    tmp_pipe_fp=str(datetime.now().strftime('%Y%m%d%H%M')) + '-' + str(uuid.uuid4())[:8] + '.pipe'
    tmp_pipe_fp=Path('/tmp')/tmp_pipe_fp

    subprocess.run(rf"tmux new -A -s '{args.session_id}' \; detach",shell=True)
    subprocess.run(f"tmux pipe-pane -t {args.session_id} -o ''", shell=True)
    subprocess.run(f"rm -f {tmp_pipe_fp} ; mkfifo {tmp_pipe_fp} && tmux pipe-pane -t {args.session_id} -o 'cat >{tmp_pipe_fp}'",shell=True)

    stop_with_keyword_fp = Path('shell_scripts')/"stop_with_keywords.sh"

    keyword=""
    echo_str=""
    if args.output:
        if args.keyword:
            keyword=args.keyword
            echo_str=""
        elif args.use_echo_stop:
            keyword=random.randint(1e9,1e10-1)
            a=random.randint(1e8,1e9-1)
            b=keyword-a
            echo_str=f"; echo $(({a}+{b}))"
        
    time.sleep(1)

    proc=subprocess.Popen(rf"bash {stop_with_keyword_fp} {tmp_pipe_fp} '{keyword}' {args.timeout}",stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True,text=True)
    subprocess.run(f"tmux send-keys -t {args.session_id} Enter",shell=True)
    # Run Command
    for cmd in split_command(args.command):
        if cmd=="'":
            subprocess.run(rf'tmux send-keys -t {args.session_id} "{cmd}"', shell=True)
        else:
            subprocess.run(rf"tmux send-keys -t {args.session_id} '{cmd}'", shell=True)
        time.sleep(1)


    subprocess.run(rf"tmux send-keys -t {args.session_id} '{echo_str}' Enter", shell=True)

    subprocess.run(f"tmux send-keys -t {args.session_id} Enter",shell=True)
    stdout, stderr = proc.communicate()
    subprocess.run(f"rm -f {tmp_pipe_fp}",shell=True)
    #remove reducdant words
    if echo_str:
        for rw in [args.command, echo_str,str(keyword),'\r']:
            stdout=stdout.replace(rw,'')
            stderr=stderr.replace(rw,'')
    stdout=clean_output(stdout)
    stderr=clean_output(stderr)
    return stdout, stderr
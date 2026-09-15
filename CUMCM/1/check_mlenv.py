# -*- coding: utf-8 -*-
import subprocess

for env in [r"D:\Applications\Anaconda3\envs\ml_env\python.exe",
            r"D:\Applications\Anaconda3\envs\paddle_env\python.exe"]:
    code = "import paddle, numpy; print(paddle.__version__, numpy.__version__, paddle.device.is_compiled_with_cuda())"
    r = subprocess.run([env, "-c", code], capture_output=True, text=True)
    print(env.split("envs")[-1], "->", (r.stdout or r.stderr).strip().splitlines()[-1][:120])

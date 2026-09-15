# Wait for papers to finish transferring, then launch batch OCR with CUDA DLLs on PATH.
Get-Process | Where-Object { $_.ProcessName -eq 'python' } | ForEach-Object {
    try { if ((Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine -match 'batch_ocr') { Stop-Process -Id $_.Id -Force } } catch {}
}
$deadline = (Get-Date).AddMinutes(90)
while (-not (Test-Path 'D:\CUMCM\_shared\papers\all\优秀论文')) {
    if ((Get-Date) -gt $deadline) { exit 1 }
    Start-Sleep -Seconds 10
}
$env:PATH = 'D:\Applications\Anaconda3\envs\paddle_env\Library\bin;D:\Applications\Anaconda3\envs\batcnn\Lib\site-packages\torch\lib;' + $env:PATH
Start-Process -FilePath 'D:\Applications\Anaconda3\envs\ml_env\python.exe' `
  -ArgumentList 'D:\CUMCM\_shared\papers\batch_ocr.py' `
  -WindowStyle Hidden `
  -RedirectStandardOutput 'D:\CUMCM\_shared\papers\ocr.log' `
  -RedirectStandardError 'D:\CUMCM\_shared\papers\ocr_err.log'
Write-Output 'relaunched'

# Launch OCR via Win32_Process.Create -> child of WmiPrvSE service, survives SSH session death.
$py = 'D:\Applications\Anaconda3\envs\ml_env\python.exe'
$cudnn = 'D:\Applications\Anaconda3\envs\paddle_env\Library\bin'
$zlib = 'D:\Applications\Anaconda3\envs\batcnn\Lib\site-packages\torch\lib'
$script = 'D:\CUMCM\_shared\papers\batch_ocr.py'
$log = 'D:\CUMCM\_shared\papers\ocr.log'
$cmdline = 'cmd /c "set PATH=' + $cudnn + ';' + $zlib + ';%PATH% && ' + $py + ' -u ' + $script + ' >> ' + $log + ' 2>&1"'
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmdline }
Write-Output ("ReturnValue=" + $r.ReturnValue + " Pid=" + $r.ProcessId)

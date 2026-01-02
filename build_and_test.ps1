# 1. Start main.py in the background
$process = Start-Process python -ArgumentList "main.py" -PassThru
Write-Host "Started main.py with PID: $($process.Id). Waiting 10 seconds to check for errors..."

# 2. Wait for 10 seconds
Start-Sleep -Seconds 10

# 3. Check if the process is still running
$runningProcess = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
if ($runningProcess) {
    Write-Host "main.py is still running. Assuming it's working correctly."
    Write-Host "Stopping main.py before building the executable..."
    Stop-Process -Id $process.Id -Force

    # Force kill any lingering main.exe processes
    Write-Host "Forcefully terminating any lingering main.exe processes..."
    taskkill /F /IM main.exe | Out-Null

    # 4. Generate the .exe
    Write-Host "Generating the executable..."
    python -m PyInstaller --onefile --noconsole main.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller failed. Please check the output."
        exit 1
    }

    # 5. Ask the user to check functionality
    Write-Host "Executable 'dist/main.exe' created successfully."
    Write-Host "Please run the executable and check if all functionalities are working as expected."

} else {
    Write-Error "main.py seems to have crashed within 10 seconds. Build aborted."
    Write-Error "Please run 'python main.py' manually to debug the issue."
    exit 1
}
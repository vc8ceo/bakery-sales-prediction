$boundary = [System.Guid]::NewGuid().ToString()
$filePath = "D:\Projects\bakery-sales-prediction\data\raw\airmate_rawdata_seiseki_201912-202506.csv"
$fileName = "data.csv"

$bodyTemplate = @"
--{0}
Content-Disposition: form-data; name="file"; filename="{1}"
Content-Type: application/octet-stream

{2}
--{0}--
"@

$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileContent = [System.Text.Encoding]::UTF8.GetString($fileBytes)

$body = $bodyTemplate -f $boundary, $fileName, $fileContent

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/upload-data" -Method POST -Body $body -ContentType "multipart/form-data; boundary=$boundary"
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Error Response: $($reader.ReadToEnd())"
    }
}

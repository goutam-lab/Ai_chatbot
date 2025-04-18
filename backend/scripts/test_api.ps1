# Test the chat API endpoint
function Test-ChatAPI {
    param (
        [string]$Message = "Top restaurants in Andheri"
    )

    Write-Host "Testing chat API with message: '$Message'`n"

    try {
        $body = @{
            message = $Message
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
        
        Write-Host "Response received:"
        Write-Host "-----------------"
        $response
        Write-Host "-----------------`n"

        # Additional verification
        if ($response.response) {
            Write-Host "Response contains restaurant information:"
            Write-Host "- Contains 'restaurant': $($response.response -match 'restaurant')"
            Write-Host "- Contains 'rating': $($response.response -match 'rating')"
            Write-Host "- Contains 'cuisine': $($response.response -match 'cuisine')"
        }
    }
    catch {
        Write-Host "Error occurred:"
        Write-Host $_.Exception.Message
    }
}

# Run the test
Test-ChatAPI 
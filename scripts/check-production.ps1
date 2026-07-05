param(
    [string]$ApiUrl = "",
    [string]$SiteUrl = "https://11fec3bf.deepstructureai.pages.dev",
    [switch]$RunTests,
    [switch]$RunBuild
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param(
        [string]$Step,
        [string]$Status,
        [string]$Detail
    )

    $results.Add([pscustomobject]@{
        Step = $Step
        Status = $Status
        Detail = $Detail
    })
}

function Test-HttpJson {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
    )

    $headers = @{ "Content-Type" = "application/json" }
    if ($Body -ne $null) {
        return Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers -Body ($Body | ConvertTo-Json -Depth 8)
    }

    return Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers
}

function Test-HttpStatus {
    param([string]$Url)

    Add-Type -AssemblyName System.Net.Http
    $client = [System.Net.Http.HttpClient]::new()
    try {
        $response = $client.GetAsync($Url).GetAwaiter().GetResult()
        return [int]$response.StatusCode
    } finally {
        $client.Dispose()
    }
}

try {
    $gitStatus = git status --short
    if ($gitStatus) {
        Add-Result "repo" "warn" "Há mudanças locais não commitadas."
    } else {
        Add-Result "repo" "pass" "Worktree limpo."
    }
} catch {
    Add-Result "repo" "warn" "Não foi possível verificar Git: $($_.Exception.Message)"
}

if ($RunTests) {
    try {
        Push-Location backend
        & .\.venv\Scripts\python.exe -m pytest tests
        Pop-Location
        Add-Result "backend-tests" "pass" "Pytest passou."
    } catch {
        Pop-Location
        Add-Result "backend-tests" "fail" $_.Exception.Message
    }
} else {
    Add-Result "backend-tests" "skip" "Use -RunTests para executar."
}

if ($RunBuild) {
    try {
        Push-Location frontend
        & "C:\Program Files\nodejs\npm.cmd" run build
        Pop-Location
        Add-Result "frontend-build" "pass" "Build Vite passou."
    } catch {
        Pop-Location
        Add-Result "frontend-build" "fail" $_.Exception.Message
    }
} else {
    Add-Result "frontend-build" "skip" "Use -RunBuild para executar."
}

if ($ApiUrl) {
    $ApiUrl = $ApiUrl.TrimEnd("/")
    try {
        $health = Test-HttpJson "$ApiUrl/api/health"
        Add-Result "api-health" "pass" "Status: $($health.status)"
    } catch {
        Add-Result "api-health" "fail" $_.Exception.Message
    }

    try {
        $readiness = Test-HttpJson "$ApiUrl/api/readiness"
        $warnings = if ($readiness.warnings.Count) { $readiness.warnings -join ", " } else { "sem avisos" }
        Add-Result "api-readiness" "pass" "Status: $($readiness.status); $warnings"
    } catch {
        Add-Result "api-readiness" "fail" $_.Exception.Message
    }

    try {
        $router = Test-HttpJson "$ApiUrl/api/router/status"
        Add-Result "router" "pass" "Rotas: $(@($router.activeRoutes.PSObject.Properties.Name).Count)"
    } catch {
        Add-Result "router" "fail" $_.Exception.Message
    }

    try {
        $chat = Test-HttpJson "$ApiUrl/api/chat" "POST" @{
            message = "Responda apenas: ok"
            mode = "fast"
            model = "auto"
        }
        Add-Result "chat" "pass" "Modelo usado: $($chat.model)"
    } catch {
        Add-Result "chat" "fail" $_.Exception.Message
    }
} else {
    Add-Result "api-online" "warn" "Informe -ApiUrl depois de hospedar o backend."
}

if ($SiteUrl) {
    try {
        $statusCode = Test-HttpStatus $SiteUrl
        if ($statusCode -ge 400) {
            Add-Result "site" "fail" "HTTP ${statusCode}: $SiteUrl"
        } else {
            Add-Result "site" "pass" "HTTP ${statusCode}: $SiteUrl"
        }
    } catch {
        Add-Result "site" "warn" "Não foi possível verificar via PowerShell: $($_.Exception.Message)"
    }
}

Add-Result "secrets" "manual" "Configurar ZAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY e DEEPSEEK_API_KEY no provedor do backend."
Add-Result "cloudflare" "manual" "Configurar VITE_API_URL e VITE_DEMO_MODE=false no Cloudflare Pages quando a API estiver online."

$results | Format-Table -AutoSize

if ($results.Status -contains "fail") {
    exit 1
}

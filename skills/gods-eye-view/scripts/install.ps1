# God's Eye View 설치 + Claude Code MCP 등록 (Windows PowerShell)
$ErrorActionPreference = 'Stop'

$GevDir   = if ($env:GEV_DIR)   { $env:GEV_DIR }   else { Join-Path $HOME 'gods-eye-view' }
$GevPort  = if ($env:GEV_PORT)  { $env:GEV_PORT }  else { '4173' }
$GevScope = if ($env:GEV_SCOPE) { $env:GEV_SCOPE } else { 'user' }
$Repo     = 'https://github.com/bilawalsidhu/gods-eye-view.git'

function Say($m)  { Write-Host "==> $m" -ForegroundColor Cyan }
function Fail($m) { Write-Host "오류: $m" -ForegroundColor Red; exit 1 }

Say '1/5 필수 도구 확인'
foreach ($c in 'git', 'node', 'npm', 'claude') {
  if (-not (Get-Command $c -ErrorAction SilentlyContinue)) { Fail "'$c' 를 찾을 수 없습니다. 먼저 설치하세요." }
}
$v = [version](node -p 'process.versions.node')
$ok = ($v.Major -eq 26) -or ($v.Major -eq 24 -and $v.Minor -ge 14)
if (-not $ok) { Fail "Node $v 는 지원되지 않습니다 (24.14 이상 24.x 또는 26.x 필요). nvm-windows/fnm 으로 Node 24 를 설치하세요." }
Write-Host "Node $v OK"

Say "2/5 소스 준비: $GevDir"
if (Test-Path (Join-Path $GevDir '.git')) {
  git -C $GevDir pull --ff-only
} elseif ((Test-Path $GevDir) -and (Get-ChildItem $GevDir -Force | Select-Object -First 1)) {
  Fail "$GevDir 가 비어 있지 않은 다른 폴더입니다. GEV_DIR 로 다른 위치를 지정하세요."
} else {
  git clone --depth 1 $Repo $GevDir
}
if ($LASTEXITCODE -ne 0) { Fail 'git 단계가 실패했습니다.' }

Say '3/5 의존성 설치 (npm ci)'
Push-Location $GevDir
try { npm ci; if ($LASTEXITCODE -ne 0) { Fail 'npm ci 가 실패했습니다.' } } finally { Pop-Location }

Say "4/5 Claude Code MCP 등록 (scope: $GevScope)"
$stdio = Join-Path $GevDir 'server\mcp\stdio.js'
claude mcp remove gods-eye-view --scope $GevScope 2>$null | Out-Null
claude mcp add --scope $GevScope gods-eye-view -- node $stdio --api-base "http://localhost:$GevPort"
if ($LASTEXITCODE -ne 0) { Fail 'claude mcp add 가 실패했습니다.' }

Say '5/5 완료'
@"

사용 방법
  1) PowerShell 하나에서 앱을 켜 둡니다 (끄지 마세요):
       cd "$GevDir"; npm run dev
  2) Claude Code 를 새로 시작합니다.
  3) 물어보세요:  Show San Diego in God's Eye View with military flights on.
  4) 지구본은 http://localhost:$GevPort 에서 봅니다.

점검:  claude mcp list   (gods-eye-view 가 Connected 인지 확인)
"@ | Write-Host

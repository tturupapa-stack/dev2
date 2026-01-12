# Git 커밋 메시지 한글 깨짐 수정 스크립트
$ErrorActionPreference = "Stop"

# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# Git 설정 확인
Write-Host "Git 인코딩 설정 확인 중..." -ForegroundColor Yellow
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.quotepath false

# 최근 커밋들의 올바른 메시지 매핑
$commitFixes = @{
    "84626a8" = "fix: .gitignore merge conflict 해결"
    "fff7276" = "fix: README.md 한글 인코딩 문제 해결 (UTF-8)"
    "a39a493" = "docs: 프롬프트 파일에 구현 완료 요약 추가"
    "b247599" = "docs: 영양성분 DB 통합 구현 완료 보고서 작성"
}

Write-Host "커밋 메시지 수정을 위해 rebase를 시작합니다..." -ForegroundColor Yellow
Write-Host "주의: 이미 푸시된 커밋을 수정하려면 force push가 필요합니다." -ForegroundColor Red

# 각 커밋을 개별적으로 수정
foreach ($hash in $commitFixes.Keys) {
    $message = $commitFixes[$hash]
    Write-Host "커밋 $hash 수정 중: $message" -ForegroundColor Cyan
    
    # 커밋이 존재하는지 확인
    $exists = git rev-parse --verify $hash 2>$null
    if ($exists) {
        # git commit --amend는 현재 HEAD에만 적용되므로
        # filter-branch나 rebase를 사용해야 합니다
        Write-Host "  커밋 발견: $hash" -ForegroundColor Green
    } else {
        Write-Host "  커밋을 찾을 수 없음: $hash" -ForegroundColor Red
    }
}

Write-Host "`n수동으로 rebase를 수행하려면 다음 명령을 사용하세요:" -ForegroundColor Yellow
Write-Host "git rebase -i HEAD~5" -ForegroundColor Cyan
Write-Host "`n각 커밋에서 'reword'로 변경하고 메시지를 수정하세요." -ForegroundColor Yellow

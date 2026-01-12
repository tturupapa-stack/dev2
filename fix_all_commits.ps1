# Git 커밋 메시지 한글 깨짐 수정 스크립트
$ErrorActionPreference = "Stop"

# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# Git 설정
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.quotepath false

Write-Host "깨진 커밋 메시지 수정을 시작합니다..." -ForegroundColor Yellow
Write-Host "주의: 이미 푸시된 커밋을 수정하려면 force push가 필요합니다." -ForegroundColor Red

# 깨진 커밋 메시지와 올바른 메시지 매핑
$commitFixes = @{
    "fff7276c81906500bd4a63fb39d27e22cc64f95a" = "fix: README.md 한글 인코딩 문제 해결 (UTF-8)"
    "a39a493a0245d15a730cb00f94386ca5a1b80f37" = "docs: 프롬프트 파일에 구현 완료 요약 추가"
    "b2475994a9e3263cad57e9c49ec6fcea6bb69311" = "docs: 영양성분 DB 통합 구현 완료 보고서 작성"
    "06c1bbde144006748561f28c5b793dd537c9304d" = "feat: 영양성분 DB 통합 구현 - Phase 1, 2 완료"
    "7692024b711e01f6cb2f3d0d3c8925724bc2e4eb" = "chore: 테스트 파일, 목업 데이터 등 streamlit에 업로드하는 데 혼선을 주는 자료들 삭제"
    "a15beb728b755f97f68820f9b4afefe7fa64ff4e" = "feat: 영양성분 DB 통합 프롬프트 작성 및 예외 처리 가이드 추가"
}

# 현재 HEAD 위치 저장
$originalHead = git rev-parse HEAD

# 각 커밋을 역순으로 수정 (가장 오래된 것부터)
$commits = @(
    "a15beb728b755f97f68820f9b4afefe7fa64ff4e",
    "7692024b711e01f6cb2f3d0d3c8925724bc2e4eb",
    "06c1bbde144006748561f28c5b793dd537c9304d",
    "b2475994a9e3263cad57e9c49ec6fcea6bb69311",
    "a39a493a0245d15a730cb00f94386ca5a1b80f37",
    "fff7276c81906500bd4a63fb39d27e22cc64f95a"
)

Write-Host "`n커밋 수정을 위해 rebase를 시작합니다..." -ForegroundColor Cyan
Write-Host "이 작업은 시간이 걸릴 수 있습니다." -ForegroundColor Yellow

# rebase를 사용하여 각 커밋 수정
$rebaseScript = @"
#!/bin/sh
exec true
"@

# PowerShell에서 rebase를 자동화하기 어려우므로, 
# 사용자에게 수동으로 rebase를 수행하도록 안내
Write-Host "`n수동 rebase가 필요합니다. 다음 단계를 따라주세요:" -ForegroundColor Yellow
Write-Host "1. git rebase -i HEAD~6 실행" -ForegroundColor Cyan
Write-Host "2. 각 깨진 커밋의 'pick'을 'reword'로 변경" -ForegroundColor Cyan
Write-Host "3. 각 커밋 메시지를 올바른 한글로 수정" -ForegroundColor Cyan
Write-Host "`n또는 다음 명령으로 자동 수정을 시도할 수 있습니다:" -ForegroundColor Yellow

# git filter-branch를 사용한 자동 수정 시도
Write-Host "`ngit filter-branch를 사용하여 자동 수정을 시도합니다..." -ForegroundColor Cyan

$env:FILTER_BRANCH_SQUELCH_WARNING = "1"
$filterScript = @"
if [ `$GIT_COMMIT = "fff7276c81906500bd4a63fb39d27e22cc64f95a" ]; then
    echo "fix: README.md 한글 인코딩 문제 해결 (UTF-8)"
elif [ `$GIT_COMMIT = "a39a493a0245d15a730cb00f94386ca5a1b80f37" ]; then
    echo "docs: 프롬프트 파일에 구현 완료 요약 추가"
elif [ `$GIT_COMMIT = "b2475994a9e3263cad57e9c49ec6fcea6bb69311" ]; then
    echo "docs: 영양성분 DB 통합 구현 완료 보고서 작성"
elif [ `$GIT_COMMIT = "06c1bbde144006748561f28c5b793dd537c9304d" ]; then
    echo "feat: 영양성분 DB 통합 구현 - Phase 1, 2 완료"
elif [ `$GIT_COMMIT = "7692024b711e01f6cb2f3d0d3c8925724bc2e4eb" ]; then
    echo "chore: 테스트 파일, 목업 데이터 등 streamlit에 업로드하는 데 혼선을 주는 자료들 삭제"
elif [ `$GIT_COMMIT = "a15beb728b755f97f68820f9b4afefe7fa64ff4e" ]; then
    echo "feat: 영양성분 DB 통합 프롬프트 작성 및 예외 처리 가이드 추가"
else
    cat
fi
"@

$filterScript | Out-File -FilePath filter_script.sh -Encoding UTF8 -NoNewline

Write-Host "필터 스크립트를 생성했습니다. 다음 명령을 실행하세요:" -ForegroundColor Yellow
Write-Host "git filter-branch -f --msg-filter 'bash filter_script.sh' HEAD~6..HEAD" -ForegroundColor Cyan

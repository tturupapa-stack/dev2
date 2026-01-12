#!/bin/bash
# Git 커밋 메시지 한글 깨짐 수정 스크립트

# UTF-8 인코딩 설정
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# Git 설정
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.quotepath false

# 최근 커밋 메시지 수정
git commit --amend -m "fix: .gitignore merge conflict 해결"

echo "커밋 메시지 수정 완료. Force push가 필요합니다."
echo "git push --force-with-lease origin main"

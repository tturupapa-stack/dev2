# Git 안전 푸시 설정 가이드

**작성일자:** 2026-01-05  
**목적:** 개발 작업을 PC에 먼저 저장하고, 선택한 경우에만 GitHub에 푸시하도록 설정

---

## ✅ 적용된 설정

### 1. Git Push 기본 동작 변경
- **`push.default = nothing`**: 기본 푸시 동작을 비활성화
  - 이제 `git push`만으로는 푸시되지 않습니다
  - 명시적으로 브랜치를 지정해야만 푸시 가능합니다

- **`push.autoSetupRemote = false`**: 자동 원격 브랜치 설정 비활성화
  - 새 브랜치를 자동으로 원격에 설정하지 않습니다

### 2. Pre-push Hook 설정
- **`.git/hooks/pre-push`**: 푸시 전 확인 요구
  - GitHub로 푸시하기 전에 확인 메시지가 표시됩니다
  - `yes`를 입력해야만 푸시가 진행됩니다

---

## 📋 사용 방법

### 로컬에만 저장 (기본 동작)

```bash
# 1. 변경사항 스테이징
git add .

# 2. 로컬에 커밋 (PC에 저장)
git commit -m "작업 내용"

# ✅ 여기까지는 PC에만 저장됩니다
```

### GitHub에 푸시 (선택적)

```bash
# 명시적으로 브랜치를 지정하여 푸시
git push origin main

# 또는 현재 브랜치 푸시
git push origin HEAD

# ⚠️ 푸시 전에 확인 메시지가 표시됩니다
# "yes"를 입력해야만 푸시가 진행됩니다
```

---

## 🔒 안전 장치

### 1. 기본 푸시 방지
- `git push`만 입력하면 아무것도 푸시되지 않습니다
- 반드시 `git push origin <브랜치명>` 형식으로 명시해야 합니다

### 2. 푸시 전 확인
- 푸시를 시도하면 다음 메시지가 표시됩니다:
```
==========================================
⚠️  GitHub 푸시 확인
==========================================

다음 저장소로 푸시하려고 합니다:
  https://github.com/tturupapa-stack/dev2

⚠️  주의: 이 작업은 원격 저장소에 변경사항을 업로드합니다.

푸시를 계속하려면 'yes'를 입력하세요:
```

### 3. 취소 가능
- `yes` 외의 아무 값이나 입력하면 푸시가 취소됩니다
- 로컬 저장소의 변경사항은 그대로 유지됩니다

---

## 📝 현재 Git 설정 확인

현재 프로젝트의 Git 설정을 확인하려면:

```bash
# 로컬 설정 확인
git config --local --list

# Push 관련 설정만 확인
git config --local --get-regexp "push"
```

---

## ⚙️ 설정 변경 내역

### `.git/config` 파일에 추가된 설정:
```ini
[push]
    default = nothing
    autoSetupRemote = false
```

### 생성된 Hook:
- `.git/hooks/pre-push`: 푸시 전 확인 스크립트

---

## 🔄 설정 되돌리기 (필요시)

만약 자동 푸시를 다시 활성화하고 싶다면:

```bash
# 기본 푸시 동작 복원
git config --local --unset push.default

# 자동 원격 설정 복원
git config --local --unset push.autoSetupRemote

# Pre-push hook 제거
rm .git/hooks/pre-push
```

---

## 💡 권장 워크플로우

1. **로컬 작업**
   ```bash
   git add .
   git commit -m "작업 내용"
   # ✅ PC에 저장 완료
   ```

2. **작업 검토**
   - 로컬에서 테스트 및 검토
   - 변경사항 확인: `git log`, `git diff`

3. **GitHub 푸시 (선택적)**
   ```bash
   git push origin main
   # 확인 메시지에 "yes" 입력
   ```

---

## ⚠️ 주의사항

1. **로컬 저장소 우선**
   - 모든 작업은 먼저 로컬에 커밋됩니다
   - GitHub 푸시는 선택 사항입니다

2. **푸시 전 확인**
   - Pre-push hook이 활성화되어 있어 항상 확인이 필요합니다
   - 실수로 푸시하는 것을 방지합니다

3. **팀 협업**
   - 팀원들과 공유할 변경사항만 푸시하세요
   - 로컬에서만 작업하는 경우 푸시하지 않아도 됩니다

---

**설정 완료일:** 2026-01-05  
**적용 범위:** 현재 프로젝트 (`team_projects_logic_D`)


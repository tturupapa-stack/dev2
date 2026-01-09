# GitHub 한글 인코딩 문제 해결 보고서

**작성일자:** 2026-01-05  
**작성자:** Logic Designer  
**관련 이슈:** GitHub 커밋 메시지 한글 깨짐 현상

---

## 1. 문제 발견

### 1.1 발견 시점
- GitHub 저장소에 `logic_designer` 모듈 푸시 후
- 커밋 메시지에서 한글이 깨져 표시됨

### 1.2 문제 증상
**깨진 커밋 메시지:**
```
Add logic_designer module: 寃利?濡쒖쭅, ?좊ː???먯닔 怨꾩궛, AI 遺꾩꽍 ?붿쭊
```

**원래 의도한 메시지:**
```
Add logic_designer module: 검증 로직, 신뢰도 점수 계산, AI 분석 엔진
```

### 1.3 영향 범위
- 커밋 메시지: 한글 깨짐
- 파일 내용: 정상 (UTF-8 인코딩 유지)
- GitHub 웹 인터페이스: 커밋 메시지만 깨짐

---

## 2. 원인 분석

### 2.1 근본 원인
1. **Git 인코딩 설정 미지정**
   - `i18n.commitencoding` 설정이 없어 기본 인코딩 사용
   - Windows 환경에서 기본 인코딩이 UTF-8이 아닐 수 있음

2. **PowerShell 인코딩 문제**
   - PowerShell에서 한글 입력 시 인코딩 변환 오류
   - 커밋 메시지 전달 과정에서 인코딩 손실

3. **Git 로그 출력 인코딩 미설정**
   - `i18n.logoutputencoding` 미설정으로 출력 시 깨짐

### 2.2 확인 사항
- 파일 내용은 UTF-8로 정상 저장됨
- 문제는 커밋 메시지 전달 과정에서만 발생
- GitHub 웹 인터페이스에서도 동일하게 깨짐

---

## 3. 해결 방법

### 3.1 Git 인코딩 설정 변경

다음 명령어로 Git 전역 설정을 UTF-8로 변경:

```bash
# 커밋 메시지 인코딩 설정
git config --global i18n.commitencoding utf-8

# 로그 출력 인코딩 설정
git config --global i18n.logoutputencoding utf-8

# 파일 경로 인코딩 설정 (한글 파일명 지원)
git config --global core.quotepath false

# GUI 인코딩 설정
git config --global gui.encoding utf-8
```

### 3.2 커밋 메시지 수정

**방법 1: 파일을 통한 커밋 메시지 작성**
```bash
# 커밋 메시지를 파일로 작성
echo "Add logic_designer module: 검증 로직, 신뢰도 점수 계산, AI 분석 엔진" > commit_message.txt

# 파일을 사용하여 커밋 메시지 수정
git commit --amend -F commit_message.txt
```

**방법 2: 환경 변수 설정 후 커밋**
```bash
# PowerShell에서 환경 변수 설정
$env:PYTHONIOENCODING="utf-8"
git commit --amend -m "Add logic_designer module: 검증 로직, 신뢰도 점수 계산, AI 분석 엔진"
```

### 3.3 강제 푸시

수정된 커밋을 GitHub에 반영:
```bash
git push origin main --force
```

**주의:** `--force` 옵션은 이미 푸시된 커밋을 덮어쓰므로, 팀원과 협의 후 사용해야 합니다.

---

## 4. 적용 결과

### 4.1 수정 전
```
21012b3 Add logic_designer module: 寃利?濡쒖쭅, ?좊ː???먯닔 怨꾩궛, AI 遺꾩꽍 ?붿쭊
```

### 4.2 수정 후
```
be9ad2a Add logic_designer module: 검증 로직, 신뢰도 점수 계산, AI 분석 엔진
```

### 4.3 확인 사항
- ✅ 커밋 메시지가 정상적으로 표시됨
- ✅ GitHub 웹 인터페이스에서도 정상 표시
- ✅ Git 로그에서 한글이 정상적으로 출력됨

---

## 5. 향후 예방 방안

### 5.1 필수 설정
모든 개발자에게 다음 Git 설정을 적용하도록 안내:

```bash
# .gitconfig 또는 프로젝트 README에 추가
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.quotepath false
git config --global gui.encoding utf-8
```

### 5.2 커밋 메시지 작성 가이드
1. **파일을 통한 작성 권장**
   - 한글이 포함된 커밋 메시지는 파일로 작성 후 `-F` 옵션 사용
   - IDE나 텍스트 에디터에서 UTF-8로 저장

2. **환경 변수 설정**
   - PowerShell 사용 시: `$env:PYTHONIOENCODING="utf-8"`
   - CMD 사용 시: `chcp 65001` (UTF-8 코드 페이지)

3. **IDE 설정 확인**
   - VS Code, PyCharm 등 IDE의 Git 인코딩 설정 확인
   - 기본 인코딩을 UTF-8로 설정

### 5.3 프로젝트 설정 파일 추가
프로젝트 루트에 `.gitattributes` 파일 추가 권장:

```gitattributes
# 모든 텍스트 파일을 UTF-8로 처리
* text=auto eol=lf
*.py text eol=lf
*.md text eol=lf
*.txt text eol=lf
```

---

## 6. 추가 확인 사항

### 6.1 파일 인코딩 확인
모든 Python 파일이 UTF-8로 저장되어 있는지 확인:
```python
# 파일 상단에 인코딩 선언 (선택사항)
# -*- coding: utf-8 -*-
```

### 6.2 GitHub 웹 인터페이스 확인
- 커밋 메시지가 정상적으로 표시되는지 확인
- 파일 내용의 한글이 정상적으로 표시되는지 확인

---

## 7. 결론

### 7.1 해결 완료
- ✅ 커밋 메시지 한글 깨짐 문제 해결
- ✅ Git 인코딩 설정 완료
- ✅ GitHub에 정상적으로 반영

### 7.2 권장 사항
1. 모든 팀원에게 Git 인코딩 설정 공유
2. 프로젝트 README에 인코딩 설정 가이드 추가
3. `.gitattributes` 파일 추가 고려
4. 커밋 메시지 작성 시 파일 사용 권장

---

## 부록: Git 설정 확인 명령어

```bash
# 현재 Git 인코딩 설정 확인
git config --get i18n.commitencoding
git config --get i18n.logoutputencoding
git config --get core.quotepath
git config --get gui.encoding

# 모든 Git 설정 확인
git config --list --global
```

---

**보고서 작성 완료일:** 2026-01-05  
**다음 검토 예정일:** 프로젝트 완료 시



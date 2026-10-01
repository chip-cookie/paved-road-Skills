# Paved Road

[English README](README.md) · MIT License

**Paved Road**는 **셀프서비스 플랫폼 인프라**(로드 밸런서, 프록시, API 게이트웨이,
프로비저닝 API와 그 뒤의 서버 플릿)를 설계·구축·리뷰할 때 AI 코딩 에이전트가 따라 하는
스킬 모음입니다.

`skills/` 폴더 하나로 **Claude Code, Codex CLI, Gemini CLI**에서 모두 동작하고,
`SKILL.md` 형식을 읽는 다른 에이전트에서도 쓸 수 있습니다.

플랫폼 엔지니어링에서 *paved road*(또는 golden path)는 제품 팀이 플랫폼 팀에 따로
요청하지 않아도 따라가기만 하면 되는 표준 경로를 뜻합니다. 이 스킬들은 에이전트에게
그런 길을 만드는 방법을 알려줍니다.

---

## 동작 방식

스킬은 `SKILL.md`가 든 폴더입니다. 짧은 설명(**언제** 쓰는지)과 단계별 절차,
주의 신호(red flags), 결과물 형식이 들어 있습니다.

1. 세션이 시작되면 에이전트는 각 스킬의 이름과 설명만 읽습니다 (전체 합쳐 수백 토큰).
2. 요청이 설명과 맞으면("이 게이트웨이 설계 리뷰해줘", "기술 부채가 어디 있지?")
   그 스킬의 전체 절차를 불러와 따라갑니다.
3. 긴 예제와 스크립트는 `references/`, `scripts/`에 있고 필요할 때만 읽습니다.

이름으로 직접 호출할 수도 있습니다 ([사용법](#사용법) 참고).

## 스킬 목록

| 스킬 | 언제 쓰나 |
|------|-----------|
| `edge-architecture-review` | 플랫폼·프록시·게이트웨이 설계를 종합 리뷰. **여기서 시작.** 6가지 관점으로 점검하고 아래 스킬로 연결 |
| `async-provisioning-broker` | 오래 걸리거나 실패할 수 있는 작업을 셀프서비스 API로 제공 (API → 큐 → 워커 → 상태 저장소 → 폴링) |
| `template-context-config` | 설정을 손으로 고치거나 재시작이 필요할 때. 템플릿 + 컨텍스트로 렌더링 → 검증 → 무중단 반영 |
| `golden-image-pipeline` | Packer + Salt/Ansible 골든 이미지, 웨이브 단위 멀티리전 IaC 배포 |
| `edge-sidecar-offload` | 서비스마다 인증·레이트리밋·로깅을 따로 구현할 때. 엣지/사이드카로 이동 |
| `guardrail-validation` | 사용자가 라우팅·DNS·LB 설정을 바꿀 수 있을 때, 어떤 입력도 트래픽 블랙홀을 만들지 못하게 |
| `churn-hotspot-refactor` | git 이력으로 변경 빈도 × 복잡도 핫스팟을 찾아 리팩터링 대상 선정 (스크립트 포함) |

---

## 설치

쓰는 에이전트를 고르세요. 어느 방법이든 스킬 7개가 모두 설치됩니다.

### Claude Code

Claude Code 세션 안에서:

```text
/plugin marketplace add chip-cookie/paved-road-Skills
/plugin install paved-road@paved-road
```

또는 터미널에서:

```bash
claude plugin marketplace add chip-cookie/paved-road-Skills
claude plugin install paved-road@paved-road
```

**설치 확인:**

```bash
claude plugin details paved-road
```

`Component inventory`에 `Skills (7)`이 보이면 성공입니다. 새 세션을 열거나
`/reload-plugins`를 실행하면 불러옵니다.

### Codex CLI

터미널에서:

```bash
codex plugin marketplace add chip-cookie/paved-road-Skills
codex plugin add paved-road@paved-road
```

또는 Codex 안에서 `/plugins`를 열고 **Paved Road**를 검색해 설치해도 됩니다.

**설치 확인:**

```bash
codex plugin list
```

`paved-road@paved-road`가 `installed, enabled`로 보이면 성공입니다. Codex 안에서
`/skills`를 실행하면 스킬 7개가 보입니다.

> 플러그인 대신 스킬 폴더로만 설치하고 싶다면 [설치 스크립트](#직접-설치-모든-에이전트)를 쓰세요.

### Gemini CLI

```bash
gemini extensions install https://github.com/chip-cookie/paved-road-Skills
```

설치 전에 확인을 묻습니다 (`--consent`를 붙이면 건너뜀).

**설치 확인:**

```bash
gemini skills list
```

또는 Gemini CLI 안에서 `/skills list`.

Gemini CLI는 세션에서 스킬이 처음 발동될 때 사용 허락을 묻습니다.

### 직접 설치 (모든 에이전트)

한 번 받아두고, 스크립트로 각 에이전트 폴더에 심볼릭 링크를 만듭니다:

```bash
git clone https://github.com/chip-cookie/paved-road-Skills ~/.paved-road
~/.paved-road/scripts/install.sh
```

| 옵션 | 동작 |
|------|------|
| *(없음)* | 모든 에이전트에, 사용자 전역으로, 심볼릭 링크로 설치 |
| `--agent claude` / `codex` / `gemini` | 한 에이전트에만 설치 |
| `--scope project` | 홈 폴더 대신 현재 프로젝트에 설치 |
| `--copy` | 링크 대신 파일 복사 |
| `--uninstall` | 스크립트로 설치한 것 제거 |

설치 위치:

| 에이전트 | 사용자 전역 | 프로젝트 |
|----------|-------------|----------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex CLI | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.agents/skills/` (Codex와 공유) | `.agents/skills/` |

Codex CLI와 Gemini CLI는 둘 다 `~/.agents/skills`를 읽기 때문에 한 번 설치로 둘 다 됩니다.

`SKILL.md`를 지원하는 다른 에이전트(Cursor, OpenCode 등)는 `skills/` 아래 폴더들을
그 에이전트의 스킬 폴더에 복사하면 됩니다.

---

## 사용법

### 에이전트가 알아서 고르게

하고 싶은 일을 그냥 말하면 됩니다:

```text
새 사내 로드 밸런서 서비스 설계 문서야. 리뷰해줘.
```

에이전트가 `edge-architecture-review`를 골라 그 절차대로 진행합니다.

### 이름으로 직접 호출

| 에이전트 | 방법 |
|----------|------|
| Claude Code | `/paved-road:edge-architecture-review` (다른 스킬도 `/paved-road:<스킬명>`) |
| Codex CLI | `$edge-architecture-review` 또는 `/skills`에서 선택 |
| Gemini CLI | 프롬프트에 스킬 이름을 언급, 예: "guardrail-validation 써서" |
| 직접 설치 (Claude Code) | `/edge-architecture-review` |

### 프롬프트 예시

```text
docs/edge-design.md를 edge-architecture-review로 리뷰하고 우선 조치 3개 뽑아줘.

DNS 레코드랑 CDN 배포를 만드는 셀프서비스 API가 필요해.
async-provisioning-broker로 FastAPI, SQS, DynamoDB 써서 설계해줘.

서비스마다 NGINX 설정을 복붙하고 있어. template-context-config로
템플릿 렌더링 방식으로 바꾸는 계획 세워줘.

golden-image-pipeline으로 프록시 서버용 Packer + Ansible 파이프라인이랑
4개 리전 배포 계획 짜줘.

서비스마다 JWT 미들웨어가 따로 있어. edge-sidecar-offload로
인증을 게이트웨이로 옮기는 계획 세워줘.

이게 우리 라우팅 API 스키마야. guardrail-validation 돌려서
트래픽 블랙홀을 만들 수 있는 입력 전부 찾아줘.

이 저장소에 churn-hotspot-refactor 돌려서 리팩터링 대상 상위 3개 뽑아줘.
```

### 추천 흐름

```
edge-architecture-review  ->  빈틈을 찾고 우선순위 매김
        |
        +-> async-provisioning-broker   (셀프서비스가 티켓 기반이거나 동기식)
        +-> template-context-config     (설정을 손으로 고치거나 재시작 필요)
        +-> golden-image-pipeline       (서버를 직접 들어가서 패치)
        +-> edge-sidecar-offload        (인증/레이트리밋이 서비스마다 중복)
        +-> guardrail-validation        (잘못된 입력이 라우팅을 깨뜨릴 수 있음)
        +-> churn-hotspot-refactor      (유지보수가 점점 느려짐)
```

### 핫스팟 스크립트 단독 실행

`churn-hotspot-refactor`에는 단독 실행 스크립트가 들어 있습니다 (Python 3, 추가 설치 없음):

```bash
python3 ~/.paved-road/skills/churn-hotspot-refactor/scripts/hotspots.py \
  --repo /path/to/repo --since "12 months ago" --top 20 \
  --exclude "tests/*,vendor/*,docs/*"
```

`--json`을 붙이면 JSON으로 출력합니다.

---

## 업데이트

| 방법 | 명령어 |
|------|--------|
| Claude Code | `claude plugin marketplace update paved-road` 후 `claude plugin update paved-road@paved-road` |
| Codex CLI | `codex plugin marketplace upgrade paved-road` 후 `codex plugin add paved-road@paved-road` |
| Gemini CLI | `gemini extensions update paved-road` |
| 직접 설치 | `git -C ~/.paved-road pull` (링크 방식이면 자동 반영, `--copy`로 설치했다면 스크립트 재실행) |

## 삭제

| 방법 | 명령어 |
|------|--------|
| Claude Code | `claude plugin uninstall paved-road@paved-road`, 필요하면 `claude plugin marketplace remove paved-road` |
| Codex CLI | `codex plugin remove paved-road@paved-road`, 필요하면 `codex plugin marketplace remove paved-road` |
| Gemini CLI | `gemini extensions uninstall paved-road` |
| 직접 설치 | `~/.paved-road/scripts/install.sh --uninstall` |

---

## 문제 해결

**스킬이 알아서 발동되지 않아요.**
이름으로 직접 호출하세요 ([이름으로 직접 호출](#이름으로-직접-호출)). 자동 발동은 요청이
스킬 설명과 얼마나 비슷한지에 달려 있습니다.

**Gemini CLI나 Codex에 스킬이 두 번 보여요.**
플러그인/확장과 직접 설치 스크립트를 둘 다 쓴 경우입니다. 하나만 남기세요:
`~/.paved-road/scripts/install.sh --uninstall`

**업데이트했는데 새 스킬이 안 보여요.**
에이전트를 재시작하세요. Claude Code는 `/reload-plugins`, Gemini CLI는 `/skills reload`.

**Gemini CLI가 프로젝트 스킬을 무시해요.**
Gemini CLI는 신뢰(trust)한 폴더에서만 프로젝트 스킬을 불러옵니다. 폴더를 신뢰하거나
사용자 전역으로 설치하세요.

**`git clone`이 비밀번호를 물어봐요.**
주소를 확인하세요: `https://github.com/chip-cookie/paved-road-Skills`

---

## 저장소 구조

```
paved-road-Skills/
├── skills/                      # 스킬 본체 (모든 에이전트 공용)
│   └── <skill>/
│       ├── SKILL.md             # 이름, 설명, 절차
│       ├── references/          # 긴 예제, 필요할 때만 읽음
│       └── scripts/             # 실행 스크립트
├── .claude-plugin/              # Claude Code 플러그인 + 마켓플레이스
├── .codex-plugin/               # Codex 플러그인 설정
├── .agents/plugins/             # Codex 마켓플레이스
├── gemini-extension.json        # Gemini CLI 확장
├── GEMINI.md                    # Gemini CLI가 읽는 스킬 목록
├── AGENTS.md                    # 기여 규칙 (사람/에이전트 공통)
├── scripts/install.sh           # 직접 설치 스크립트
├── scripts/validate.py          # 커밋 전 스킬 검사
└── docs/source-notes.md         # 패턴 출처
```

## 기여

이슈와 PR 환영합니다. [AGENTS.md](AGENTS.md)를 읽고 아래를 실행하세요:

```bash
python3 scripts/validate.py
```

## 라이선스 및 출처

MIT. [LICENSE](LICENSE) 참고.

패턴은 Vasilios Syrakis의 아틀라시안 엣지 플랫폼 관련 공개 YouTube 영상(2026년 5월)을
요약한 것입니다. [docs/source-notes.md](docs/source-notes.md) 참고.
이 프로젝트는 독립 프로젝트이며 Atlassian과 제휴·보증 관계가 없습니다.
Sovereign은 Atlassian의 오픈소스 Envoy 컨트롤 플레인으로, 참조만 하며 포함하지 않습니다.

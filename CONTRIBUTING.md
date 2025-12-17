<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=25,0,51&height=150&section=header&text=Contributing&fontSize=50&animation=fadeIn&fontAlignY=38&desc=Join%20the%20Development&descAlignY=60&descSize=18"/>

<div align="center">

[![Code Quality](https://img.shields.io/badge/code%20quality-strict-blueviolet?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-required-success?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)

</div>

---

## 🧪 Quality Gates

We prioritize code stability. Every Pull Request runs a CI pipeline that checks:

1. **Linting:** No style violations (Ruff).
2. **Typing:** Strict static type checking (Mypy).
3. **Testing:** All unit tests must pass (Pytest).

### ⚡ Quick Check Commands

Run these locally before pushing:

```bash
# 1. Lint & Format
ruff check . --fix
ruff format .

# 2. Type Check
export PYTHONPATH=src
mypy --config-file pyproject.toml src/core src/nomi src/stt

# 3. Run Unit Tests
pytest
```

## 🏗️ Architecture Guide

```mermaid
graph TD
    A[run.py] -->|starts| B[Bot & Dispatcher]
    B -->|uses| C[Handlers]
    C -->|uses| D[NomiService]
    D -->|uses| E[NomiClient]
    E -->|validates| F[Pydantic Models]
    C -->|uses| G[VoskSTT]

    style D fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
    style E fill:#B19CD9,stroke:#2c3e50,stroke-width:2px,color:#fff
    style F fill:#E92063,stroke:#2c3e50,stroke-width:2px,color:#fff
```

- **Domain Logic:** Keep logic in `src/nomi/service.py`, not in handlers.
- **Type Safety:** Never use `Dict` or `Any` for API responses. Use schemas in `src/nomi/schemas.py`.
- **Infrastructure:** Use `Dockerfile` for environment consistency.

## 📝 Commit Messages

We follow **Conventional Commits**:

- `feat:` New features
- `fix:` Bug fixes
- `refactor:` Code improvements without logic changes
- `test:` Adding or fixing tests
- `chore:` Config, Docker, CI updates

**Example:**

> `feat(voice): add support for ogg to wav conversion`

-----

<div align="center">
Thank you for making NomiAssistantTG better!
</div>


#!/usr/bin/env python3
"""PreToolUse 훅: Edit/Write로 새로 작성되는 코드에 주석이 있는지 확인한다.

이 프로젝트는 학습 목적을 겸하기 때문에(CLAUDE.md 코딩 컨벤션 참고),
Claude Code가 어느 정도 규모 이상의 코드를 새로 쓰면서 주석을 하나도
남기지 않으면, 이 훅이 도구 실행 자체를 막는다(permissionDecision: deny).
그러면 Claude Code는 이 이유를 보고 주석을 추가해서 다시 시도한다.
"""

import json
import sys

# 파일 확장자별로 어떤 기호가 "주석"인지 정의한다.
COMMENT_PREFIXES = {
    ".py": ("#",),
    ".ts": ("//", "/*", "*"),
    ".tsx": ("//", "/*", "*"),
    ".js": ("//", "/*", "*"),
    ".jsx": ("//", "/*", "*"),
}

# 이 줄 수 미만의 작은 변경은 검사하지 않는다.
# (한두 줄짜리 사소한 수정까지 막으면 너무 번거로워서 실용성이 떨어진다)
MIN_LINES_TO_CHECK = 3


def allow() -> None:
    """도구 실행을 허용한다는 JSON을 stdout에 출력한다."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                }
            }
        )
    )


def deny(reason: str) -> None:
    """도구 실행을 막는다는 JSON을 stdout에 출력한다. reason은 Claude에게 그대로 전달된다."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> None:
    raw = sys.stdin.read()  # Claude Code가 이 훅에 전달하는 JSON을 표준입력으로 읽는다

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # 입력 파싱에 실패하면 막는 것보다 통과시키는 게 안전하다 (개발 흐름을 막지 않기 위해)
        allow()
        return

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # 파일 확장자를 뽑아서, 우리가 검사 대상으로 정의한 언어인지 확인한다
    ext = "." + file_path.rsplit(".", 1)[-1] if "." in file_path else ""
    prefixes = COMMENT_PREFIXES.get(ext)

    if not prefixes:
        # .md, .json, .toml 등 코드가 아닌 파일은 검사하지 않는다
        allow()
        return

    # Write 도구는 파일 전체 내용이 file_content에 들어있고,
    # Edit 도구는 교체될 새 코드 조각이 new_string에 들어있다.
    if tool_name == "Write":
        new_code = tool_input.get("file_content", "")
    elif tool_name == "Edit":
        new_code = tool_input.get("new_string", "")
    else:
        allow()
        return

    # 빈 줄을 제외한 실제 코드 줄만 센다
    lines = [line for line in new_code.splitlines() if line.strip()]

    if len(lines) < MIN_LINES_TO_CHECK:
        # 너무 작은 변경은 검사하지 않는다
        allow()
        return

    has_comment = any(line.strip().startswith(prefixes) for line in lines)

    if has_comment:
        allow()
    else:
        deny(
            "이 프로젝트는 학습 목적으로 코드에 설명 주석을 다는 걸 컨벤션으로 정했습니다 "
            "(CLAUDE.md 코딩 컨벤션 참고). 지금 작성하려는 코드에는 주석이 하나도 없습니다. "
            "각 줄 또는 블록마다 무엇을 왜 하는지 설명하는 주석을 추가해서 다시 작성해주세요."
        )


if __name__ == "__main__":
    main()

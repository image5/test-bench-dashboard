#!/bin/bash
# 测试用例匹配器安装脚本

SKILL_NAME="testcase-matcher-skill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== $SKILL_NAME 安装脚本 ==="

# 检测平台
detect_platform() {
    if [ -d "$HOME/.claude" ]; then
        echo "claude"
    elif [ -d ".cursor" ]; then
        echo "cursor"
    elif [ -d ".github" ]; then
        echo "copilot"
    elif [ -d "$HOME/.cursor" ]; then
        echo "cursor-global"
    elif [ -d "$HOME/.windsurf" ]; then
        echo "windsurf"
    elif [ -d ".windsurf" ]; then
        echo "windsurf-project"
    elif [ -d ".clinerules" ]; then
        echo "cline"
    elif [ -d "$HOME/.gemini" ]; then
        echo "gemini"
    elif [ -d ".kiro" ]; then
        echo "kiro"
    elif [ -d "$HOME/.agents" ]; then
        echo "universal"
    else
        echo "unknown"
    fi
}

# 安装到指定路径
install_to() {
    local dest="$1"
    echo "安装到: $dest"
    mkdir -p "$dest"
    cp -R "$SCRIPT_DIR"/* "$dest/"
    echo "✓ 安装完成"
    echo ""
    echo "使用方法: 在对话中输入 /$SKILL_NAME"
}

# 主逻辑
PLATFORM="${1:-$(detect_platform)}"

case "$PLATFORM" in
    claude)
        install_to "$HOME/.claude/skills/$SKILL_NAME"
        ;;
    cursor)
        install_to ".cursor/rules/$SKILL_NAME"
        ;;
    cursor-global)
        install_to "$HOME/.cursor/rules/$SKILL_NAME"
        ;;
    copilot)
        install_to ".github/skills/$SKILL_NAME"
        ;;
    windsurf)
        install_to ".windsurf/rules/$SKILL_NAME"
        ;;
    windsurf-project)
        install_to ".windsurf/rules/$SKILL_NAME"
        ;;
    cline)
        install_to ".clinerules/$SKILL_NAME"
        ;;
    gemini)
        install_to "$HOME/.gemini/skills/$SKILL_NAME"
        ;;
    kiro)
        install_to ".kiro/skills/$SKILL_NAME"
        ;;
    universal)
        install_to "$HOME/.agents/skills/$SKILL_NAME"
        ;;
    all)
        echo "安装到所有检测到的平台..."
        [ -d "$HOME/.claude" ] && install_to "$HOME/.claude/skills/$SKILL_NAME"
        [ -d ".cursor" ] && install_to ".cursor/rules/$SKILL_NAME"
        [ -d ".github" ] && install_to ".github/skills/$SKILL_NAME"
        [ -d "$HOME/.agents" ] && install_to "$HOME/.agents/skills/$SKILL_NAME"
        ;;
    *)
        echo "无法自动检测平台。请手动指定："
        echo "  ./install.sh --platform claude"
        echo "  ./install.sh --platform cursor"
        echo "  ./install.sh --platform copilot"
        echo "  ./install.sh --platform universal"
        echo "  ./install.sh --all  (安装到所有可用平台)"
        exit 1
        ;;
esac

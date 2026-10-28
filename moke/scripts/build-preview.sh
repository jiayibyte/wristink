#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
export JAVA_HOME="/Library/Java/JavaVirtualMachines/jdk-19.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
sdk_config="$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg"
sdk_path="$(tr -d '\r\n' < "$sdk_config")"
./scripts/build.sh -r
"$sdk_path/bin/monkeyc" -f preview.jungle -d instinct3solar45mm -o bin/InstinctFace-demo.prg -y "$HOME/.Garmin/keys/developer_key.der" -r -w
print '正式安装版：bin/InstinctFace.prg（真实数据）'
print '演示预览版：bin/InstinctFace-demo.prg（完整模拟数据，独立应用 ID）'
if [[ "${1:-}" == "--run" ]]; then
    "$sdk_path/bin/connectiq"
    for attempt in 1 2 3; do
        if "$sdk_path/bin/monkeydo" "$PWD/bin/InstinctFace-demo.prg" instinct3solar45mm; then
            exit 0
        fi
        sleep 1
    done
    print -u2 '模拟器未就绪；请关闭模拟器中的编辑对话框后重试。'
    exit 1
fi

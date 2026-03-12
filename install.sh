#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
FORCE=0
NO_PAUSE=0
UNINSTALL=0
CONFIG_PATH=""
INTERACTIVE=1
TARGET_NAMES=()

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/$(basename "${BASH_SOURCE[0]}")"
DOTFILES="$SCRIPT_DIR"
SKILLS="$DOTFILES/skills"
AGENTS="$DOTFILES/AGENTS.md"

if [[ -z "${CONFIG_PATH:-}" ]]; then
  CONFIG_PATH="$DOTFILES/targets.json"
fi

RESULT_TARGETS=()
RESULT_KINDS=()
RESULT_PATHS=()
RESULT_STATUS=()
RESULT_MESSAGES=()

VERIFY_TARGETS=()
VERIFY_KINDS=()
VERIFY_PATHS=()
VERIFY_STATUS=()
VERIFY_MESSAGES=()

write_info() {
  printf '\033[36m%s\033[0m\n' "$1"
}

write_ok() {
  printf '\033[32m%s\033[0m\n' "$1"
}

write_warn() {
  printf '\033[33m%s\033[0m\n' "$1"
}

write_err() {
  printf '\033[31m%s\033[0m\n' "$1"
}

add_result() {
  RESULT_TARGETS+=("$1")
  RESULT_KINDS+=("$2")
  RESULT_PATHS+=("$3")
  RESULT_STATUS+=("$4")
  RESULT_MESSAGES+=("$5")
}

add_verify_result() {
  VERIFY_TARGETS+=("$1")
  VERIFY_KINDS+=("$2")
  VERIFY_PATHS+=("$3")
  VERIFY_STATUS+=("$4")
  VERIFY_MESSAGES+=("$5")
}

normalize_path() {
  local p="$1"
  if [[ -z "$p" ]]; then
    printf '%s\n' ""
    return
  fi

  python3 - <<'PY' "$p"
import os, sys
print(os.path.abspath(sys.argv[1]).rstrip("/"))
PY
}

expand_path_template() {
  local p="$1"
  p="${p//\{HOME\}/$HOME}"
  p="${p//\{DOTFILES\}/$DOTFILES}"
  printf '%s\n' "$p"
}

ensure_parent_dir() {
  local p="$1"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ ! -e "$p" ]]; then
      write_info "[预演] 将创建目录：$p"
    fi
    return
  fi

  mkdir -p "$p"
}

remove_existing_path() {
  local p="$1"

  if [[ ! -e "$p" && ! -L "$p" ]]; then
    return
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将删除：$p"
    return
  fi

  rm -rf "$p"
}

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    write_err "[dotfiles] 未找到 jq。Linux 版本需要 jq 来读取 targets.json。"
    write_err "[dotfiles] Debian/Ubuntu: sudo apt-get install jq"
    write_err "[dotfiles] macOS (Homebrew): brew install jq"
    exit 1
  fi
}

require_python3() {
  if ! command -v python3 >/dev/null 2>&1; then
    write_err "[dotfiles] 未找到 python3。当前脚本用它做稳妥的路径归一化。"
    exit 1
  fi
}

get_backup_root() {
  local root="$HOME/.dotfiles-backup"
  if [[ ! -d "$root" && "$DRY_RUN" -ne 1 ]]; then
    mkdir -p "$root"
  fi
  printf '%s\n' "$root"
}

backup_existing_path() {
  local path="$1"
  local target_name="$2"
  local kind="$3"

  if [[ ! -e "$path" && ! -L "$path" ]]; then
    return 0
  fi

  local timestamp backup_root safe_target safe_kind leaf backup_dir final_dir backup_path
  timestamp="$(date +%Y%m%d-%H%M%S)"
  backup_root="$(get_backup_root)"
  safe_target="$(printf '%s' "$target_name" | sed 's#[\\/:*?"<>|]#_#g')"
  safe_kind="$(printf '%s' "$kind" | sed 's#[\\/:*?"<>|]#_#g')"
  leaf="$(basename "$path")"
  backup_dir="$backup_root/$timestamp"
  final_dir="$backup_dir/$safe_target-$safe_kind"
  backup_path="$final_dir/$leaf"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将备份：$path -> $backup_path"
    return 0
  fi

  mkdir -p "$final_dir"
  mv "$path" "$backup_path"
  write_warn "[备份] 已备份：$path -> $backup_path"
}

load_targets_count() {
  jq '.targets | length' "$CONFIG_PATH"
}

get_target_name_by_index() {
  local idx="$1"
  jq -r ".targets[$idx].name" "$CONFIG_PATH"
}

get_selected_targets_json() {
  if [[ "${#TARGET_NAMES[@]}" -eq 0 ]]; then
    jq -c '.targets[]' "$CONFIG_PATH"
    return
  fi

  local names_json
  names_json="$(printf '%s\n' "${TARGET_NAMES[@]}" | jq -R . | jq -s .)"

  jq -c --argjson names "$names_json" '
    .targets[]
    | select(.name as $n | $names | index($n))
  ' "$CONFIG_PATH"
}

is_correct_skills_link() {
  local target_path="$1"

  if [[ ! -L "$target_path" ]]; then
    return 1
  fi

  local actual expected
  actual="$(readlink "$target_path" || true)"
  expected="$SKILLS"

  actual="$(normalize_path "$actual")"
  expected="$(normalize_path "$expected")"

  [[ "$actual" == "$expected" ]]
}

get_agents_state() {
  local target_path="$1"

  if [[ ! -e "$target_path" && ! -L "$target_path" ]]; then
    printf '%s\n' "Missing"
    return
  fi

  if [[ -L "$target_path" ]]; then
    local actual expected
    actual="$(readlink "$target_path" || true)"
    expected="$AGENTS"

    actual="$(normalize_path "$actual")"
    expected="$(normalize_path "$expected")"

    if [[ "$actual" == "$expected" ]]; then
      printf '%s\n' "Linked"
      return
    fi
  fi

  if [[ -f "$target_path" && -f "$AGENTS" ]]; then
    if cmp -s "$target_path" "$AGENTS"; then
      printf '%s\n' "Copied"
      return
    fi
  fi

  printf '%s\n' "Other"
}

verify_skills_entry() {
  local target_name="$1"
  local dst="$2"
  local skill_name="$3"

  local dst_expanded target_path
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$skill_name"

  if is_correct_skills_link "$target_path"; then
    write_ok "[校验通过] $target_name / skills：$target_path"
    add_verify_result "$target_name" "skills" "$target_path" "成功" "是预期链接"
  else
    write_err "[校验失败] $target_name / skills：$target_path"
    add_verify_result "$target_name" "skills" "$target_path" "失败" "不是预期链接"
  fi
}

verify_agents_entry() {
  local target_name="$1"
  local dst="$2"
  local file_name="$3"

  local dst_expanded target_path agent_state
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$file_name"
  agent_state="$(get_agents_state "$target_path")"

  if [[ "$agent_state" == "Linked" || "$agent_state" == "Copied" ]]; then
    write_ok "[校验通过] $target_name / agents：$target_path"
    add_verify_result "$target_name" "agents" "$target_path" "成功" "是预期链接或正确副本"
  else
    write_err "[校验失败] $target_name / agents：$target_path"
    add_verify_result "$target_name" "agents" "$target_path" "失败" "不是预期链接或正确副本"
  fi
}

install_skills_entry() {
  local target_name="$1"
  local dst="$2"
  local skill_name="$3"

  local dst_expanded target_path
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$skill_name"

  ensure_parent_dir "$dst_expanded"

  if is_correct_skills_link "$target_path"; then
    write_ok "[跳过] $target_name / skills 已正确存在：$target_path"
    add_result "$target_name" "skills" "$target_path" "跳过" "已是正确链接"
    if [[ "$DRY_RUN" -ne 1 ]]; then
      verify_skills_entry "$target_name" "$dst" "$skill_name"
    fi
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      write_warn "[跳过] $target_name / skills 已存在非预期内容：$target_path"
      write_warn "       如需接管，请使用 --force（会先备份再替换）。"
      add_result "$target_name" "skills" "$target_path" "跳过" "已存在非预期内容；未使用 --force"
      return
    fi

    backup_existing_path "$target_path" "$target_name" "skills"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将创建 skills 链接：$target_path -> $SKILLS"
    add_result "$target_name" "skills" "$target_path" "预演" "将创建符号链接"
    return
  fi

  ln -s "$SKILLS" "$target_path"
  write_ok "[完成] $target_name / skills：$target_path -> $SKILLS"
  add_result "$target_name" "skills" "$target_path" "成功" "已创建符号链接"
  verify_skills_entry "$target_name" "$dst" "$skill_name"
}

install_agents_entry() {
  local target_name="$1"
  local dst="$2"
  local file_name="$3"

  local dst_expanded target_path agent_state
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$file_name"

  ensure_parent_dir "$dst_expanded"

  agent_state="$(get_agents_state "$target_path")"
  if [[ "$agent_state" == "Linked" ]]; then
    write_ok "[跳过] $target_name / agents 已正确存在：$target_path"
    add_result "$target_name" "agents" "$target_path" "跳过" "已是正确符号链接"
    if [[ "$DRY_RUN" -ne 1 ]]; then
      verify_agents_entry "$target_name" "$dst" "$file_name"
    fi
    return
  fi

  if [[ "$agent_state" == "Copied" ]]; then
    write_ok "[跳过] $target_name / agents 已存在受管副本：$target_path"
    add_result "$target_name" "agents" "$target_path" "跳过" "已是正确副本"
    if [[ "$DRY_RUN" -ne 1 ]]; then
      verify_agents_entry "$target_name" "$dst" "$file_name"
    fi
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      write_warn "[跳过] $target_name / agents 已存在非预期内容：$target_path"
      write_warn "       如需接管，请使用 --force（会先备份再替换）。"
      add_result "$target_name" "agents" "$target_path" "跳过" "已存在非预期内容；未使用 --force"
      return
    fi

    backup_existing_path "$target_path" "$target_name" "agents"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将创建 agents 链接：$target_path -> $AGENTS"
    add_result "$target_name" "agents" "$target_path" "预演" "将创建符号链接"
    return
  fi

  ln -s "$AGENTS" "$target_path"
  write_ok "[完成] $target_name / agents：$target_path -> $AGENTS"
  add_result "$target_name" "agents" "$target_path" "成功" "已创建符号链接"
  verify_agents_entry "$target_name" "$dst" "$file_name"
}

uninstall_skills_entry() {
  local target_name="$1"
  local dst="$2"
  local skill_name="$3"

  local dst_expanded target_path
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$skill_name"

  if [[ ! -e "$target_path" && ! -L "$target_path" ]]; then
    write_info "[跳过] $target_name / skills 不存在：$target_path"
    add_result "$target_name" "skills" "$target_path" "跳过" "目标不存在"
    return
  fi

  if ! is_correct_skills_link "$target_path"; then
    if [[ "$FORCE" -ne 1 ]]; then
      write_warn "[跳过] $target_name / skills 存在，但不是当前脚本管理的目标：$target_path"
      write_warn "       如需卸载并清理，请使用 --force（会先备份再删除）。"
      add_result "$target_name" "skills" "$target_path" "跳过" "存在非受管内容；未使用 --force"
      return
    fi

    backup_existing_path "$target_path" "$target_name" "skills-uninstall"
  else
    remove_existing_path "$target_path"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将卸载 skills：$target_path"
    add_result "$target_name" "skills" "$target_path" "预演" "将删除"
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    remove_existing_path "$target_path"
  fi

  write_ok "[完成] 已卸载 $target_name / skills：$target_path"
  add_result "$target_name" "skills" "$target_path" "成功" "已删除"
}

uninstall_agents_entry() {
  local target_name="$1"
  local dst="$2"
  local file_name="$3"

  local dst_expanded target_path agent_state
  dst_expanded="$(expand_path_template "$dst")"
  target_path="$dst_expanded/$file_name"

  if [[ ! -e "$target_path" && ! -L "$target_path" ]]; then
    write_info "[跳过] $target_name / agents 不存在：$target_path"
    add_result "$target_name" "agents" "$target_path" "跳过" "目标不存在"
    return
  fi

  agent_state="$(get_agents_state "$target_path")"
  if [[ "$agent_state" != "Linked" && "$agent_state" != "Copied" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      write_warn "[跳过] $target_name / agents 存在，但不是当前脚本管理的目标：$target_path"
      write_warn "       如需卸载并清理，请使用 --force（会先备份再删除）。"
      add_result "$target_name" "agents" "$target_path" "跳过" "存在非受管内容；未使用 --force"
      return
    fi

    backup_existing_path "$target_path" "$target_name" "agents-uninstall"
  else
    remove_existing_path "$target_path"
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    write_info "[预演] 将卸载 agents：$target_path"
    add_result "$target_name" "agents" "$target_path" "预演" "将删除"
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    remove_existing_path "$target_path"
  fi

  write_ok "[完成] 已卸载 $target_name / agents：$target_path"
  add_result "$target_name" "agents" "$target_path" "成功" "已删除"
}

process_target_json() {
  local target_json="$1"

  local target_name
  target_name="$(jq -r '.name' <<<"$target_json")"

  write_info ""
  write_info "[dotfiles] 正在处理：$target_name"

  local skills_len agents_len i dst name

  skills_len="$(jq '.skills | length // 0' <<<"$target_json")"
  for (( i=0; i<skills_len; i++ )); do
    dst="$(jq -r ".skills[$i].path" <<<"$target_json")"
    name="$(jq -r ".skills[$i].name // \"skills\"" <<<"$target_json")"

    if [[ "$UNINSTALL" -eq 1 ]]; then
      if ! uninstall_skills_entry "$target_name" "$dst" "$name"; then
        add_result "$target_name" "skills" "$(expand_path_template "$dst")/$name" "失败" "卸载失败"
      fi
    else
      if ! install_skills_entry "$target_name" "$dst" "$name"; then
        add_result "$target_name" "skills" "$(expand_path_template "$dst")/$name" "失败" "安装失败"
      fi
    fi
  done

  agents_len="$(jq '.agents | length // 0' <<<"$target_json")"
  for (( i=0; i<agents_len; i++ )); do
    dst="$(jq -r ".agents[$i].path" <<<"$target_json")"
    name="$(jq -r ".agents[$i].name // \"AGENTS.md\"" <<<"$target_json")"

    if [[ "$UNINSTALL" -eq 1 ]]; then
      if ! uninstall_agents_entry "$target_name" "$dst" "$name"; then
        add_result "$target_name" "agents" "$(expand_path_template "$dst")/$name" "失败" "卸载失败"
      fi
    else
      if ! install_agents_entry "$target_name" "$dst" "$name"; then
        add_result "$target_name" "agents" "$(expand_path_template "$dst")/$name" "失败" "安装失败"
      fi
    fi
  done
}

show_summary() {
  echo
  printf '\033[35m%s\033[0m\n' "================ 执行结果汇总 ================"

  if [[ "${#RESULT_STATUS[@]}" -eq 0 ]]; then
    printf '\033[33m%s\033[0m\n' "没有产生任何执行结果。"
  else
    local success=0 skipped=0 preview=0 failed=0 i status
    for status in "${RESULT_STATUS[@]}"; do
      case "$status" in
        成功) ((success+=1)) ;;
        跳过) ((skipped+=1)) ;;
        预演) ((preview+=1)) ;;
        失败) ((failed+=1)) ;;
      esac
    done

    printf '成功：%s    跳过：%s    预演：%s    失败：%s\n' "$success" "$skipped" "$preview" "$failed"

    for (( i=0; i<${#RESULT_STATUS[@]}; i++ )); do
      local line
      line="[$(printf '%s' "${RESULT_STATUS[$i]}")] ${RESULT_TARGETS[$i]} / ${RESULT_KINDS[$i]}
  路径：${RESULT_PATHS[$i]}
  说明：${RESULT_MESSAGES[$i]}"

      case "${RESULT_STATUS[$i]}" in
        成功) printf '\033[32m%s\033[0m\n' "$line" ;;
        跳过) printf '\033[33m%s\033[0m\n' "$line" ;;
        预演) printf '\033[36m%s\033[0m\n' "$line" ;;
        失败) printf '\033[31m%s\033[0m\n' "$line" ;;
        *) printf '%s\n' "$line" ;;
      esac
    done
  fi

  echo
  printf '\033[35m%s\033[0m\n' "================ 校验结果汇总 ================"

  if [[ "${#VERIFY_STATUS[@]}" -eq 0 ]]; then
    if [[ "$DRY_RUN" -eq 1 || "$UNINSTALL" -eq 1 ]]; then
      printf '\033[33m%s\033[0m\n' "当前模式不进行安装后校验。"
    else
      printf '\033[33m%s\033[0m\n' "没有产生任何校验结果。"
    fi
  else
    local verify_ok=0 verify_fail=0 i status
    for status in "${VERIFY_STATUS[@]}"; do
      case "$status" in
        成功) ((verify_ok+=1)) ;;
        失败) ((verify_fail+=1)) ;;
      esac
    done

    printf '通过：%s    失败：%s\n' "$verify_ok" "$verify_fail"

    for (( i=0; i<${#VERIFY_STATUS[@]}; i++ )); do
      local line
      line="[$(printf '%s' "${VERIFY_STATUS[$i]}")] ${VERIFY_TARGETS[$i]} / ${VERIFY_KINDS[$i]}
  路径：${VERIFY_PATHS[$i]}
  说明：${VERIFY_MESSAGES[$i]}"

      case "${VERIFY_STATUS[$i]}" in
        成功) printf '\033[32m%s\033[0m\n' "$line" ;;
        失败) printf '\033[31m%s\033[0m\n' "$line" ;;
        *) printf '%s\n' "$line" ;;
      esac
    done
  fi

  printf '\033[35m%s\033[0m\n' "============================================"
}

show_main_menu() {
  echo
  printf '\033[35m%s\033[0m\n' "================ dotfiles 安装器 ================"
  echo "1) 安装"
  echo "2) 卸载"
  echo "3) 预演安装"
  echo "4) 预演卸载"
  echo "5) 退出"
  printf '\033[35m%s\033[0m\n' "==============================================="

  while true; do
    read -r -p "请选择操作: " choice
    case "$choice" in
      1) DRY_RUN=0; UNINSTALL=0; break ;;
      2) DRY_RUN=0; UNINSTALL=1; break ;;
      3) DRY_RUN=1; UNINSTALL=0; break ;;
      4) DRY_RUN=1; UNINSTALL=1; break ;;
      5) exit 0 ;;
      *) write_warn "请输入 1-5 之间的编号。" ;;
    esac
  done
}

show_target_menu() {
  local count i target_name input parts part n all_index
  count="$(load_targets_count)"
  all_index=$((count + 1))

  echo
  write_info "[dotfiles] 请选择目标，可多选（用逗号分隔）："
  for (( i=0; i<count; i++ )); do
    target_name="$(get_target_name_by_index "$i")"
    printf '%s) %s\n' "$((i + 1))" "$target_name"
  done
  printf '%s) 全部\n' "$all_index"

  while true; do
    read -r -p "请输入编号: " input
    [[ -z "${input// }" ]] && { write_warn "请输入至少一个编号。"; continue; }

    IFS=',' read -r -a parts <<<"$input"
    TARGET_NAMES=()
    local choose_all=0 valid=1 seen=""

    for part in "${parts[@]}"; do
      part="${part// /}"
      [[ -z "$part" ]] && continue

      if ! [[ "$part" =~ ^[0-9]+$ ]]; then
        valid=0
        break
      fi

      n="$part"

      if [[ "$n" -eq "$all_index" ]]; then
        choose_all=1
        break
      fi

      if (( n < 1 || n > count )); then
        valid=0
        break
      fi

      if [[ ",$seen," != *",$n,"* ]]; then
        seen="${seen},$n"
        TARGET_NAMES+=("$(get_target_name_by_index "$((n - 1))")")
      fi
    done

    if [[ "$valid" -ne 1 ]]; then
      write_warn "输入格式不正确，请输入数字编号，例如：1,3"
      continue
    fi

    if [[ "$choose_all" -eq 1 ]]; then
      TARGET_NAMES=()
      for (( i=0; i<count; i++ )); do
        TARGET_NAMES+=("$(get_target_name_by_index "$i")")
      done
      break
    fi

    if [[ "${#TARGET_NAMES[@]}" -eq 0 ]]; then
      write_warn "请选择至少一个目标。"
      continue
    fi

    break
  done
}

interactive_mode() {
  show_main_menu
  show_target_menu

  read -r -p "是否允许接管已存在的陌生目标？(y/N): " force_answer
  if [[ "$force_answer" =~ ^([yY]|yes|YES)$ ]]; then
    FORCE=1
  else
    FORCE=0
  fi

  echo
  write_info "[dotfiles] 本次执行配置："
  if [[ "$UNINSTALL" -eq 1 && "$DRY_RUN" -eq 1 ]]; then
    echo "  模式：预演卸载"
  elif [[ "$UNINSTALL" -eq 1 ]]; then
    echo "  模式：卸载"
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    echo "  模式：预演安装"
  else
    echo "  模式：安装"
  fi
  echo "  接管陌生目标：$( [[ "$FORCE" -eq 1 ]] && echo "是（会先备份再替换）" || echo "否" )"
  echo "  目标：${TARGET_NAMES[*]}"

  read -r -p "确认执行？(Y/n): " confirm
  if [[ "$confirm" =~ ^([nN]|no|NO)$ ]]; then
    write_warn "[dotfiles] 已取消。"
    exit 0
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        INTERACTIVE=0
        shift
        ;;
      --force)
        FORCE=1
        INTERACTIVE=0
        shift
        ;;
      --no-pause)
        NO_PAUSE=1
        INTERACTIVE=0
        shift
        ;;
      --uninstall)
        UNINSTALL=1
        INTERACTIVE=0
        shift
        ;;
      --config)
        CONFIG_PATH="$2"
        INTERACTIVE=0
        shift 2
        ;;
      --target)
        TARGET_NAMES+=("$2")
        INTERACTIVE=0
        shift 2
        ;;
      --help|-h)
        cat <<'EOF'
用法：
  ./install.sh                 # 交互模式
  ./install.sh --dry-run
  ./install.sh --uninstall
  ./install.sh --force
  ./install.sh --target "Codex CLI"
  ./install.sh --config ./targets.json
  ./install.sh --no-pause

参数：
  --dry-run     预演，不真正修改
  --uninstall   卸载模式
  --force       允许接管陌生目标（先备份再替换）
  --target      指定目标，可重复传入
  --config      指定配置文件路径
  --no-pause    执行完不暂停
EOF
        exit 0
        ;;
      *)
        write_err "[dotfiles] 未知参数：$1"
        exit 1
        ;;
    esac
  done
}

main() {
  parse_args "$@"
  require_jq
  require_python3

  if [[ ! -f "$CONFIG_PATH" ]]; then
    write_err "[dotfiles] 未找到配置文件：$CONFIG_PATH"
    exit 1
  fi

  if [[ "$UNINSTALL" -ne 1 ]]; then
    [[ -d "$SKILLS" ]] || { write_err "[dotfiles] 未找到 skills 目录：$SKILLS"; exit 1; }
    [[ -f "$AGENTS" ]] || { write_err "[dotfiles] 未找到 AGENTS.md：$AGENTS"; exit 1; }
  fi

  if [[ "$INTERACTIVE" -eq 1 ]]; then
    interactive_mode
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ "$UNINSTALL" -eq 1 ]]; then
      write_info "[dotfiles] 当前为预演模式：只显示将卸载什么，不会真的删除。"
    else
      write_info "[dotfiles] 当前为预演模式：只显示将安装什么，不会真的修改。"
    fi
  fi

  if [[ "$FORCE" -eq 1 ]]; then
    write_warn "[dotfiles] 已启用 --force：遇到陌生目标时，会先备份到 $HOME/.dotfiles-backup 再替换。"
  fi

  if [[ "$UNINSTALL" -eq 1 ]]; then
    write_warn "[dotfiles] 当前为卸载模式。"
  fi

  local selected_json found_any=0
  while IFS= read -r selected_json; do
    [[ -z "$selected_json" ]] && continue
    found_any=1
    process_target_json "$selected_json"
  done < <(get_selected_targets_json)

  if [[ "$found_any" -ne 1 ]]; then
    write_err "[dotfiles] 没有可执行的目标。"
    exit 1
  fi

  show_summary

  if [[ "$NO_PAUSE" -ne 1 ]]; then
    echo
    read -r -p "按回车退出" _
  fi
}

main "$@"
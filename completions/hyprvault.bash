# Bash completions for hyprvault

_hyprvault_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="save load list delete help"

    case "${prev}" in
        hyprvault)
            COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
            return 0
            ;;
        load|delete)
            local sessions=""
            local config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/hyprvault/sessions"
            if [[ -d "$config_dir" ]]; then
                sessions=$(find "$config_dir" -name "*.json" -exec basename {} .json \; 2>/dev/null)
            fi
            COMPREPLY=($(compgen -W "${sessions}" -- "${cur}"))
            return 0
            ;;
    esac
}

complete -F _hyprvault_completions hyprvault

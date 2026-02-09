# Fish completions for hyprvault

# Disable file completions
complete -c hyprvault -f

# Commands
complete -c hyprvault -n "__fish_use_subcommand" -a "save" -d "Save current session"
complete -c hyprvault -n "__fish_use_subcommand" -a "load" -d "Load a saved session"
complete -c hyprvault -n "__fish_use_subcommand" -a "list" -d "List saved sessions"
complete -c hyprvault -n "__fish_use_subcommand" -a "delete" -d "Delete a session"
complete -c hyprvault -n "__fish_use_subcommand" -a "help" -d "Show help"

# Session name completions for load/delete
function __hyprvault_sessions
    set -l config_dir ~/.config/hyprvault/sessions
    if test -d $config_dir
        for f in $config_dir/*.json
            basename $f .json
        end
    end
end

complete -c hyprvault -n "__fish_seen_subcommand_from load delete" -a "(__hyprvault_sessions)" -d "Session"

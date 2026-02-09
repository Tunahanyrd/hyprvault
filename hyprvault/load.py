import json
import asyncio

from .utils import get_session_path, GREEN, YELLOW, RED, RESET

HYPR_V = 0.0


async def dispatch(cmd_args, wait=True):
    proc = await asyncio.create_subprocess_exec(
        "hyprctl",
        "dispatch",
        *cmd_args,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    if wait:
        await proc.wait()


async def init_hypr_config():
    """Versiyonu ve diğer evrensel ayarları bir kereye mahsus alır."""
    global HYPR_V
    proc = await asyncio.create_subprocess_exec(
        "hyprctl", "version", "-j", stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    try:
        v_data = json.loads(stdout)
        v_parts = v_data.get("version", "0.0.0").split(".")
        HYPR_V = float(f"{v_parts[0]}.{v_parts[1]}")
    except Exception:
        HYPR_V = 0.0


async def get_clients():
    proc = await asyncio.create_subprocess_exec(
        "hyprctl", "clients", "-j", stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    return json.loads(stdout)


def find_best_match(sw, current_clients, used_addresses: set):
    """Find the best matching window, avoiding already-used addresses."""
    class_name = sw["class_name"]
    command = sw.get("command", "")

    # First pass: try to match by class_name AND command
    for c in current_clients:
        addr = c.get("address")
        if addr in used_addresses:
            continue
        if c.get("class") == class_name:
            # Check if command matches (compare basename)
            client_pid = c.get("pid", 0)
            if client_pid:
                try:
                    with open(f"/proc/{client_pid}/cmdline", "rb") as f:
                        client_cmd = f.read().split(bytes([0]))[0].decode("utf-8")
                        if client_cmd == command:
                            return c
                except Exception:
                    pass

    # Second pass: match by class_name only
    for c in current_clients:
        addr = c.get("address")
        if addr in used_addresses:
            continue
        if c.get("class") == class_name:
            return c

    return None


async def restore_window(sw, current_clients, used_addresses: set):
    """Restore a single window to its saved state."""
    ws_id = sw["workspace_id"]

    match = find_best_match(sw, current_clients, used_addresses)

    if match:
        addr = match["address"]
        used_addresses.add(addr)

        # First, focus the window to make dispatches work on it
        await dispatch(["focuswindow", f"address:{addr}"])
        await asyncio.sleep(0.1)

        # Exit fullscreen if currently fullscreen
        if match.get("fullscreen", 0) > 0:
            await dispatch(["fullscreen", "0"])
            await asyncio.sleep(0.1)

        # Set floating/tiled state
        if sw["is_floating"]:
            await dispatch(["setfloating", f"address:{addr}"])
            await asyncio.sleep(0.05)
            await dispatch(
                [
                    "resizewindowpixel",
                    f"exact {sw['size'][0]} {sw['size'][1]},address:{addr}",
                ]
            )
            await dispatch(
                ["movewindowpixel", f"exact {sw['at'][0]} {sw['at'][1]},address:{addr}"]
            )
        else:
            await dispatch(["settiled", f"address:{addr}"])

        # Move to target workspace
        await dispatch(["movetoworkspacesilent", f"{ws_id},address:{addr}"])
        await asyncio.sleep(0.1)

        # Apply fullscreen state if needed
        saved_fs_state = sw.get("fullscreen", 0)
        if saved_fs_state > 0:
            await dispatch(["focuswindow", f"address:{addr}"])
            await asyncio.sleep(0.05)
            await dispatch(["fullscreen", str(saved_fs_state)])

        return addr, sw.get("focus_history_id", 999)
    else:
        # Window not found, spawn a new one
        rules = f"workspace {ws_id} silent"
        if sw["is_floating"]:
            rules += f";float;move {sw['at'][0]} {sw['at'][1]};size {sw['size'][0]} {sw['size'][1]}"
        else:
            rules += ";tile"

        cmd = sw.get("command", "")
        if cmd:
            print(f"{YELLOW}[*]{RESET} Spawning new window: {cmd}")
            await asyncio.create_subprocess_exec(
                "hyprctl", "dispatch", "exec", f"[{rules}]", cmd
            )
        return None, None


async def restore_session(name="last_session"):
    session_path = get_session_path(name)

    try:
        with open(session_path, "r") as f:
            saved_windows = json.load(f)
    except FileNotFoundError:
        print(f"{RED}[-]{RESET} Session not found: {session_path}")
        return

    await init_hypr_config()
    current_clients = await get_clients()

    # Track which windows we've already matched
    used_addresses: set[str] = set()
    focus_candidates = []

    # Sort by focus_history_id to restore in order
    saved_windows.sort(key=lambda x: x.get("focus_history_id", 999), reverse=True)

    for sw in saved_windows:
        addr, fid = await restore_window(sw, current_clients, used_addresses)
        if addr and fid is not None:
            focus_candidates.append((addr, fid))

    # Focus the window that was last focused
    if focus_candidates:
        target_addr = min(focus_candidates, key=lambda x: x[1])[0]
        if target_addr:
            await dispatch(["focuswindow", f"address:{target_addr}"])

    print(f"{GREEN}[+]{RESET} Session restored from: {session_path}")


if __name__ == "__main__":
    try:
        asyncio.run(restore_session())
    except KeyboardInterrupt:
        pass

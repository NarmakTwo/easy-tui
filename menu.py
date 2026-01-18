import curses

def menu(title, classes, color='blue', selector=['-', '→'], toggle=False, operators={}):
    """
    Basic menu for selecting options and executing functions using curses.
    
    :param title: Title of the menu
    :param classes: List of options to select from
    :param color: Color of the selector
    :param selector: List of characters to use as the selector (default is ['-', '→'])
    :param toggle: Whether to allow toggling of options
    :param operators: Dictionary of functions to execute on selection (key: name, value: function)

    in the operators dict, returning a dictionary with the following keys will do the following:
        add: List of classes to add to the list of options
        remove: List of classes to remove from the list of options
        finish: Ends the menu and returns the selected options

    Press [tab] to switch between options and functions.
    """
    def character(stdscr):
        col_map = {'red': curses.COLOR_RED, 'green': curses.COLOR_GREEN, 'yellow': curses.COLOR_YELLOW,
                   'blue': curses.COLOR_BLUE, 'magenta': curses.COLOR_MAGENTA, 'cyan': curses.COLOR_CYAN, 'white': curses.COLOR_WHITE}
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, col_map.get(color.lower(), curses.COLOR_BLUE), -1)
        normal, highlighted = curses.color_pair(1), curses.color_pair(2)
        ops = operators.copy()
        if "Finish" not in ops:
            ops["Finish"] = lambda x: None
        op_keys = list(ops.keys())
        toggled = [False] * len(classes)
        cursor_pos, active_group = 0, "options"
        while True:
            stdscr.erase()
            stdscr.addstr(f"{title}\n\n", normal)
            stdscr.addstr("--- OPTIONS ---\n", normal)
            for i, cls in enumerate(classes):
                is_curr = (active_group == "options" and cursor_pos == i)
                pref = selector[1] if is_curr else selector[0]
                mark = "[x]" if toggled[i] else "[ ]"
                stdscr.addstr(f"{pref} {mark} {cls}\n", highlighted if is_curr else normal)
            stdscr.addstr("\n--- FUNCTIONS ---\n", normal)
            for i, op_name in enumerate(op_keys):
                is_curr = (active_group == "operators" and cursor_pos == i)
                pref = selector[1] if is_curr else selector[0]
                stdscr.addstr(f"{pref} {op_name}\n", highlighted if is_curr else normal)
            c = stdscr.getch()
            if c == 9:
                active_group = "operators" if active_group == "options" else "options"
                cursor_pos = 0
            elif c == curses.KEY_UP:
                cursor_pos = max(0, cursor_pos - 1)
            elif c == curses.KEY_DOWN:
                limit = (len(classes) - 1) if active_group == "options" else (len(op_keys) - 1)
                cursor_pos = min(limit, cursor_pos + 1)
            elif c in (10, 13):
                results = [classes[i] for i, v in enumerate(toggled) if v]
                if active_group == "options":
                    if toggle:
                        toggled[cursor_pos] = not toggled[cursor_pos]
                    else:
                        return [classes[cursor_pos]]
                else:
                    op_name = op_keys[cursor_pos]
                    if op_name.lower() == "finish":
                        return results
                    opReturn = ops[op_name](results)
                    if getattr(opReturn, "add", None):
                        classes.extend(opReturn.add)
                    if getattr(opReturn, "remove", None):
                        classes.remove(opReturn.remove)
                    if getattr(opReturn, "finish", None):
                        return results
    return curses.wrapper(character)

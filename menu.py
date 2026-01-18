def menu(title, classes, color='blue', selector=['-', '→'], toggle=False, operators={}, display=None, default=False):
    """
    Basic menu for selecting options and executing functions using curses.
    :param title: Title of the menu
    :param classes: List of options to select from (can be objects or dicts)
    :param color: Color of the selector
    :param selector: List of characters to use as the selector (default is ['-', '→'])
    :param toggle: Whether to allow toggling of options
    :param operators: Dictionary of functions to execute on selection (key: name, value: function)
    :param display: Key string to access the display value if classes contains dictionaries
    :param default: Whether to default all toggles to on if toggle is True
    :return List of selected options
    in the operators dict, returning a dictionary with the following keys will do the following:
        add: List of classes to add to the list of options
        remove: List of classes to remove from the list of options
        finish: Ends the menu and returns the selected options
    Press [tab] to switch between options and functions.
    """
    def character(stdscr):
        col_map = {'red': curses.COLOR_RED, 'green': curses.COLOR_GREEN, 'yellow': curses.COLOR_YELLOW, 'blue': curses.COLOR_BLUE, 'magenta': curses.COLOR_MAGENTA, 'cyan': curses.COLOR_CYAN, 'white': curses.COLOR_WHITE}
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, col_map.get(color.lower(), curses.COLOR_BLUE), -1)
        normal, highlighted = curses.color_pair(1), curses.color_pair(2)
        ops = operators.copy()
        if "Finish" not in ops: ops["Finish"] = lambda x: {}
        op_keys = list(ops.keys())
        selected_items = set()
        if toggle and default:
            selected_items = set(id(cls) for cls in classes)
        cursor_pos, active_group = 0, "options"
        curses.curs_set(0)
        while True:
            stdscr.erase()
            max_y, max_x = stdscr.getmaxyx()
            y_pos = 0
            try:
                stdscr.addstr(f"{title}\n\n", normal)
            except:
                pass
            y_pos = 3
            try:
                stdscr.addstr("--- OPTIONS ---\n", normal)
            except:
                pass
            y_pos += 1
            for i, cls in enumerate(classes):
                if y_pos >= max_y - 6:
                    break
                is_curr = (active_group == "options" and cursor_pos == i)
                pref = selector[1] if is_curr else selector[0]
                mark = "[x]" if id(cls) in selected_items else "[ ]"
                label = cls[display] if (display is not None and isinstance(cls, dict)) else str(cls)
                label = label[:max_x - 10].encode('ascii', 'replace').decode('ascii')
                try:
                    stdscr.addstr(f"{pref} {mark} {label}\n", highlighted if is_curr else normal)
                except:
                    pass
                y_pos += 1
            try:
                stdscr.addstr("\n--- FUNCTIONS ---\n", normal)
            except:
                pass
            for i, op_name in enumerate(op_keys):
                if y_pos >= max_y - 1:
                    break
                is_cur = (active_group == "operators" and cursor_pos == i)
                pref = selector[1] if is_cur else selector[0]
                try:
                    stdscr.addstr(f"{pref} {op_name}\n", highlighted if is_cur else normal)
                except:
                    pass
                y_pos += 1
            c = stdscr.getch()
            if c == 9:
                active_group = "operators" if active_group == "options" else "options"
                cursor_pos = 0
            elif c == curses.KEY_UP:
                cursor_pos = max(0, cursor_pos - 1)
            elif c == curses.KEY_DOWN:
                limit = (len(classes) - 1) if active_group == "options" else (len(op_keys) - 1)
                cursor_pos = min(max(0, limit), cursor_pos + 1)
            elif c in (10, 13):
                res = [cls for cls in classes if id(cls) in selected_items]
                if active_group == "options":
                    target = classes[cursor_pos]
                    if toggle:
                        if id(target) in selected_items: selected_items.remove(id(target))
                        else: selected_items.add(id(target))
                    else:
                        return [target]
                else:
                    op_name = op_keys[cursor_pos]
                    if op_name.lower() == "finish": return res
                    curses.endwin()
                    opReturn = ops[op_name](res)
                    if isinstance(opReturn, dict):
                        if "add" in opReturn: classes.extend(opReturn["add"])
                        if "remove" in opReturn:
                            for r_item in opReturn["remove"]:
                                if r_item in classes: classes.remove(r_item)
                    cursor_pos = 0
                    curses.curs_set(0)
                    stdscr.refresh()
    return curses.wrapper(character)

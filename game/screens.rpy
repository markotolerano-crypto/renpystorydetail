# --- STYLE SETTINGS ---
style default:
    font "MADE Mirage Regular PERSONAL USE.otf" 
    size 30
    color "#ffffff"



style md_opt_bar is bar:
    # 1. CONTAINER HEIGHT
    # Must match your thumb height (48px) to prevent clipping.
    ysize 48

    # 2. THUMB SETTINGS
    # Centers the thumb on the ends of the bar.
    thumb_offset 24
    thumb "images/slider_thumb.png"
    thumb_shadow None

    # 3. TRACK ALIGNMENT (The Double-Transform Fix)
    # Inner Transform: Forces the image to be a thin 12px strip.
    # Outer Transform: Creates a 48px tall container and centers the 12px strip inside it.
    
    # Background (Empty Part)
    base_bar Transform(
        Transform(Frame("images/slider_empty.png", 12, 12), ysize=12),
        ysize=48, yalign=0.5
    )
    right_bar Transform(
        Transform(Frame("images/slider_empty.png", 12, 12), ysize=12),
        ysize=48, yalign=0.5
    )

    # Foreground (Filled Part)
    left_bar Transform(
        Transform("images/slider_fill_flat.png", ysize=12),
        ysize=48, yalign=0.5
    )

# ==========================================================
# Reading-only options (safe defaults)
# ==========================================================
default persistent.md_read_theme = "amoled"   # amoled / dark / light
default persistent.md_text_speed = "normal"  # instant / fast / normal


# INLINE TAP PROMPTS (Animated in-text choices)
# Usage in script:
#   $ md_ip_set_choices("hand", [("Touch her hand", "touch"), ("Pull away", "back")])
#   "She pauses. {ip=hand}touch her hand{/ip} and see what happens."
# Later:
#   if md_ip_get("hand") == "touch": ...
#   elif md_ip_get("hand") is None: ...  # ignored
# ==========================================================

default md_ip_results = {}      # prompt_id -> chosen value (missing/None = ignored)
default md_ip_choices = {}      # prompt_id -> list of (label, value)

init -2 python:
    # Helper setters/getters you can call from script.
    def md_ip_set_choices(prompt_id, choices):
        # choices: [("Label", value), ...]
        store.md_ip_choices[prompt_id] = list(choices)

    def md_ip_set(prompt_id, value):
        store.md_ip_results[prompt_id] = value

    def md_ip_get(prompt_id, default=None):
        return store.md_ip_results.get(prompt_id, default)

    # Hyperlink handling for {a=ip:...} used by the {ip} text tag below.
    def _md_ip_styler(target):
        # We render the animated text ourselves, so styling here is mostly a fallback.
        if target and target.startswith("ip:"):
            return "md_ip_link"
        return "hyperlink_text"

    def _md_ip_click(target):
        if not target:
            return

        if target.startswith("ip:"):
            pid = target[3:]
            renpy.show_screen("md_ip_menu", prompt_id=pid)
            renpy.restart_interaction()
            return

        # Safe fallback: open URLs if someone uses {a=https://...}
        if target.startswith("http://") or target.startswith("https://"):
            renpy.open_url(target)

    def _md_ip_hover(target):
        return

    # Ren'Py 8.5+: hyperlink handling is configured via config.hyperlink_handlers
    # (hyperlink_functions is a style property, not a config variable).
    #
    # We register an in-game protocol "ip:" that opens the inline prompt menu.
    def _md_ip_handler(value):
        pid = (value or "").strip()
        if not pid:
            return None
        renpy.show_screen("md_ip_menu", prompt_id=pid)
        renpy.restart_interaction()
        return None

    config.hyperlink_handlers["ip"] = _md_ip_handler

    # Custom text tag: {ip=prompt_id}This phrase animates and can be tapped{/ip}
    #
    # IMPORTANT: This function must have no side-effects (Ren'Py may call it during prediction).
    def _md_ip_tag(tag, argument, contents):
        pid = (argument or "").strip()
        if not pid:
            return contents

        # Embed an animated Text displayable in-line.
        theme = getattr(store.persistent, "md_read_theme", "amoled")

        if theme == "light":
            # Slightly softer than pure black, and remove the heavy black outline.
            fg = "#111111"
            ol = [(1, "#ffffff", 0, 0)]
        else:
            fg = "#ffffff"
            ol = [(2, "#000000", 0, 0)]

        d = At(Text(contents, tokenized=True, style="md_ip_text", color=fg, outlines=ol, size=45), md_ip_glitch)

        return [
            (renpy.TEXT_TAG, "a=ip:%s" % pid),
            (renpy.TEXT_DISPLAYABLE, d),
            (renpy.TEXT_TAG, "/a"),
        ]
    config.custom_text_tags["ip"] = _md_ip_tag

# Subtle “glitch/breath” motion for the tappable phrase itself.
transform md_ip_glitch:
    subpixel True
    # A tiny calm drift most of the time...
    block:
        yoffset 0
        xoffset 0
        alpha 1.0
        pause 0.60
        linear 0.80 alpha 0.92
        linear 0.80 alpha 1.0
        pause 0.50

        # ...then a quick micro-glitch burst (rare-ish, not constant).
        linear 0.02 xoffset -2
        linear 0.02 xoffset 2
        linear 0.02 xoffset -1
        linear 0.02 xoffset 1
        linear 0.02 xoffset 0
        pause 1.00
        repeat

# Visual style for the animated phrase (no underline/brackets/icons).
style md_ip_text is default:
    size 45
    color "#ffffff"
    outlines [(2, "#000000", 0, 0)]
    # A tiny extra spacing can help tapping accuracy/readability on mobile.
    kerning 0.5

style hyperlink_text is default:
    underline False

style hyperlink_hover is hyperlink_text:
    color "#ffffff"

style md_ip_link is hyperlink_text:
    # Fallback only. Keep it close to normal text (no underline).
    underline False

# Popup menu shown when the phrase is tapped.
screen md_ip_menu(prompt_id):
    $ _md_theme = getattr(persistent, "md_read_theme", "amoled")
    $ _md_bg = "#000000" if _md_theme == "amoled" else ("#111111" if _md_theme == "dark" else "#ffffff")
    $ _md_fg = "#ffffff" if _md_theme in ("amoled", "dark") else "#000000"
    $ _md_popup = "#111111" if _md_theme in ("amoled", "dark") else "#f2f2f2"
    $ _md_btn = "#1f1f1f" if _md_theme in ("amoled", "dark") else "#ffffff"
    $ _md_btn_hover = "#2a2a2a" if _md_theme in ("amoled", "dark") else "#e6e6e6"
    $ _md_dim = "#00000080" if _md_theme in ("amoled", "dark") else "#00000040"
    modal True
    zorder 300

    # Dim the reading screen slightly.
    add Solid(_md_dim)

    # Tap outside to close (leaves result as "ignored"/unset).
    button:
        xfill True
        yfill True
        background None
        action Hide("md_ip_menu")

    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 900
        padding (60, 45)
        background Solid(_md_popup)
        vbox:
            spacing 25

            # Optional title line (can be removed if you want it even cleaner).
            text "Choose":
                size 38
                color _md_fg
                xalign 0.5
                outlines ([(1, "#ffffff", 0, 0)] if _md_theme == "light" else [(2, "#000000", 0, 0)])

            $ _opts = md_ip_choices.get(prompt_id, None)
            if not _opts:
                $ _opts = [("Yes", True), ("No", False)]

            for _label, _val in _opts:
                textbutton _label:
                    action [Function(md_ip_set, prompt_id, _val), Hide("md_ip_menu")]
                    background Solid(_md_btn)
                    hover_background Solid(_md_btn_hover)
                    xpadding 30
                    ypadding 18
                    text_size 45
                    text_color _md_fg
                    text_hover_color _md_fg
                    text_outlines ([(1, "#ffffff", 0, 0)] if _md_theme == "light" else [(2, "#000000", 0, 0)])
                    xfill True

    key "K_ESCAPE" action Hide("md_ip_menu")

screen menu_scene():
    # Persistent menu background + leaves.
    # This screen is NOT tagged as "menu", so it is not replaced when switching
    # between menu screens (Preferences/Save/Load/etc.). That keeps the leaf
    # animation continuous and prevents it from restarting/syncing.
    zorder 0

    $ _mm_leaves_y = int(config.screen_height * 0.40)

    # Background depends on which menu screen is currently active.
    if renpy.get_screen("main_menu"):
        add cover_sky_1200("sky_loop")
        add cover_1920("forestbg", yalign=1.0) at parallax_gyro
    else:
        # Options and other menu screens: pure black behind the UI.
        add Solid("#000000")

    # Leaves always render from the same persistent screen instance.
    # Leaves render from the same persistent screen instance (do not restart between menus).
    add Transform("falling_leaves", yoffset=_mm_leaves_y)

    # Tree only on the start screen (keeps the original layering).
    if renpy.get_screen("main_menu"):
        add Transform("tree", zoom=1.00, xalign=0.5, yalign=1.0) at parallax_gyro

default persistent.md_skip_mode = "seen"     # seen / all

init python:
    def md_reset_settings():
        # Reading
        persistent.md_read_theme = "amoled"
        persistent.md_text_speed = "normal"
        # Helpers
        persistent.md_skip_mode = "seen"
        # Set engine preferences safely
        try:
            preferences.afm_enable = False
            preferences.afm_time = 10.0
        except Exception:
            pass
        try:
            # Seen-only skipping by default
            preferences.skip_unseen = False
        except Exception:
            pass

# ==========================================================
# 1. MAIN MENU
# ==========================================================


init python:
    # Safely returns the correct menu action for a notification "goto" payload.
    # Avoids subscripting None inside screen-language action constructors.
    def _notif_goto_action(pending):
        if not pending:
            return NullAction()
        try:
            kind, key = pending
        except Exception:
            return NullAction()

        if kind == "lore":
            return ShowMenu("bio_lore_detail", lore_key=key, from_notif=True)
        elif kind == "character":
            return ShowMenu("bio_character_detail", char_key=key, from_notif=True)
        else:
            return ShowMenu("bio_menu")




init -2 python:
    # Ensures our persistent menu scene (background + leaves) is shown only once,
    # so the leaf animation doesn\'t restart when switching between menu screens.
    def md_ensure_menu_scene():
        try:
            if not renpy.get_screen("menu_scene"):
                renpy.show_screen("menu_scene")
        except Exception:
            # If screen lookup isn\'t available yet, ignore.
            pass



screen menu_scene():
    # Persistent menu background + leaves.
    # This screen is NOT tagged as "menu", so it is not replaced when switching
    # between menu screens (Preferences/Save/Load/etc.). That keeps the leaf
    # animation continuous and prevents it from restarting/syncing.
    zorder 0

    $ _mm_leaves_y = int(config.screen_height * 0.40)

    # Background depends on which menu screen is currently active.
    if renpy.get_screen("main_menu"):
        add cover_sky_1200("sky_loop")
        add cover_1920("forestbg", yalign=1.0) at parallax_gyro
    else:
        # Options and other menu screens: pure black behind the UI.
        add Solid("#000000")

    # Leaves always render from the same persistent screen instance.
    # Leaves render from the same persistent screen instance (do not restart between menus).
    add Transform("falling_leaves", yoffset=_mm_leaves_y)

    # Tree only on the start screen (keeps the original layering).
    if renpy.get_screen("main_menu"):
        add Transform("tree", zoom=1.00, xalign=0.5, yalign=1.0) at parallax_gyro


screen main_menu():
    tag menu
    zorder 10
    on "show" action Function(md_ensure_menu_scene)


    # Title logo (supports either title_logo.png or images/title_logo.png)
    $ _logo = "images/title_logo.png" if renpy.loadable("images/title_logo.png") else "title_logo.png"
    if renpy.loadable(_logo):
        add _logo:
            xalign 0.5
            yalign 0.15
    text "v[config.version]":
        xalign 0.98
        yalign 0.98
        size 20
        color "#ffffff80" 

    # BUTTONS
    vbox:
        xalign 0.5 
        yalign 0.85 
        spacing 40

        if renpy.newest_slot():
            textbutton "CONTINUE (Load Latest)":
                action Show("menu_fade_to_game", target_action=Continue())
                text_size 50 
                text_color "#ffffff" 
                text_outlines [(2, "#000", 0, 0)] 
                xalign 0.5
                activate_sound "audio/start.ogg" 
            
            textbutton "NEW GAME":
                action Show("menu_fade_to_game", target_action=Start())
                text_size 50 
                text_color "#ffffff" 
                text_outlines [(2, "#000", 0, 0)] 
                xalign 0.5
                activate_sound "audio/start.ogg"

        else:
            textbutton "START STORY":
                action Show("menu_fade_to_game", target_action=Start())
                text_size 50 
                text_color "#ffffff" 
                text_outlines [(2, "#000", 0, 0)] 
                xalign 0.5
                activate_sound "audio/start.ogg"

        textbutton "OPTIONS":
            action ShowMenu("preferences")
            text_size 50 
            text_color "#ffffff" 
            text_outlines [(2, "#000", 0, 0)] 
            xalign 0.5
            activate_sound "audio/option.ogg"


# ==========================================================
# 1B. MAIN MENU -> GAME FADE (3 seconds)
# ==========================================================
transform menu_fade_black:
    alpha 0.0
    linear 3.0 alpha 1.0

screen menu_fade_to_game(target_action):
    zorder 1000
    modal True
    add Solid("#000") at menu_fade_black
    timer 3.0 action [Hide("menu_scene"), target_action]
# ==========================================================
# 2. READING SCREEN
# ==========================================================
screen say(who, what):
    style_prefix "say"

    # Reading theme + text speed affect reading mode only.
    $ _md_theme = getattr(persistent, "md_read_theme", "amoled")
    $ _md_bg = "#000000" if _md_theme == "amoled" else ("#111111" if _md_theme == "dark" else "#ffffff")
    $ _md_fg = "#ffffff" if _md_theme in ("amoled", "dark") else "#000000"

    $ _md_speed = getattr(persistent, "md_text_speed", "normal")
    $ _md_cps = 0 if _md_speed == "instant" else (60 if _md_speed == "fast" else 30)

    add Solid(_md_bg)

    window:
        id "window"
        background None
        yalign 0.5
        xfill True
        xalign 0.0
        xpadding 80

        vbox:
            xalign 0.0
            yalign 0.5
            spacing 20

            if who is not None:
                text who id "who":
                    size 45
                    bold True
                    xalign 0.0
                    color "#ffcc00"

            text what id "what":
                xalign 0.0
                text_align 0.0
                size 45
                color _md_fg
                slow_cps _md_cps
# ==========================================================
# 3. POP-UP MENU (FIXED TO CLOSE ON ESC)
# ==========================================================
screen three_button_menu():
    zorder 200
    modal True

    # Tap background to close
    button:
        action Hide("three_button_menu")
        xfill True
        yfill True
        background "#00000080"

    # Pressing ESC / Android Back again closes this menu.
    key "game_menu" action Hide("three_button_menu")

    # Auto-hide after 6 seconds
    timer 6.0 action Hide("three_button_menu")

    # --- TOP UI (Protected Area) ---
    button:
        action NullAction()
        xfill True
        yalign 0.0
        yoffset 160
        ysize 180
        background None
        at slide_down_top

        add ui_top_image():
            xalign 0.5
            yalign 0.0

        # Uses the SAME text you set with: $ save_name = "Chapter ...\nLocation: ..."
        text "[save_name]":
            xalign 0.5
            yalign 0.55
            text_align 0.5
            size 26
            outlines [(2, "#000", 0, 0)]

    # --- BOTTOM DOCK (Protected Area) ---
    button:
        action NullAction()
        xfill True
        yalign 1.0
        ysize 190
        background None
        at slide_up_down

        add ui_bottom_image():
            xalign 0.5
            yalign 1.0

        hbox:
            xalign 0.5
            yalign 1.0
            yoffset -25
            spacing 60

            textbutton "MEMORIES":
                action [FilePage(1), ShowMenu("save")]
                text_size 40
                text_outlines [(2, "#000", 0, 0)]
                activate_sound "audio/ui.ogg"

            textbutton "BIO":
                action [ Hide("three_button_menu"), ShowMenu("bio_menu") ]
                text_size 40
                text_outlines [(2, "#000", 0, 0)]
                activate_sound "audio/ui.ogg"

            textbutton "OPTIONS":
                action ShowMenu("preferences")
                text_size 40
                text_outlines [(2, "#000", 0, 0)]
                activate_sound "audio/ui.ogg"

transform slide_up_down:
    on show:
        alpha 0.0
        yoffset 260
        parallel:
            easein 0.60 yoffset 0
        parallel:
            easein 0.60 alpha 1.0
    on hide:
        parallel:
            easeout 0.60 yoffset 260
        parallel:
            easeout 0.60 alpha 0.0

transform slide_down_top:
    on show:
        alpha 0.0
        # Move just above the top edge so the animation is visible (no clipping).
        yoffset -260
        parallel:
            easein 0.60 yoffset 0
        parallel:
            easein 0.60 alpha 1.0
    on hide:
        parallel:
            easeout 0.60 yoffset -260
        parallel:
            easeout 0.60 alpha 0.0


# ==========================================================
# ==========================================================
# 4. BIO SCREENS
# ==========================================================
init -2 python:
    # persistent flag used to reveal "Powers & Magic" in Lore once player has opened Biography at least once.
    if not hasattr(persistent, "bio_seen_powers"):
        persistent.bio_seen_powers = False

    # Lore content (edit these any time).
    if "BIO_LORE" not in globals():
        BIO_LORE = {
            "modern_lovers": {
                "title": "Modern Lovers 101",
                "body": "Add your Modern Lovers explanation here.",
            },
            "powers_magic": {
                "title": "Powers & Magic",
                "body": "This appears after you’ve opened a character bio (or when you set persistent.bio_seen_powers = True).",
            },
            "artifacts_items": {
                "title": "Artifacts & Items",
                "body": "Add world-important items here (e.g., Full Moon Pin, Storage Box).",
            },
            "locations_worlds": {
                "title": "Locations & Worlds",
                "body": "Add key locations here (Earth, Zeynad, etc.).",
            },
        }

    # Relationship Web entries: set met=False to hide until they meet them.
    if "BIO_RELATIONSHIPS" not in globals():
        BIO_RELATIONSHIPS = [
            {"name": "Nancy", "label": "Mentor? Rival?", "desc": "", "met": False},
            {"name": "Celina", "label": "Friendly", "desc": "", "met": False},
        ]

    # Secrets list (player unlock hints)
    if "BIO_SECRETS" not in globals():
        BIO_SECRETS = [
            {"title": "Secret #1", "hint": "Finish Celina's route to unlock this extra scene."},
            {"title": "Secret #2", "hint": "Meet (person) to unlock this extra scene."},
        ]

    # Unsolved Questions
    if "BIO_QUESTIONS_OPEN" not in globals():
        BIO_QUESTIONS_OPEN = [
            {"title": "Why did ____ happen?", "body": "Add your mystery thread here."},
        ]
    if "BIO_QUESTIONS_RESOLVED" not in globals():
        BIO_QUESTIONS_RESOLVED = []

    # Lore order in the left list.
    if "BIO_LORE_ORDER" not in globals():
        BIO_LORE_ORDER = [
            "modern_lovers",
            "powers_magic",
            "artifacts_items",
            "locations_worlds",
            "relationships_web",
            "secrets",
        ]


screen bio_profile(char_to_show):
    tag bio
    modal True
    zorder 20000
    layer "overlay"
    key "game_menu" action [ Hide("bio_menu"), Hide("bio_roster"), Hide("bio_profile"), Hide("bio_lore"), Hide("bio_questions") ]

    # Mark "powers seen" so Lore can show Powers & Magic entry.
    on "show" action SetField(persistent, "bio_seen_powers", True)

    add Solid("#000")
    add Solid("#ffffff")  # keep your light profile style
    if char_to_show and hasattr(char_to_show, "bust_file"):
        add char_to_show.bust_file yalign 1.0 xalign 1.0 zoom 1.0

    textbutton "BACK":
        xalign 0.95 yalign 0.05 text_size 40 text_color "#000"
        action [Hide("bio_profile"), Show("bio_roster")]
        activate_sound "audio/ui.ogg"

    vbox:
        xalign 0.1 yalign 0.1 spacing 25
        text char_to_show.full_name size 50 color "#000" bold True
        for key, val in char_to_show.info.items():
            text "[key]: [val]" size 40 color "#000"


screen save():
    tag menu
    use file_slots()

screen load():
    tag menu
    use file_slots()

screen file_slots():
    modal True

    # Background behind the window.
    add Solid("#0b0f14")
    add Solid("#0008")

    # Window frame (supports game/images/ or game/).
    python:
        _mw_path = "images/memories_window_clean.png" if renpy.loadable("images/memories_window_clean.png") else "memories_window_clean.png"
        _iw, _ih = renpy.image_size(_mw_path)
        # Make the window as large as possible, but leave room for the bottom X button.
        _scale = min((config.screen_width * 1.03) / float(_iw), (config.screen_height * 0.88) / float(_ih))
        _mw = int(_iw * _scale)
        _mh = int(_ih * _scale)

        # Slot area inside the window (tuned to fit the inner panel).
        _slot_w = int(_mw * 0.72)
        _slot_h = int(_mh * 0.56)
        _slot_yoff = int(_mh * 0.07)

    add im.Scale(_mw_path, _mw, _mh) xalign 0.5 yalign 0.5

    on "show" action FilePage(1)

    # Close button (bottom center for mobile).
    textbutton "X":
        text_size 70
        xalign 0.5
        yalign 0.92
        xpadding 70
        ypadding 18
        background Solid("#0006")
        hover_background Solid("#0009")
        action Return()
        activate_sound "audio/ui.ogg"

    # Slots container placed inside the window panel.
    fixed:
        xsize _slot_w
        ysize _slot_h
        xalign 0.5
        yalign 0.5
        yoffset _slot_yoff

        vbox:
            spacing 18

            for i in range(1, 6):
                $ _sn = FileSaveName(i, empty="")
                # Empty slots are grey; only saved slots use chapter-theme colors.
                $ _slot_color = "#3b3f48" if not _sn else theme_color_from_save_name(_sn)
                $ _slot_icon = theme_icon_from_save_name(_sn) if _sn else None

                vbox:
                    spacing 6

                    # Slot card.
                    button:
                        action FileAction(i)
                        xsize _slot_w
                        ysize 130
                        background Solid(_slot_color)

                        hbox:
                            xalign 0.05
                            yalign 0.5
                            spacing 22

                            text "[i]" size 54 bold True color "#66ccff" yalign 0.5
                            add Solid("#ffffff30", xsize=2, ysize=92, yalign=0.5)

                            vbox:
                                yalign 0.5
                                spacing 4

                                text FileTime(i, format="%b %d, %Y - %H:%M", empty="Empty Slot"):
                                    size 20
                                    color "#aaaaaa"

                                text FileSaveName(i, empty="Tap 'Overwrite' to save here"):
                                    size 28
                                    bold True
                                    color "#ffffff"
                                    xmaximum _slot_w - 260

                        if _slot_icon:
                            add _slot_icon xalign 0.95 yalign 0.5 xysize (100, 100)

                    # Actions row (NO long black bars).
                    hbox:
                        spacing 14
                        xalign 0.5

                        textbutton "OVERWRITE":
                            action FileSave(i)
                            xsize int(_slot_w * 0.48)
                            ysize 56
                            background Solid("#00000000")
                            hover_background Solid("#00000033")
                            text_color "#d7dbe6"
                            text_size 24
                            text_align 0.5
                            xalign 0.5
                            activate_sound "audio/slot.ogg"

                        textbutton "LOAD":
                            action FileLoad(i)
                            xsize int(_slot_w * 0.48)
                            ysize 56
                            background Solid("#00000000")
                            hover_background Solid("#00000033")
                            text_color "#d7dbe6"
                            text_size 24
                            text_align 0.5
                            xalign 0.5
                            activate_sound "audio/slot.ogg"

# ==========================================================

# 6. CUSTOM POPUP
# ==========================================================
screen confirm(message, yes_action, no_action):
    modal True
    zorder 30000

    # Dim the game behind the prompt.
    add "#00000080"

    # Detect quit confirmation so we can use the custom framed popup only for exit.
    $ _msg = message if isinstance(message, str) else ""
    $ _is_quit = ("quit" in _msg.lower())

    if _is_quit:

        # Use the ornate frame image as the popup background.
        $ _img_pref = "images/exit_window_clean.png"
        $ _img_alt  = "exit_window_clean.png"
        $ _img = _img_pref if renpy.loadable(_img_pref) else _img_alt

        # Fit the popup to the screen while preserving the frame's aspect ratio.
        $ _sw = renpy.config.screen_width
        $ _sh = renpy.config.screen_height
        $ _aspect = 464.0 / 675.0  # frame image aspect (h / w)
        $ _max_w = int(_sw * 0.92)
        $ _max_h = int(_sh * 0.42)
        $ _w = _max_w
        $ _h = int(_w * _aspect)
        if _h > _max_h:
            $ _h = _max_h
            $ _w = int(_h / _aspect)

        # Safe inner padding (relative to the frame size).
        $ _pad_l = int(_w * 0.10)
        $ _pad_r = int(_w * 0.10)
        $ _pad_t = int(_h * 0.28)  # move content lower
        $ _pad_b = int(_h * 0.18)

        $ _content_w = _w - _pad_l - _pad_r
        $ _gap = int(_content_w * 0.06)
        $ _btn_w = int((_content_w - _gap) / 2.0)

        fixed:
            xalign 0.5
            yalign 0.5
            xsize _w
            ysize _h

            add Transform(_img, size=(_w, _h))

            $ _content_h = _h - _pad_t - _pad_b
            $ _text_y = int(_content_h * 0.06)
            $ _btn_y  = int(_content_h * 0.62)

            fixed:
                xpos _pad_l
                ypos _pad_t
                xsize _content_w
                ysize _content_h

                text _msg:
                    xsize _content_w
                    xalign 0.5
                    ypos _text_y
                    text_align 0.5
                    color "#ffffff"
                    bold True
                    size int(_h * 0.070)

                hbox:
                    xsize _content_w
                    xalign 0.5
                    ypos _btn_y
                    spacing _gap

                    textbutton "YES":
                        xsize _btn_w
                        action yes_action
                        text_size int(_h * 0.090)
                        text_color "#ffffff"
                        text_bold True
                        text_xalign 0.5
                        activate_sound "audio/ui.ogg"

                    textbutton "NO":
                        xsize _btn_w
                        action no_action
                        text_size int(_h * 0.090)
                        text_color "#ffffff"
                        text_bold True
                        text_xalign 0.5
                        activate_sound "audio/ui.ogg"


    else:

        # Default confirm styling (unchanged).
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 100

            text message:
                size 50
                text_align 0.5
                xalign 0.5
                color "#ffffff"
                bold True

            hbox:
                xalign 0.5
                spacing 150

                textbutton "YES":
                    action yes_action
                    text_size 60
                    text_color "#ffffff"
                    text_bold True
                    activate_sound "audio/ui.ogg"

                textbutton "NO":
                    action no_action
                    text_size 60
                    text_color "#ffffff"
                    text_bold True
                    activate_sound "audio/ui.ogg"

# ==========================================================
# 7. OPTIONS
# ==========================================================
screen preferences():
    tag menu
    modal True
    zorder 10
    on "show" action Function(md_ensure_menu_scene)
    
    # Opaque black backdrop so the persistent leaves behind don't show through in Options.
    add Solid("#000000")


    # Window image (same vibe as Biography).
    $ _opt_img = "images/options_window_clean.png" if renpy.loadable("images/options_window_clean.png") else None

    # Fit the window to the screen WITHOUT stretching (preserve aspect ratio).
    $ _sw = config.screen_width
    $ _sh = config.screen_height
    $ _max_w = int(_sw * 0.90)
    $ _max_h = int(_sh * 0.80)

    if _opt_img:
        $ _iw, _ih = renpy.image_size(_opt_img)
        $ _scale = min(float(_max_w) / float(_iw), float(_max_h) / float(_ih))
        $ _w = int(_iw * _scale)
        $ _h = int(_ih * _scale)
    else:
        $ _scale = 1.0
        $ _w = _max_w
        $ _h = _max_h

    # Inner safe area (keeps content away from plaque + borders).
    $ _pad_l = int(_w * 0.11)
    $ _pad_r = int(_w * 0.11)
    # Tweak padding so content sits a bit higher and never spills into the bottom ornament.
    $ _pad_t = int(_h * 0.29)
    $ _pad_b = int(_h * 0.22)
    $ _inner_w = _w - _pad_l - _pad_r
    $ _inner_h = _h - _pad_t - _pad_b

    # Leave room for a visible scrollbar inside the frame.
    $ _scroll_w = 26
    $ _vp_gap = 32  # gap between content viewport and scrollbar
    $ _vp_w = _inner_w - _scroll_w - _vp_gap

    # Keep slider thumbs from being clipped at 0%/100% inside the clipped viewport.
    $ _thumb_inset = 28
    $ _bar_w = max(100, _vp_w - (_thumb_inset * 2))

    # Readability helpers (window art is mid-gray).
    $ _t = "#f5f7ff"
    $ _t2 = "#e8ecff"
    $ _outline = [(2, "#000000cc", 0, 0)]
    $ _btn_off = Frame("images/btn_idle.png", 20, 20)
    # Selected state + scrollbar/thumb color: match the window border (light gray).
    $ _btn_on = Frame("images/btn_selected.png", 20, 20)
    $ _btn_text_off = "#f5f7ff"
    $ _btn_text_on = "#0b0b0b"

    # Compact, visible bar styling (prevents the AFM delay bar from eating vertical space).

    fixed:
        xalign 0.5
        # Nudge the whole window slightly upward so top/bottom black space feels balanced.
        yalign 0.47
        xsize _w
        ysize _h

        if _opt_img:
            add Transform(_opt_img, zoom=_scale):
                xalign 0.5
                yalign 0.5
        else:
            add Solid("#111111")

        # Scrollable content inside the window.
        viewport id "md_opts_vp":
            area (_pad_l, _pad_t, _vp_w, _inner_h)
            draggable True
            mousewheel True
            clipping True

            vbox:
                spacing 24
                xfill True

                # --------------------
                # READING
                # --------------------
                text "READING":
                    size 44
                    bold True
                    color _t
                    outlines _outline
                    xalign 0.5
                    textalign 0.5

                null height 10

                text "Theme":
                    size 30
                    color _t2
                    outlines _outline

                hbox:
                    spacing 14

                    textbutton "AMOLED":
                        action SetField(persistent, "md_read_theme", "amoled")
                        background (_btn_on if persistent.md_read_theme == "amoled" else _btn_off)
                        text_color (_btn_text_on if persistent.md_read_theme == "amoled" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                    textbutton "DARK":
                        action SetField(persistent, "md_read_theme", "dark")
                        background (_btn_on if persistent.md_read_theme == "dark" else _btn_off)
                        text_color (_btn_text_on if persistent.md_read_theme == "dark" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                    textbutton "LIGHT":
                        action SetField(persistent, "md_read_theme", "light")
                        background (_btn_on if persistent.md_read_theme == "light" else _btn_off)
                        text_color (_btn_text_on if persistent.md_read_theme == "light" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                null height 12


                text "Text Speed":
                    size 30
                    color _t2
                    outlines _outline

                hbox:
                    spacing 14

                    textbutton "INSTANT":
                        action SetField(persistent, "md_text_speed", "instant")
                        background (_btn_on if persistent.md_text_speed == "instant" else _btn_off)
                        text_color (_btn_text_on if persistent.md_text_speed == "instant" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                    textbutton "FAST":
                        action SetField(persistent, "md_text_speed", "fast")
                        background (_btn_on if persistent.md_text_speed == "fast" else _btn_off)
                        text_color (_btn_text_on if persistent.md_text_speed == "fast" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                    textbutton "NORMAL":
                        action SetField(persistent, "md_text_speed", "normal")
                        background (_btn_on if persistent.md_text_speed == "normal" else _btn_off)
                        text_color (_btn_text_on if persistent.md_text_speed == "normal" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 180
                        yminimum 60

                null height 24

                # --------------------
                # HELPERS
                # --------------------
                text "HELPERS":
                    size 44
                    bold True
                    color _t
                    outlines _outline
                    xalign 0.5
                    textalign 0.5

                null height 10

                text "Auto-forward":
                    size 30
                    color _t2
                    outlines _outline

                hbox:
                    spacing 14

                    textbutton "OFF":
                        action SetField(preferences, "afm_enable", False)
                        background (_btn_on if not preferences.afm_enable else _btn_off)
                        text_color (_btn_text_on if not preferences.afm_enable else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 160
                        yminimum 60

                    textbutton "ON":
                        action SetField(preferences, "afm_enable", True)
                        background (_btn_on if preferences.afm_enable else _btn_off)
                        text_color (_btn_text_on if preferences.afm_enable else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 160
                        yminimum 60

                null height 10

                if preferences.afm_enable:
                    text "Auto-forward delay":
                        size 28
                        color _t2
                        outlines _outline
                    bar value Preference("auto-forward time") style "md_opt_bar":
                        xsize _bar_w
                        xalign 0.5

                    null height 12

                text "Skip Mode":
                    size 30
                    color _t2
                    outlines _outline

                hbox:
                    spacing 14

                    textbutton "SEEN ONLY":
                        action [SetField(persistent, "md_skip_mode", "seen"), Preference("skip", "seen"), Return(), Skip()]
                        background (_btn_on if persistent.md_skip_mode == "seen" else _btn_off)
                        text_color (_btn_text_on if persistent.md_skip_mode == "seen" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 220
                        yminimum 60

                    textbutton "ALL":
                        action [SetField(persistent, "md_skip_mode", "all"), Preference("skip", "all"), Return(), Skip()]
                        background (_btn_on if persistent.md_skip_mode == "all" else _btn_off)
                        text_color (_btn_text_on if persistent.md_skip_mode == "all" else _btn_text_off)
                        text_xalign 0.5
                        text_yalign 0.5
                        text_outlines _outline
                        xminimum 160
                        yminimum 60

                null height 24

                # --------------------
                # AUDIO
                # --------------------
                text "AUDIO":
                    size 44
                    bold True
                    color _t
                    outlines _outline
                    xalign 0.5
                    textalign 0.5

                null height 10

                text "BGM Volume":
                    size 30
                    color _t2
                    outlines _outline
                bar value Preference("music volume") style "md_opt_bar":
                    xsize _bar_w
                    xalign 0.5


                null height 12

                text "UI / SFX Volume":
                    size 30
                    color _t2
                    outlines _outline
                bar value Preference("sound volume") style "md_opt_bar":
                    xsize _bar_w
                    xalign 0.5

                null height 24

                # --------------------
                # SYSTEM
                # --------------------
                text "SYSTEM":
                    size 44
                    bold True
                    color _t
                    outlines _outline
                    xalign 0.5
                    textalign 0.5

                null height 10

                textbutton "RESET SETTINGS":
                    xalign 0.5
                    background _btn_off
                    text_color _btn_text_off
                    text_xalign 0.5
                    text_yalign 0.5
                    text_outlines _outline
                    xminimum 360
                    yminimum 70
                    action Confirm("Reset all settings to default?", Function(md_reset_settings))

                null height 20

        # Visible scrollbar (inside the frame).
        vbar value YScrollValue("md_opts_vp"):
            xpos (_pad_l + _vp_w + _vp_gap)
            ypos _pad_t
            ysize _inner_h
            xsize _scroll_w
            base_bar Solid("#2a2a2a")
            thumb Solid("#c7c7c7")

    # Bottom-centered close button (thumb access).
    textbutton "X":
        xalign 0.5
        yalign 0.93
        text_size 76
        text_color "#ffffff"
        text_outlines [(2, "#000000cc", 0, 0)]
        background None
        action Return()
        activate_sound "audio/ui.ogg"


screen notify_overlay(message, detail=None, duration=2.0):
    # Tap the toast to open a detail popup.
    zorder 500

    button:
        xalign 0.5
        yalign 0.02
        xsize 800
        ysize 150
        background "#003366"
        action [Hide("notify_overlay"), Show("notify_popup", title=message, detail=(detail if detail is not None else message))]

        text message:
            align (0.5, 0.5)
            size 40
            text_align 0.5

    # If the player taps it, this screen hides immediately, so this timer stops.
    timer duration action Hide("notify_overlay")


screen notify_popup(title, detail):
    modal True
    zorder 900

    # Dim background + tap outside to close
    button:
        xfill True
        yfill True
        background "#00000080"
        action Hide("notify_popup")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 520
        background "#111111"
        padding (40, 35)

        vbox:
            spacing 25
            xalign 0.5
            yalign 0.5

            text title:
                size 44
                bold True
                xalign 0.5
                text_align 0.5

            text detail:
                size 30
                xalign 0.5
                text_align 0.5

            textbutton "OK":
                xalign 0.5
                ysize 70
                xsize 240
                background "#222222"
                text_size 34
                action Hide("notify_popup")
                activate_sound "audio/ui.ogg"

# Biography persistent defaults
default persistent.met_celina = False
default persistent.met_denna = False
default persistent.met_tery = False
default persistent.met_nancy = False
default persistent.met_ino = False
default persistent.met_mathew = False

default persistent.secret_1 = False
default persistent.secret_2 = False

default persistent.bio_seen_powers = False


init -5 python:
    # -------------------------
    # Biography system defaults
    # -------------------------

    # Per-character meta. Set persistent flags (e.g., persistent.met_nancy = True) to reveal entries.
    BIO_CHAR_LIST = [
        { "key": "celina", "name": "Celina", "met_var": "met_celina" },
        { "key": "denna",  "name": "Denna",  "met_var": "met_denna"  },
        { "key": "tery",   "name": "Tery",   "met_var": "met_tery"   },
        { "key": "nancy",  "name": "Nancy",  "met_var": "met_nancy"  },
        { "key": "ino",    "name": "Ino",    "met_var": "met_ino"    },
        { "key": "mathew", "name": "Mathew", "met_var": "met_mathew" },
    ]

    # Character pages (you can expand these anytime)
    BIO_CHAR_DATA = {
        "celina": {
            "overview": "Celina — (write overview here).",
            "relationships": "Celina relationships — (write here).",
            "powers": "Celina powers — (write here).",
        },
        "denna": {
            "overview": "Denna — (write overview here).",
            "relationships": "Denna relationships — (write here).",
            "powers": "Denna powers — (write here).",
        },
        "tery": {
            "overview": "Tery — (write overview here).",
            "relationships": "Tery relationships — (write here).",
            "powers": "Tery powers — (write here).",
        },
        "nancy": {
            "overview": "Nancy — (write overview here).",
            "relationships": "Nancy relationships — (write here).",
            "powers": "Nancy powers — (write here).",
        },
        "ino": {
            "overview": "Ino — (write overview here).",
            "relationships": "Ino relationships — (write here).",
            "powers": "Ino powers — (write here).",
        },
        "mathew": {
            "overview": "Mathew — (write overview here).",
            "relationships": "Mathew relationships — (write here).",
            "powers": "Mathew powers — (write here).",
        },
    }

    # Lore entries (NO glossary, NO timeline). Powers & Magic appears only after a powers tab is opened.
    BIO_LORE = {
        "modern_lovers": {
            "title": "Modern Lovers 101",
            "body": "Write your Modern Lovers explanation here.",
        },
        "powers_magic": {
            "title": "Powers & Magic",
            "body": "Global rules of powers (only shown after Powers is discovered in Characters).",
        },
        "artifacts_items": {
            "title": "Artifacts & Items",
            "body": "World-important items (write here).",
        },
        "locations_worlds": {
            "title": "Locations & Worlds",
            "body": "Key places and worlds (write here).",
        },
        "relationships_web": {
            "title": "Relationships Web",
            "body": "",
        },
        "secrets": {
            "title": "Secrets",
            "body": "",
        },
    }

    BIO_LORE_ORDER = [
        "modern_lovers",
        "powers_magic",
        "artifacts_items",
        "locations_worlds",
        "relationships_web",
        "secrets",
    ]

    # Relationship Web list. Each entry can be gated by met_var.
    # You can edit the label/desc anytime.
    BIO_RELATIONSHIPS = [
        { "name": "Nancy",  "label": "Mentor? Rival?", "desc": "(description here)", "met_var": "met_nancy" },
        { "name": "Celina", "label": "Friendly",       "desc": "(description here)", "met_var": "met_celina" },
    ]

    # Secrets list. Each entry can be gated by unlock_var.
    BIO_SECRETS = [
        { "title": "Secret #1", "hint": "Finish Celina's route to unlock this extra scene.", "unlock_var": "secret_1" },
        { "title": "Secret #2", "hint": "Meet (person) to unlock this extra scene.",         "unlock_var": "secret_2" },
    ]

    # Unsolved Questions
    BIO_QUESTIONS_OPEN = [
        { "title": "Why did ____ happen?", "body": "(write the question detail here)" },
        { "title": "What is the rule behind ____?", "body": "(write the question detail here)" },
    ]
    BIO_QUESTIONS_RESOLVED = [
        # Move items here when resolved.
    ]

    def _bio_flag(varname, default=False):
        try:
            return getattr(persistent, varname)
        except Exception:
            return default

    def bio_is_met(met_var):
        return bool(_bio_flag(met_var, False))

    def bio_is_unlocked(unlock_var):
        return bool(_bio_flag(unlock_var, False))



screen bio_menu():
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        if renpy.loadable("images/biography_window_clean.png"):
            _bw_path = "biography_window_clean.png"
        elif renpy.loadable("images/memories_window_clean.png"):
            _bw_path = "memories_window_clean.png"
        else:
            _bw_path = None

        # Use the image size if available; otherwise fall back to a template size.
        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        # Scale to fit on any phone (including 1080x2400) while keeping margins.
        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.90) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (relative to a 900x1500 template):
        # x=146..763, y=198..1297  => w=617, h=1099
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        # Bottom-center close for mobile
        textbutton "X":
            xalign 0.5
            yalign 0.92
            text_size 70
            xpadding 70
            ypadding 18
            action Return()

        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            vbox:
                xalign 0.5
                yalign 0.5
                spacing 24


                textbutton "Characters":
                    xminimum int(_in_w * 0.80)
                    xalign 0.5
                    xpadding 46
                    ypadding 24
                    text_size 46
                    text_color "#F2F2F2"
                    text_hover_color "#FFFFFF"
                    background Solid("#2A2E34AA")
                    hover_background Solid("#3A4048CC")
                    action ShowMenu("bio_roster")
                textbutton "Lore":
                    xminimum int(_in_w * 0.80)
                    xalign 0.5
                    xpadding 46
                    ypadding 24
                    text_size 46
                    text_color "#F2F2F2"
                    text_hover_color "#FFFFFF"
                    background Solid("#2A2E34AA")
                    hover_background Solid("#3A4048CC")
                    action ShowMenu("bio_lore")
                textbutton "Unsolved Questions":
                    xminimum int(_in_w * 0.80)
                    xalign 0.5
                    xpadding 46
                    ypadding 24
                    text_size 46
                    text_color "#F2F2F2"
                    text_hover_color "#FFFFFF"
                    background Solid("#2A2E34AA")
                    hover_background Solid("#3A4048CC")
                    action ShowMenu("bio_questions")



screen bio_roster():
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        if renpy.loadable("images/characters_window_clean.png"):
            _bw_path = "characters_window_clean.png"
        elif renpy.loadable("images/biography_window_clean.png"):
            _bw_path = "biography_window_clean.png"
        elif renpy.loadable("images/memories_window_clean.png"):
            _bw_path = "memories_window_clean.png"
        else:
            _bw_path = None

        # Use the image size if available; otherwise fall back to a template size.
        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.86) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (relative to a 900x1500 template):
        # x=146..763, y=198..1297  => w=617, h=1099
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        # X = go back to Biography main menu
        textbutton "X":
            xalign 0.5
            yalign 0.92
            text_size 70
            xpadding 70
            ypadding 18
            action ShowMenu("bio_menu")

        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            $ _shown_chars = [c for c in BIO_CHAR_LIST if bio_is_met(c.get('met_var', ''))]
            $ _need_scroll = len(_shown_chars) > 6

            if not _shown_chars:
                text "No characters met yet.":
                    xalign 0.5
                    yalign 0.5
                    size 40
                    color "#F2F2F2"
            elif _need_scroll:
                viewport:
                    mousewheel True
                    draggable True
                    ymaximum _in_h

                    vbox:
                        spacing 14
                        xfill True
                        for c in _shown_chars:
                            textbutton c['name']:
                                xminimum int(_in_w * 0.88)
                                xalign 0.5
                                xpadding 44
                                ypadding 18
                                text_size 40
                                text_color "#F2F2F2"
                                text_hover_color "#FFFFFF"
                                background Solid("#2A2E34AA")
                                hover_background Solid("#3A4048CC")
                                action ShowMenu("bio_character_detail", char_key=c['key'])
            else:
                vbox:
                    spacing 14
                    xfill True
                    yalign 0.5
                    for c in _shown_chars:
                        textbutton c['name']:
                            xminimum int(_in_w * 0.88)
                            xalign 0.5
                            xpadding 44
                            ypadding 18
                            text_size 40
                            text_color "#F2F2F2"
                            text_hover_color "#FFFFFF"
                            background Solid("#2A2E34AA")
                            hover_background Solid("#3A4048CC")
                            action ShowMenu("bio_character_detail", char_key=c['key'])

screen bio_character_detail(char_key=None, from_notif=False):
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        _bw_path = None

        # 1) Character-specific detail window (optional).
        # If you add an image like: game/images/detail_window_celina.png
        # it will be used when viewing Celina's page.
        if char_key:
            _candidate = "detail_window_%s.png" % char_key
            if renpy.loadable("images/" + _candidate):
                _bw_path = _candidate

        # 2) Fallback chain.
        if _bw_path is None:
            if renpy.loadable("images/detail_window_clean.png"):
                _bw_path = "detail_window_clean.png"
            elif renpy.loadable("images/characters_window_clean.png"):
                _bw_path = "characters_window_clean.png"
            elif renpy.loadable("images/biography_window_clean.png"):
                _bw_path = "biography_window_clean.png"
            elif renpy.loadable("images/memories_window_clean.png"):
                _bw_path = "memories_window_clean.png"
            else:
                _bw_path = None


        # Use the image size if available; otherwise fall back to a template size.
        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.86) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (relative to a 900x1500 template):
        # x=146..763, y=198..1297  => w=617, h=1099
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

        # Resolve character name + data safely.
        _cname = None
        for _c in BIO_CHAR_LIST:
            if _c.get("key") == char_key:
                _cname = _c.get("name")
                break
        if not _cname:
            _cname = (char_key or "Character").replace("_", " ").title()

        _d = BIO_CHAR_DATA.get(char_key, {})

    default char_tab = "overview"  # overview / relationships / powers

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        # X = go back to the Characters list (NOT back to reading)
        textbutton "X":
            xalign 0.5
            yalign 0.92
            text_size 70
            xpadding 70
            ypadding 18
            action (Return() if from_notif else ShowMenu("bio_roster"))
        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            vbox:
                spacing 14
                xfill True
                yfill True

                frame:
                    xalign 0.5
                    background Solid("#2A2E3480")
                    xpadding 26
                    ypadding 12
                    text _cname size 44 bold True xalign 0.5

                grid 3 1:
                    xfill True
                    xspacing 10
                    # Force a single row of 3 buttons (no wrapping in portrait).
                    textbutton "Overview":
                        xsize int(_in_w / 3.0) - 8
                        action SetScreenVariable("char_tab", "overview")
                        xfill True
                        text_xalign 0.5
                        text_yalign 0.5
                        text_size 28
                        background Solid("#2A2E3480")
                        hover_background Solid("#353A4280")
                        xpadding 16
                        ypadding 10
                    textbutton "Relationships":
                        xsize int(_in_w / 3.0) - 8
                        action SetScreenVariable("char_tab", "relationships")
                        xfill True
                        text_xalign 0.5
                        text_yalign 0.5
                        text_size 28
                        background Solid("#2A2E3480")
                        hover_background Solid("#353A4280")
                        xpadding 16
                        ypadding 10
                    textbutton "Powers":
                        xsize int(_in_w / 3.0) - 8
                        action [ SetField(persistent, "bio_seen_powers", True), SetScreenVariable("char_tab", "powers") ]
                        xfill True
                        text_xalign 0.5
                        text_yalign 0.5
                        text_size 28
                        background Solid("#2A2E3480")
                        hover_background Solid("#353A4280")
                        xpadding 16
                        ypadding 10


                viewport:
                    mousewheel True
                    draggable True
                    ymaximum int(_in_h * 0.78)

                    vbox:
                        spacing 12
                        xfill True

                        if char_tab == "overview":
                            text _d.get("overview", "No overview yet.") size 26
                        elif char_tab == "relationships":
                            text _d.get("relationships", "No relationships yet.") size 26
                        else:
                            text _d.get("powers", "No powers yet.") size 26
screen bio_lore():
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        if renpy.loadable("images/lore_window_clean.png"):
            _bw_path = "lore_window_clean.png"
        elif renpy.loadable("images/biography_window_clean.png"):
            _bw_path = "biography_window_clean.png"
        elif renpy.loadable("images/memories_window_clean.png"):
            _bw_path = "memories_window_clean.png"
        else:
            _bw_path = None

        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.86) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (based on 900x1500 template): x=146..763, y=198..1297
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

        _bio_lore = globals().get("BIO_LORE", {})
        _bio_lore_order = globals().get("BIO_LORE_ORDER", list(_bio_lore.keys()))

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        # Close button (bottom-center for mobile)
        textbutton "X":
            text_size 70
            xalign 0.5
            yalign 0.92
            xpadding 70
            ypadding 18
            action ShowMenu("bio_menu")
        # Content area
        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            $ _shown_lore = [k for k in _bio_lore_order if not (k == 'powers_magic' and not persistent.bio_seen_powers)]
            $ _need_scroll = len(_shown_lore) > 6

            if not _shown_lore:
                text "No lore entries yet.":
                    xalign 0.5
                    yalign 0.5
                    size 40
                    color "#F2F2F2"
            elif _need_scroll:
                viewport:
                    mousewheel True
                    draggable True
                    ymaximum _in_h

                    vbox:
                        spacing 12
                        xfill True
                        for key in _shown_lore:
                            $ _t = _bio_lore.get(key, {}).get('title', key.replace('_', ' ').title())
                            textbutton _t:
                                xminimum int(_in_w * 0.88)
                                xalign 0.5
                                xpadding 44
                                ypadding 18
                                text_size 40
                                text_color "#F2F2F2"
                                text_hover_color "#FFFFFF"
                                background Solid("#2A2E34AA")
                                hover_background Solid("#3A4048CC")
                                action ShowMenu("bio_lore_detail", lore_key=key)
            else:
                vbox:
                    spacing 12
                    xfill True
                    yalign 0.5
                    for key in _shown_lore:
                        $ _t = _bio_lore.get(key, {}).get('title', key.replace('_', ' ').title())
                        textbutton _t:
                            xminimum int(_in_w * 0.88)
                            xalign 0.5
                            xpadding 44
                            ypadding 18
                            text_size 40
                            text_color "#F2F2F2"
                            text_hover_color "#FFFFFF"
                            background Solid("#2A2E34AA")
                            hover_background Solid("#3A4048CC")
                            action ShowMenu("bio_lore_detail", lore_key=key)

screen bio_lore_detail(lore_key=None, from_notif=False):
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        if renpy.loadable("images/detail_window_clean.png"):
            _bw_path = "detail_window_clean.png"
        elif renpy.loadable("images/lore_window_clean.png"):
            _bw_path = "lore_window_clean.png"
        elif renpy.loadable("images/biography_window_clean.png"):
            _bw_path = "biography_window_clean.png"
        elif renpy.loadable("images/memories_window_clean.png"):
            _bw_path = "memories_window_clean.png"
        else:
            _bw_path = None

        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.86) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (based on 900x1500 template): x=146..763, y=198..1297
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

        # safe helpers if you didn't define them in script.rpy
        def bio_is_unlocked(varname):
            if not varname:
                return True
            return bool(getattr(persistent, varname, False))

        def bio_is_met(varname):
            if not varname:
                return True
            return bool(getattr(persistent, varname, False))

        _bio_lore = globals().get("BIO_LORE", {})
        _rels = globals().get("BIO_RELATIONSHIPS", [])
        _secs = globals().get("BIO_SECRETS", [])

        _title = _bio_lore.get(lore_key, {}).get("title", str(lore_key))
        _body  = _bio_lore.get(lore_key, {}).get("body", "")

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        # Back + Close (bottom for mobile)
        textbutton "X":
            text_size 70
            xalign 0.5
            yalign 0.92
            xpadding 70
            ypadding 18
            action (Return() if from_notif else ShowMenu("bio_lore"))
        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            viewport:
                mousewheel True
                draggable True
                ymaximum _in_h

                vbox:
                    spacing 12
                    xfill True

                    if lore_key == "relationships_web":
                        text "Relationships Web" size 44 bold True xalign 0.5

                        for r in _rels:
                            $ _met = bio_is_met(r.get("met_var", ""))
                            if _met:
                                text "[r['name']]: [r['label']]" size 30 bold True
                                if r.get("desc"):
                                    text r["desc"] size 24

                    elif lore_key == "secrets":
                        text "Secrets" size 44 bold True xalign 0.5

                        for s in _secs:
                            $ _ok = bio_is_unlocked(s.get("unlock_var", ""))
                            text "• " + s["title"] size 28
                            if s.get("hint"):
                                text s["hint"] size 22

                    else:
                        frame:
                            xalign 0.5
                            background Solid("#2A2E3480")
                            xpadding 26
                            ypadding 12
                            text _title size 44 bold True xalign 0.5
                        null height 40
                        if _body:
                            text _body size 26
                        else:
                            text "No text yet for this entry." size 24

screen bio_questions():
    tag menu
    modal True
    zorder 20000

    add Solid("#000")

    python:
        # Choose background window art.
        if renpy.loadable("images/detail_window_clean.png"):
            _bw_path = "detail_window_clean.png"
        elif renpy.loadable("images/biography_window_clean.png"):
            _bw_path = "biography_window_clean.png"
        elif renpy.loadable("images/memories_window_clean.png"):
            _bw_path = "memories_window_clean.png"
        else:
            _bw_path = None

        # Use the image size if available; otherwise fall back to a template size.
        if _bw_path:
            _iw, _ih = renpy.image_size(_bw_path)
        else:
            _iw, _ih = (900, 1500)

        # Scale to fit on any phone (including 1080x2400) while keeping margins.
        _scale = min((config.screen_width * 0.98) / float(_iw), (config.screen_height * 0.90) / float(_ih))
        _bw = int(_iw * _scale)
        _bh = int(_ih * _scale)

        # Inner panel area (relative to a 900x1500 template):
        # x=146..763, y=198..1297  => w=617, h=1099
        _in_x = int(_bw * (146.0/900.0))
        _in_y = int(_bh * (198.0/1500.0))
        _in_w = int(_bw * (617.0/900.0))
        _in_h = int(_bh * (1099.0/1500.0))

    default uq_selected = None
    default uq_tab = "open"  # open/resolved

    if _bw_path:
        add im.Scale(_bw_path, _bw, _bh) xalign 0.5 yalign 0.5
    else:
        add Solid("#121318") xalign 0.5 yalign 0.5 xsize _bw ysize _bh

    frame:
        xalign 0.5
        yalign 0.5
        xsize _bw
        ysize _bh
        background None

        textbutton "X":
            xalign 0.5
            yalign 0.92
            text_size 70
            xpadding 70
            ypadding 18
            action ShowMenu("bio_menu")
        frame:
            xpos _in_x
            ypos _in_y
            xsize _in_w
            ysize _in_h
            background None

            vbox:
                spacing 16
                xfill True
                yfill True

                text "Unsolved Questions" size 44 bold True xalign 0.5

                hbox:
                    spacing 16
                    xalign 0.5
                    textbutton "Open":
                        action [ SetScreenVariable("uq_tab", "open"), SetScreenVariable("uq_selected", None) ]
                    textbutton "Resolved":
                        action [ SetScreenVariable("uq_tab", "resolved"), SetScreenVariable("uq_selected", None) ]

                hbox:
                    spacing 24
                    xfill True
                    yfill True

                    frame:
                        xsize int(_in_w * 0.45)
                        ysize int(_in_h * 0.78)
                        background None

                        viewport:
                            mousewheel True
                            draggable True
                            ymaximum int(_in_h * 0.78)

                            vbox:
                                spacing 12
                                xfill True

                                $ _lst = BIO_QUESTIONS_OPEN if uq_tab == "open" else BIO_QUESTIONS_RESOLVED
                                if not _lst:
                                    text "No entries yet." size 24
                                else:
                                    for q in _lst:
                                        textbutton q["title"]:
                                            xfill True
                                            action SetScreenVariable("uq_selected", q)

                    frame:
                        xsize int(_in_w * 0.55)
                        ysize int(_in_h * 0.78)
                        background None

                        viewport:
                            mousewheel True
                            draggable True
                            ymaximum int(_in_h * 0.78)

                            vbox:
                                spacing 12
                                xfill True

                                if uq_selected is None:
                                    text "Select a question." size 28
                                else:
                                    frame:
                                        xalign 0.5
                                        background Solid("#2A2E3480")
                                        xpadding 22
                                        ypadding 10
                                        text uq_selected["title"] size 40 bold True xalign 0.5
                                    null height 18
                                    if uq_selected.get("body"):
                                        text uq_selected["body"] size 24

# ============================================================================
# NEW MOBILE NOTIFICATION SYSTEM (toast + detail popup with optional Check)
# (Added without changing Biography screens)
# ============================================================================

transform _notif_toast_in:
    alpha 0.0
    yoffset -20
    easeout 0.20 alpha 1.0 yoffset 0

transform _notif_card_in:
    alpha 0.0
    xzoom 0.15
    easeout 0.22 alpha 1.0 xzoom 1.0

transform _notif_card_out:
    alpha 1.0
    xzoom 1.0
    easein 0.18 alpha 0.0 xzoom 0.15

transform _notif_btn_in:
    alpha 0.0
    pause 0.23
    easeout 0.12 alpha 1.0

transform _notif_btn_out:
    alpha 1.0
    easein 0.12 alpha 0.0


default _notif_current = None

screen notify_overlay(message=None, title=None, body=None, detail=None, icon=None, goto=None, duration=6.0):
    # Top toast (mobile banner). Tap opens detail popup.
    modal False
    zorder 25000

    $ _title = title if title is not None else message
    $ _body = body if body is not None else ""
    $ _detail = detail
    $ _icon = icon
    $ _goto = goto
    $ _dur = duration if duration is not None else 6.0

    if _title:

        frame:
            at _notif_toast_in
            xalign 0.5
            yalign 0.0
            yoffset 70
            xmaximum 980
            padding (26, 18)
            background Solid("#101010CC")

            button:
                background None
                hover_background None
                action [ SetVariable("_notif_current", {"title": _title, "body": _body, "detail": _detail, "icon": _icon, "goto": _goto}),
                         Hide("notify_overlay"),
                         Show("notify_popup") ]

                hbox:
                    spacing 16
                    yalign 0.5

                    # Icon (left). If missing, show a small placeholder badge.
                    if _icon and renpy.loadable(_icon):
                        add _icon:
                            xysize (48, 48)
                            yalign 0.5
                    else:
                        frame:
                            xsize 48
                            ysize 48
                            background Solid("#FFFFFF22")
                            xalign 0.5
                            yalign 0.5
                            text "!":
                                size 34
                                bold True
                                xalign 0.5
                                yalign 0.5
                                color "#FFFFFF"

                    vbox:
                        spacing 6
                        xfill True

                        text _title:
                            size 34
                            bold True
                            color "#FFFFFF"
                            xalign 0.0

                        if _body:
                            text _body:
                                size 26
                                color "#E6E6E6"
                                xalign 0.0

        timer _dur action Hide("notify_overlay") repeat False


screen notify_popup():
    # Center detail popup. Buttons are OUTSIDE the window below it (Check above OK).
    modal True
    zorder 26000

    # Delay buttons until after the card finishes animating in, and animate out before closing.
    default _notif_btn_ready = False
    default _notif_closing = False
    default _notif_pending_goto = None

    on "show" action [SetScreenVariable("_notif_btn_ready", False), SetScreenVariable("_notif_closing", False), SetScreenVariable("_notif_pending_goto", None)]
    timer 0.23 action SetScreenVariable("_notif_btn_ready", True) repeat False

    if _notif_closing:
        timer 0.20 action [
            # Now actually close and clear the current notification.
            SetVariable("_notif_current", None),
            Hide("notify_popup"),
            _notif_goto_action(_notif_pending_goto),
        ] repeat False


    if _notif_current:

        $ _t = _notif_current.get("title", "")
        $ _d = _notif_current.get("detail", "")
        $ _g = _notif_current.get("goto", None)

        # Size the ornate detail window to the current screen (keeps aspect, avoids stretching).
        python:
            _sw = config.screen_width
            _sh = config.screen_height
            # notification_window_clean.png is 675x670.
            _ratio = 670.0 / 675.0
            _card_w = int(_sw * 0.88)
            _card_h = int(_card_w * _ratio)
            _max_h = int(_sh * 0.62)
            if _card_h > _max_h:
                _card_h = _max_h
                _card_w = int(_card_h / _ratio)
            _pad_l = int(_card_w * 0.10)
            _pad_r = _pad_l
            _pad_t = int(_card_h * 0.18)
            _pad_b = int(_card_h * 0.12)
            _detail_h = int(_card_h * 0.42)

        # Dimming overlay (tap outside closes)
        button:
            xfill True
            yfill True
            background Solid("#00000080")
            action SetScreenVariable("_notif_closing", True)

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 10

            frame:
                if _notif_closing:
                    at _notif_card_out
                else:
                    at _notif_card_in
                xalign 0.5
                xsize _card_w
                ysize _card_h
                padding (_pad_l, _pad_t, _pad_r, _pad_b)
                background Transform("images/notification_window_clean.png", xsize=_card_w, ysize=_card_h, fit="contain")

                vbox:
                    spacing 18
                    xfill True

                    text _t:
                        size 44
                        bold True
                        xalign 0.5
                        text_align 0.5
                        color "#FFFFFF"

                    # Scrollable detail area (fixed height)
                    viewport id "notif_detail_vp":
                        xfill True
                        ysize _detail_h
                        mousewheel True
                        draggable True

                        vbox:
                            xfill True
                            text _d:
                                size 28
                                color "#EDEDED"
                                xalign 0.0
                                text_align 0.0

            # Buttons OUTSIDE the window:
            if _g:
                button:
                    at (_notif_btn_out if _notif_closing else _notif_btn_in)
                    xalign 0.5
                    xminimum 220
                    padding (24, 12)
                    background Solid("#222222F0")
                    sensitive _notif_btn_ready
                    action [SetScreenVariable("_notif_pending_goto", _g), SetScreenVariable("_notif_closing", True)]
                    text "Check":
                        size 30
                        bold True
                        xalign 0.5
                        yalign 0.5
                        color "#FFFFFF"

            button:
                at (_notif_btn_out if _notif_closing else _notif_btn_in)
                xalign 0.5
                xminimum 220
                padding (24, 12)
                background Solid("#222222F0")
                sensitive _notif_btn_ready
                action SetScreenVariable("_notif_closing", True)
                text "OK":
                    size 30
                    bold True
                    xalign 0.5
                    yalign 0.5
                    color "#FFFFFF"
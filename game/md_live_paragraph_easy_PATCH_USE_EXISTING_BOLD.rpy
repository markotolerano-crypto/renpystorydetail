# md_live_paragraph_easy.rpy
# Live-updating paragraph screen that matches your reading screen (centered, size 45, theme-aware)
# and uses your EXISTING quote-bold system (config.say_menu_text_filter / bold_quotes).
#
# Usage in script (inside a label):
#   $ md_ip_set("breakfast", None)
#   call screen md_live_paragraph_easy(
#       "breakfast",
#       [("Biro", "joke"), ("Salamat", "thanks")],
#       """{ip=breakfast}"Ate, breakfast ba ‘to o parusa?"{/ip} ...""",
#       [("thanks", """{ip=breakfast}"Salamat, Ate."{/ip} ...""")]
#   )

init -2 python:

    def md_lp_apply_text_filters(s):
        """
        Apply the same text filter your normal say/menu uses,
        so auto-bold inside "quotes" works here too.
        """
        try:
            f = getattr(config, "say_menu_text_filter", None)
            if callable(f):
                return f(s)
        except:
            pass
        return s

    def md_lp_pick_text(prompt_id, default_text, variants_list=None):
        # variants_list: [("value", "text"), ...]
        v = md_ip_get(prompt_id, None)

        chosen = default_text
        if variants_list:
            for key, txt in variants_list:
                if key == v:
                    chosen = txt
                    break

        return md_lp_apply_text_filters(chosen)

screen md_live_paragraph_easy(prompt_id, choices, default_text, variants_list=None):

    modal True
    zorder 100

    # Theme + text speed (match your screen say).
    $ _md_theme = getattr(persistent, "md_read_theme", "amoled")
    $ _md_bg = "#000000" if _md_theme == "amoled" else ("#111111" if _md_theme == "dark" else "#ffffff")
    $ _md_fg = "#ffffff" if _md_theme in ("amoled", "dark") else "#000000"

    $ _md_speed = getattr(persistent, "md_text_speed", "normal")
    $ _md_cps = 0 if _md_speed == "instant" else (60 if _md_speed == "fast" else 30)

    # Ensure choices exist for this prompt (safe to call repeatedly).
    python:
        md_ip_set_choices(prompt_id, choices)

    # Tap anywhere (not on the inline phrase) to continue.
    key "dismiss" action Return()

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

            text md_lp_pick_text(prompt_id, default_text, variants_list):
                xalign 0.0
                text_align 0.0
                size 45
                color _md_fg
                slow_cps _md_cps
                xfill True
                layout "subtitle"

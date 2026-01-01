# --- 1. PYTHON INIT & TEXT FILTER ---
init python:
    import re
    
    # This automatically bolds text inside quotes
    def bold_quotes(text):
        return re.sub(r'"(.*?)"', r'{b}"\1"{/b}', text)

    # Apply the filter
    config.say_menu_text_filter = bold_quotes

    # Gyro Parallax Function
    def gyro_func(trans, st, at):
        try:
            reading = renpy.input.get_accelerometer()
            if reading:
                x, y, z = reading
                trans.xoffset = x * -20.0
                trans.yoffset = y * 20.0
            else:
                trans.xoffset = 0
                trans.yoffset = 0
        except:
            pass
        return 0

# --- 2. CONFIGURATION ---


# --- 2C. IMAGE FIT HELPERS (1080x1920 assets -> 1080x2400 screen) ---
init python:
    # Stretches a displayable to exactly fill the current screen.
    # On 1080x2400, 1080-wide assets will only stretch vertically (no side distortion).
    # Scales/crops to fill the screen WITHOUT distortion.
    # Use these for 1080x1920 assets when the project is 1080x2400.
    def cover_from_base_height(d, base_h, yalign=0.5):
        z = float(config.screen_height) / float(base_h)
        return Transform(d, zoom=z, xalign=0.5, yalign=yalign)

    # 1080x1920 portrait assets -> fill 1080x2400 by zooming (1.25x) and cropping sides.
    def cover_1920(d, yalign=0.5):
        return cover_from_base_height(d, 1920.0, yalign=yalign)

    # Wide sky (3207x1200) -> scale by height only, keep it wide (no forced xsize).
    def cover_sky_1200(d):
        return cover_from_base_height(d, 1200.0, yalign=0.0)
# --- 2B. CHAPTER UI IMAGE HELPERS ---
init python:
    import re

    def _chapter_num_from_save_name():
        """
        Extracts the chapter number from save_name, expecting something like:
            "Chapter 1: ...\nLocation: ..."
        Returns 1 if not found.
        """
        try:
            s = save_name or ""
        except Exception:
            s = ""
        m = re.search(r"Chapter\s+(\d+)", s, re.I)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return 1
        return 1

    def ui_top_image():
        ch = _chapter_num_from_save_name()
        if 1 <= ch <= 14:
            return "DefaultUITop.png"
        elif 15 <= ch <= 26:
            return "CelinaUITop.png"
        elif 27 <= ch <= 40:
            return "DennaUITop.png"
        elif 41 <= ch <= 51:
            return "NancyUITop.png"
        return "DefaultUITop.png"

    def ui_bottom_image():
        ch = _chapter_num_from_save_name()
        if 1 <= ch <= 14:
            return "DefaultUIBottom.png"
        elif 15 <= ch <= 26:
            return "CelinaUIBottom.png"
        elif 27 <= ch <= 40:
            return "DennaUIBottom.png"
        elif 41 <= ch <= 51:
            return "NancyUIBottom.png"
        return "DefaultUIBottom.png"

# --- Save Slot Theme Helpers (for Memories UI) ---
init python:
    # Slot colors by chapter theme
    _THEME_COLORS = {
        "default": "#1e7a35",  # green
        "celina":  "#1a2b8a",  # blue
        "denna":   "#8a1a1a",  # red
        "nancy":   "#b12a8a",  # pink
    }

    # Optional mini-icons shown on the right side of each slot.
    # If a file isn't present, it simply won't show (no crash).
    _THEME_ICONS = {
        "default": "images/DefaultMini.png",
        "celina":  "images/CelinaMini.png",
        "denna":   "images/DennaMini.png",
        "nancy":   "images/NancyMini.png",
    }

    def theme_from_save_name(s):
        """Return theme key based on chapter number inside a save_name string."""
        s = s or ""
        m = re.search(r"Chapter\s+(\d+)", s, re.I)
        try:
            ch = int(m.group(1)) if m else 1
        except Exception:
            ch = 1

        if 1 <= ch <= 14:
            return "default"
        elif 15 <= ch <= 26:
            return "celina"
        elif 27 <= ch <= 40:
            return "denna"
        elif 41 <= ch <= 51:
            return "nancy"
        return "default"

    def theme_color_from_save_name(s):
        return _THEME_COLORS.get(theme_from_save_name(s), _THEME_COLORS["default"])

    def theme_icon_from_save_name(s):
        icon = _THEME_ICONS.get(theme_from_save_name(s))
        if not icon:
            return None
        try:
            return icon if renpy.loadable(icon) else None
        except Exception:
            return None

    # Custom notification helper (clickable toast -> detail popup)
    # Custom notification helper (mobile toast -> detail popup, with optional Check link)
    def custom_notify(*args, **kwargs):
        """
        Usage:
          custom_notify(title, body=None, detail=None, icon=None, goto=None, duration=6.0)
        Backwards compatible with older calls:
          custom_notify(message, detail=None, duration=...)
        """
        duration = kwargs.get('duration', 6.0)
        icon = kwargs.get('icon', None)
        goto = kwargs.get('goto', None)
        # Allow both 'detail' and 'details' keyword spellings
        detail_kw = kwargs.get('detail', kwargs.get('details', None))
        body_kw = kwargs.get('body', None)
    
        title = None
        body = None
        detail = None
    
        if len(args) == 0:
            title = kwargs.get('title', None)
            body = body_kw
            detail = detail_kw
        elif len(args) == 1:
            title = args[0]
            body = body_kw
            # old style: custom_notify(message, detail=...)
            detail = detail_kw
        elif len(args) == 2:
            # new style: (title, body) OR old style: (message, detail)
            title = args[0]
            # If caller ALSO passed detail keyword, treat args[1] as body.
            if 'detail' in kwargs or 'details' in kwargs or body_kw is not None:
                body = args[1]
                detail = detail_kw
            else:
                body = None
                detail = args[1]
        else:
            title = args[0]
            body = args[1]
            detail = args[2]
    
        if body is None or (isinstance(body, str) and body.strip() == ""):
            # Keep the planned two-line toast look when there are details.
            if detail and (not isinstance(detail, str) or detail.strip() != ""):
                body = "Tap for more details!"
            else:
                body = ""
    
        # If detail is blank, fall back so popup isn't empty.
        if detail is None or (isinstance(detail, str) and detail.strip() == ""):
            detail = body if body else title
    
        renpy.show_screen(
            "notify_overlay",
            title=title, body=body, detail=detail, icon=icon, goto=goto, duration=duration
        )
define menu_fade = Fade(1.5, 0.0, 1.5, color="#000")

init python:
    # --- CONTROLS FIX ---
    # I have REMOVED the 'dismiss' and 'rollback' lines.
    # Clicking to continue and Swiping to rollback will now work normally.
    
    # 1. Enable ESC / Right Click / Back Button
    config.keymap['game_menu'] = ['K_ESCAPE', 'K_MENU', 'mouseup_3', 'K_AC_BACK'] 
    
    # 2. THE ESC FIX: 
    # This tells Ren'Py to open your menu ON TOP of the text,
    # instead of hiding the text (which is the default behavior).
    config.game_menu_action = Show("three_button_menu")

    # 3. ANDROID BACK FIX:
    # Ensure the Android Back gesture/button does NOT rollback.
    _rb = list(config.keymap.get('rollback', []))
    if 'K_AC_BACK' in _rb:
        _rb.remove('K_AC_BACK')
        config.keymap['rollback'] = _rb

    # 4. SWIPE UP = ROLLBACK (backtrack)  [Option 1 controls]
    _gest = dict(getattr(config, 'gestures', {}) or {})
    _gest['n'] = 'rollback'
    # 5. (Android gesture-nav safe fallback) SWIPE DOWN = OPEN DOCK/TOP UI
    # This avoids relying on Android's edge-swipe Back gesture, which some phones reserve for leaving the app.
    _gest['s'] = 'dock_menu'
    config.gestures = _gest

    # 6. HARD CATCH for Android Back: handle K_AC_BACK in the underlay, so Ren'Py consumes it
    # before Android treats it as "leave the app".
    def _toggle_dock_from_back():
        # Only during gameplay, not while a menu is already open.
        if renpy.context()._menu:
            return

        if renpy.get_screen("three_button_menu"):
            renpy.hide_screen("three_button_menu")
        else:
            renpy.show_screen("three_button_menu")

    # Map a dedicated event name to the Android Back keysym.
    config.keymap['dock_menu'] = ['K_AC_BACK']

    # Underlay keymap is always present during interactions.
    config.underlay.append(renpy.Keymap(dock_menu=_toggle_dock_from_back))

    config.version = "1.0"

    # Transitions
    config.after_load_transition = menu_fade
    config.end_splash_transition = Dissolve(0.5)
    config.enter_transition = Dissolve(0.5)
    config.exit_transition = Dissolve(0.5)
    config.window_show_transition = Dissolve(2.0)

# --- 3. CLASS DEFINITIONS ---
init python:
    class CharBio:
        def __init__(self, name, full_name, icon_file, bust_file):
            self.name = name
            self.full_name = full_name
            self.icon_file = icon_file
            self.bust_file = bust_file
            self.met = False
            self.info = {}

        def unlock(self):
            if not self.met:
                self.met = True
                renpy.show_screen("notify_overlay", message="New Character: " + self.name)
        
        def unlock_info(self, key, value):
            if key not in self.info:
                self.info[key] = value
                renpy.show_screen("notify_overlay", message="Bio Updated: " + self.name)

# --- 4. TRANSFORM DEFINITIONS ---
transform parallax_gyro:
    subpixel True
    function gyro_func

# --- 5. IMAGE DEFINITIONS ---
image forestbg = "forestbg.png" 
image tree = "tree.png"
image bg_bio       = Solid("#1a0b2d")
image bg_memories  = Solid("#0b2d1a")
image bg_options   = Solid("#2d0b0b")

image sky_raw = "sky.jpg"
image sky_fixed = "sky_raw"

image sky_loop:
    HBox("sky_fixed", "sky_fixed")
    subpixel True
    xpos 0
    linear 60.0 xpos -1080 
    repeat

image leaf_particle = "leaf.png"
image falling_leaves = SnowBlossom("leaf_particle", count=20, border=50, xspeed=20, yspeed=100, start=0, fast=True, horizontal=False)

# Replace "logo.png" with your file name.
# xalign 0.5 / yalign 0.5 puts it dead center.

image splash_logo_1 = Transform("images/splash.png", xalign=0.5, yalign=0.5)
image splash_logo_2 = Text("WARNING: CONTAINS FANTASY", size=50, xalign=0.5, yalign=0.5)

# --- 6. GAME VARIABLES ---
default char_aria = CharBio("Aria", "Aria the Mage", Solid("#f00", xsize=200, ysize=200), Solid("#f00", xsize=600, ysize=900))
default char_leon = CharBio("Leon", "Leon the Knight", Solid("#00f", xsize=200, ysize=200), Solid("#00f", xsize=600, ysize=900))

# --- 7. SPLASH SCREEN ---
label splashscreen:
    scene black
    pause 0.5
    show splash_logo_1 with dissolve
    pause 1.0
    hide splash_logo_1 with dissolve
    show splash_logo_2 with dissolve
    pause 1.0
    hide splash_logo_2 with dissolve
    pause 0.5
    return 

# --- 8. START LABEL (STORY) ---
label start:
    # --- BIOGRAPHY TEST DATA (remove later) ---
    python:
        # Mark some characters as met so they appear in Characters/Relationships lists.
        persistent.met_celina = True
        persistent.met_denna  = True
        persistent.met_tery   = True
        persistent.met_nancy  = True
        persistent.met_ino    = True
        persistent.met_mathew = True

        # Pretend the player has seen Powers already (so Lore -> Powers & Magic appears).
        persistent.bio_seen_powers = True

        # Sample Relationship Web (shown only if 'met' is True).
        BIO_RELATIONSHIPS = [
            {"name": "Nancy",  "label": "Mentor? Rival?", "desc": "She helps… but sometimes it feels like a test.", "met": persistent.met_nancy},
            {"name": "Celina", "label": "Friendly",       "desc": "Warm, playful, but gets intense when jealous.", "met": persistent.met_celina},
            {"name": "Denna",  "label": "Ally",           "desc": "Smart and dangerous—always planning something.", "met": persistent.met_denna},
        ]

        # Sample Secrets list (you can later gate these with your own flags).
        BIO_SECRETS = [
            {"title": "Secret #1", "hint": "Finish Celina's route to unlock this extra scene."},
            {"title": "Secret #2", "hint": "Meet a certain person to unlock this extra scene."},
        ]

        # Sample Unsolved Questions (Open/Resolved tabs).
        BIO_QUESTIONS_OPEN = [
            {"title": "Why did Celina come to Earth?", "body": "There are hints about a mission, but the real reason isn't confirmed yet."},
            {"title": "What is the Storage Box really capable of?", "body": "People say time stops inside… but what are the limits?"},
        ]
        BIO_QUESTIONS_RESOLVED = [
            {"title": "What does the Full Moon Pin mean?", "body": "Giving it to your partner is basically a marriage proposal."},
        ]

        # Lore pages (these keys MUST match what's used in screens.rpy).
        BIO_LORE = {
            "modern_lovers": {
                "title": "Modern Lovers 101",
                "body": "Modern Lovers are an extraordinary group from another world. Their mission centers on finding a partner and giving unconditional love.",
            },
            "powers_magic": {
                "title": "Powers & Magic",
                "body": "Some characters have abilities with rules and limits. This entry is shown only after Powers is discovered in the character pages.",
            },
            "artifacts_items": {
                "title": "Artifacts & Items",
                "body": "Important objects include the Full Moon Pin and the Storage Box (time stops inside).",
            },
            "locations_worlds": {
                "title": "Locations & Worlds",
                "body": "Earth (modern world) and Zeynad (Celina's world) are connected by secrets and rules you’ll learn later.",
            },
            # These two are handled specially by the screen (lists above), but keeping titles helps the left menu.
            "relationships_web": {"title": "Relationships Web", "body": ""},
            "secrets": {"title": "Secrets", "body": ""},
        }

        BIO_LORE_ORDER = [
            "modern_lovers",
            "powers_magic",
            "artifacts_items",
            "locations_worlds",
            "relationships_web",
            "secrets",
        ]
    # --- END BIOGRAPHY TEST DATA ---

    # --- NOTIFICATION UI TEST (remove later) ---
    python:
        custom_notify(
            "Achievement Update",
            "You just unlocked a new achievement! Tap for more details!",
            detail="Achievement: Modern Lovers 101\n\nReward: +50 XP\nDescription: Finished the intro test.",
            goto=("lore", "modern_lovers"),
            duration=6.0
        )
    # --- END NOTIFICATION UI TEST ---

    scene black 
    
    # Enhanced Save Info
    $ save_name = "Chapter 1: The Beginning\nLocation: Dark Forest"
    
    # Hard pause to force pacing
    pause 1.0 
    
    # Text box dissolves in
    window show 

    # START OF STORY
    '"Tery! Tery! Gising na!"'

    'Naradaman kong may yumuyugyog sa katawan ko ng maraming beses. Ang gulo naman. "Gising na sabi eh!" Sigaw nito habang ako\'y ginugulo sa aking pagtulog. Hindi pa rin ako kumikilos. Ginigising na ako ng Ate kong si Eliza, ngunit ayoko pang bumangon.\n\nNakakatamad kaya. Tapos napaka-aga pa. "10 minutes pa Ateee.." Sabi kong tamad na boses. Hinahayaan ko lang siyang yugyugin ako. Patigasan. Pero ilang sandali lang ay tumigil din ang pagyu-yugyog niya sa\'kin. Sumuko na siya agad?'

    'Natuwa tuloy ang mga mata ko at nagsimulang makatulog muli. Pero ilang saglit lang ay nabigla nalang ako ng naramdaman kong umupo siya sa\'kin. Doon ko naaalala na hindi pala ganon lang kadaling sumusuko si Eliza. Napadilat agad at siya ang nakita ko sa harap ko.'

    'Naka-upo. Nakangiti.'

    '"A-Anong sa tingin mong g-ginagawa mo Ate?" Na-uutal kong sabi sa kanya. Paano ka hindi magugulat kung naka-upo siya sayo?! "Ayaw mo pa kasing gumising eh!" Masungit niyang sagot.'

    'Ito nanaman siya, nagiging isip bata kahit alam niyang siya ang mas nakatatanda sa\'ming dalawa. "Oo na basta umalis ka na dyan nang makabangon na ko." Sabi kong hirap na makatingin sa kanya.\n\nIsa lang ang pumapasok sa isip ko ngayon.'

    'ATE KO BA TALAGA SIYA??'

    'Tinitigan ko siya ng masama. Yun na ang sign para matauhan naman siya. Mala-late ako sa school kapag hinayaan ko lang kaming ganito. "Hmp. Sungit." Pagkatapos ay sa wakas, naka-kawala na rin ako sa sitwasyon na iyon.\n\n'

    'Naglakad siya palabas pero biglang napahinto ng mukhang may nakalimutan pa siyang sabihin. "Nakahanda na breakfast mo. Pati na rin yung uniform mo nandyan na rin, na-iplantsa ko na." Her usual saying araw-araw. "Thanks, Ate." Ngiting sabi ko. Bumawi lang siya sa ngiti ko\'t pagkatapos ay lumabas na siya sa aking kwarto nang tuluyan.\n\nPagbaba ko rin sa kusina, naamoy ko na agad ang niluto niya. "Sana hotdog… sana hotdog…" bulong ko habang lumalapit. Pagtingin ko sa mesa, gulay nga.'

    $ md_ip_set("breakfast", None)

    call screen md_live_paragraph_easy(
        "breakfast",
        [("Biro", "joke"), ("Salamat", "thanks")],
        """{ip=breakfast}"Ate, breakfast ba ‘to o parusa?"{/ip} Biro ko, sabay upo. "Parusa sa hindi marunong gumising ng maaga." Balik niya agad, naka-smirk pa. Napailing na lang ako habang kumakain. Kahit anong reklamo ko, at the end of the day, masarap pa rin gawa ni Ate. Kung may contest nga lang ng "pinakamasarap na lutong gulay", feeling ko panalo agad si Ate — kahit ako lang judge.""",
        [
            ("thanks", """{ip=breakfast}"Salamat, Ate."{/ip} pasalamat ko sa kanya. Ngumiti lang siya sa'kin habang patuloy pa ring nag-aasikaso para sa araw naming ito. May pasok din siya sa kanyang trabaho.""")
        ]
    )
    'Alam ko, sobra akong bias. Pero siya lang naman ang dahilan kung bakit hindi ako lumalabas ng bahay ng gutom. At pero ulit sa totoo lang, grabe siya. Daig pa Parents namin. Siya na kasi ang tumatayo bilang breadwinner, plus ilaw ng tahanan pa dito sa\'ming bahay. Napaka-swerte ko talaga dahil siya ang naging Ate ko.\n\nGaano na kaya ako katamad ngayon kung wala siya sa tabi ko sa mga sandaling ito? Wala akong makakapitan kahit sino man. Ang relatives namin ay hindi kami matulungan dahil naghihirap din sila. Pero gumagawa naman sila ng paraan para matulungan kami kahit paano.'

    'Ngayon ay 17 na ko.'

    'Si Ate Eliza nama\'y isang taon lang ang agwat sa\'kin. Siya na ang nag-aasikaso sa\'kin simula pa noong nawala ang parents namin 8 years ago. It was a car accident. Dapat ay magce-celebrate lang kami noong araw na iyon dahil nagkaroon kami ni Eliza ng maraming recognitions sa school. Nakasakay kami sa kotse ni Papa na siyang nagda-drive papunta sa kakainan naming restaurant. Sobrang excited namin ni Ate noon dahil minsan lang kami mapunta sa isang kainan.\n\nHanggang sa, biglang may humarurot na kotseng padaan sa kabilang lane na ka-intersect namin kaya... Doon nawala ang lahat para sa\'min ni Ate.'

    'It was so sudden and unbelievable.'

    'Nagluksa kami at nahirapan kaming dalawa ni Ate. May ilang relatives na tumulong paminsan-minsan, pero sila rin ay may sariling problema at hirap sa buhay. Kaya sa huli, kami pa rin dalawa ang totoong magkasama in the end. It felt so hopeless, and it was almost like we had to give up...\n\nPero noong isang araw, nagbago si Ate Eliza. Naging positive siya, and I don\'t even know what the reason is behind why she became like this until now. She never told me why. Basta bigla nalang siyang naging ganito.'

    'Hindi nagtagal ay naging ganon din ako. Tinanggap nalang ang katotohanan at ipinagpatuloy ang buhay namin. Hanggang sa ito, ganito na kami ngayon ni Ate Eliza. Normal na ang aming buhay. Walang problema. Masaya at kuntento na. Basta magkasama kaming dalawa.\n\nKaso, may nagbago sa kanya. Ayaw niya kong tumutulong sa gawaing bahay. At kapag sinubukan ko\'y napapagalitan niya ako at nagkakatampuhan lang kami. She was never like this before.'

    'Tapos ang isa pa sa mga ikinagulat ko\'y.. Huminto siya sa kanyang pag-aaral simula noong makapagtapos siya ng Mid High. Gusto niya ako lamang daw at siya na lamang ang magta-trabaho para sa\'ming dalawa.\n\nIt was so unfair. Siya ang gumagawa lahat habang ako\'y ganito lamang, nagpapakasarap. Nagta-trabaho siya ngayon sa isang fast food restaurant para lang makapag-aral ako at makapagtapos ng aking pag-aaral.'

    'She sacrificed her future. Mas pinili niya ang future ko.'

    'Lahat ginagawa niya. Wag lang ako magreklamo kahit isang beses sa kanya. Nakaramdam tuloy ako ng malaking guilt kasi hindi kaagad ako gumising noong nandito si Ate Eliza.\n\nMinsan naiisip ko, paano kung hindi nawala sila Mama at Papa? Siguro nabigyan pa si Ate ng pagkakataon na ma-enjoy ang buhay tulad ko sa school. Pero pinili niyang akuin lahat para sa’min. Sa harap ng iba, lagi siyang kalmado, organized, parang kaya niya lahat. Pero sa bahay, napapansin ko rin yung mga gabing nakatulala lang siya, hawak yung picture frame ni Mama habang pinipilit ngumiti pag nahuli ko siyang ganon.'

    'Hindi ko sinasabi sa kanya, pero ramdam ko. Kahit pagod na siya, kahit gusto niya ring bumigay, lagi niya akong inuuna. Minsan na-guilty ako na ako yung bunso at wala akong magawa kundi tumingin lang. Kaya siguro kahit anong sermon o utos niya, hindi ako makapagreklamo. Kahit minsan parang nanay ko na siya, alam kong ginagawa niya ‘yon dahil mahal niya ako. Minsan nahuhuli ko siyang inaabot yung baon ko kahit siya yung walang kinakain—kunwari pa na hindi ko napapansin. Ang kulit lang, kasi kunyari hindi ako nakakapansin. AT ulit kong isip sa sarili ko, kung wala talaga si Ate beside me right now, matagal na akong palpak. Siya ang lagi kong alarm clock, tagapagsalba, at taga-bantay.'

    'Next time! Gigising na rin ako nang maaga! Promise!'

    'O sige na\'t tama na \'tong pag mumuni-muni ko. Naligo, nagsepilyo at sinuot ang aking uniform. Well done Tery! Pumopogi nanaman ang lalaking nakatingin sa harap ng salamin! Minsan naiisip ko, kung may award para sa pinaka-handsome sa bahay… well, ako lang naman ang kandidato. Automatic panalo.\n\nPagkatapos kong mangarap nang gising sa salamin ay hinarap ko na ang katotohanan. Binuksan ko na ang pinto sa aking kwarto palabas at bababa na dapat ako nang may nakita akong hindi inaasahan..'

    '"T-Tery?!" Sigaw ng Ate kong nabibigla. "S-Sorry Ate!!" Sigaw ko rin sabay pasok sa kwarto then.. *slam!*'

    'Sinara ko ng malakas. Hay nako! Hindi talaga siya nag-iingat! Maraming beses na rin itong nangyari at kahit kailan ay hindi ako masanay... At hindi pwedeng masanay Tery! Siya si Eliza Sorrells! Siya ang nag-iisang kapatid ko!\n\nNag-iinit nanaman tuloy ang mukha ko. Paano ba naman ay nakita ko ang Ate kong nakataklop lang ng twalya. Sa tuwing umaga ay sabay kasi kaming umaalis ng bahay dahil same kami ng time nang pagpasok sa school ko at sa trabaho niya.'

    'Katatapos lang niya sigurong maligo. Fresh na fresh at ang bango-bango niya…. Sinampal ko ng tatlong beses ang aking mukha nang maisip ko ang mga kalokohan kong ito.'

    'Maka-alis na nga! Pero...!'

    'Palabas na sana ako ng gate nang may tumawag sa akin. "Tery." Napahinto ako. Si Tita Edith pala. Nasa labas siya ng gate nila, nagwawalis ng bakuran.\n\nSiya ang nakababatang kapatid ni Papa. Noong nawala ang mga magulang namin, naglahong parang bula ang lahat ng kamag-anak namin. Takot silang mahingan ng tulong o obligahing kupkupin kaming magkapatid. Pero si Tita Edith... siya lang ang hindi umalis. Kahit na hikahos din siya sa buhay, hindi niya kami natiis.'

    'Ambait pa niya. Pinagwawalis pa kami sa labas. "Po? Good morning po Tita." Bati ko. Tumigil siya sa pagwawalis at lumapit sa akin. Sinuri niya ang uniform ko. "Ang aga mo yata? Hindi ka ba sasabay sa Ate mo?"\n\nErm. I Suddenly remembered what happened inside the house. "M-Mauna na po ako, may tatapusin pa po kasi ako sa school." Pagsisinungaling ko.'

    '"Nag-almusal ka na ba? Amoy na amoy ko ang niluluto ng Ate mo mula dito ah." Natigilan ako. Naamoy niya pala yung niluluto ni Eliza. Nakakonsensya, pero hindi ko pa kayang harapin si Eliza ngayon.\n\n"Ah... O-Opo.. Pero kakain din po ko sa school mamaya. Male-late na po kasi ako."'

    'Napailing siya. "Hay naku. Sayang naman yung niluto. Kamukhang-kamukha mo talaga ang Papa mo. Ang tigas ng ulo, aalis ng walang laman ang tiyan."\n\nDumukot siya sa bulsa ng duster niya at may inabot na bente pesos sa akin. Luma at gusot na ang pera. "Tita, wag na po. May baon naman ako—"'

    '"Kunin mo na. Pandagdag mo dyan sa school." Pinilit niya sa kamay ko ang pera. "Nangako ako sa Papa mo... na babantayan ko kayo hangga\'t kaya ko. Ayokong nalilipasan kayo ng gutom."\n\nNatahimik ako. Ito ang rason kung bakit hindi ko siya matanggihan. "Salamat po, Tita..."'

    '"Sige na, pumasok ka na. Ako nalang babati sa Ate mo."'

    'Umalis ako habang hawak ang gusot na bente pesos. Mabigat sa loob, pero mainit sa pakiramdam. Alam kong hirap din siya, pero pilit niyang tinutupad ang pangako niya kay Papa.'

    # POV CHANGE

    centered "{size=+10}ELIZA{/size}"

    '"Thanks Ate."\n\nTalaga nga naman si Kuya..'

    'Super kuntento na ko sa buhay naming dalawa ni Tery. I\'m super happy na ganito kami. At ayokong sad siya. Gusto ko parati siyang happy.\n\nGusto ko ma-enjoy ni Tery ang kabataan niya hanggang sa dumating ang time na kailangan niya na ring harapin ang mundong ito. Hindi naman sa wala akong tiwala or confident kay Kuya Tery. Ayoko lang talagang maranasan niya ito agad.'

    'Kaya ako muna ang kikilos para sa\'ming dalawa..'

    'Pumasok agad ako sa aking kwarto at nagmadaling nagbihis kasi malalate na talaga ako sa work ko. Bakit ba! Eh minsan niya lang sabihin iyon sa\'kin eh!'

    'Ay wait! Nakalimutan ko yung pinapakulo kong tubig!!'

    'Kaya kahit hindi pa ko tapos ay nagtakip lang ako ng tuwalya para makalabas. Pero noong lumabas naman ako..\n\nNarinig ko ang pagbukas ng pinto ng kwarto ni Tery, kaya napaharap agad ako sa kanya.'

    'N-Nakita nanaman niya kong naka-twalya lang nanaman!! "T-Tery?!" Anong gagawin ko?! Nakita kong na-iilang siya sobra at hindi alam kung saan titingin. "S-Sorry Ate!!" Sigaw niya sabay pasok sa kwarto then..'

    'Slam! Sinara niya ng malakas. O-Ok lang ang lahat... Diba?'

    'Hinayaan ko nalang at nagmadali ako sa baba upang patayin ang stove at pagkatapos ay bumalik agad sa kwartong nagmamadali. Bakit ba parating natsa-tsambahan ni Tery na kapag lalabas ako\'y ganon..?'

    'Kasalanan mo Eliza! Hindi ka kasi nag-iingat! Makakalimutin ka!'

    'Pagkatapos ay hindi pa rin yata siya lumalabas dahil sumilip din ako sa baba at wala akong nakitang Tery. Mukhang dahil yata na-ulit nanaman ito!'

    'Kasalanan ko talaga! I\'m sorry!'

    'Nagmadali akong kumatok sa kwarto niya. "Tery?! Wala lang iyon sa\'kin promise!!" Sigaw ko habang hinihintay siyang sumagot.'

    'Ngunit hindi pa rin siya sumasagot! Malaki na siguro galit niya sa\'kin huhuhu!'

    '"Sorry na talaga Tery! Please lumabas ka na!" Ulit kong panghihingi nang sorry sa kanya.'

    'Wala talaga! "O-Ok lang na nakita mo iyon Tery!" Pagkatapos ay hinintay ko muli at baka ito\'y sumagot na.'

    '"..." Sobrang tahimik talaga! Nagkulong ba siya?! Hindi kaya..-! Wait!! Wait lang, wait lang.. Wag mong sabihing..'

    'Para kumpirmahin ay binuksan ko ang pinto. "Sabi ko na nga ba eh!!"'

    '"Iniwan nanaman niya ako! Pumasok agad siya!!" Hay nako Tery! Pero in the end hinayaan ko na since magiging awkward nanaman ang interaksyon namin. Lalo na later.'

    'Nang masigurado kong nakaalis na siya, dahan-dahan akong napaupo sa sofa. Nawala bigla ang ngiti ko. Ang bigat ng katahimikan sa bahay kapag wala siya.\n\nTumayo ako at naglakad papunta sa kwarto ko. Pero imbis na magbihis, lumapit ako sa ilalim ng kama at hinila ang isang lumang kahon ng sapatos na puno ng alikabok. Ito ang kaisa-isang bagay sa bahay na bawal galawin ni Tery.'

    'Binuksan ko ito. Sa loob, hindi sapatos ang laman, kundi ang mga "sana" ko.'

    'Kinuha ko ang isang naninilaw na envelop na may seal ng pinaka-prestigiyosong unibersidad sa bansa. Four years ago na \'to. Dahan-dahan ko itong binuklat, kahit memoryado ko na ang bawat salita.\n\n"Ms. Eliza Sorrells, due to your perfect entrance exam score and Valedictorian status, we are offering you a Full Merit Scholarship for the BS Nursing program. We recognize your exceptional academic potential and..."'

    'Napahawak ako sa dibdib ko. Naalala ko ang araw na dumating \'to. Ang daming nagsasabi sa akin noon—mga tita, tito, pati teachers ko—"Eliza, sayang ang utak mo. Kuhanin mo yan. Kami na bahala kay Tery."\n\nPero nung tinignan ko si Tery noon... ang liit-liit pa niya. Iyak siya nang iyak hanggang sa nakakapit sa laylayan ng damit ko. Alam ko sa sarili ko, kung mag-aaral ako ng Nursing, mapapabayaan ko siya. Kung iaasa ko siya sa mga kamag-anak, baka iparamdam lang sa kanya na pabigat siya.'

    'Naalala ko yung gabing tinanong ako ni Tery, noong Grade 9 siya. "Ate, diba ang talino mo? Diba Top 1 ka? Bakit nag-crew ka sa fast food? Diba dapat Nursing ka?"\n\nIyon ang pinakamahirap na acting na ginawa ko sa buong buhay ko. Tumawa ako nang malakas—yung tawang walang bahid ng lungkot—sabay gulo sa buhok niya.'

    '"Naku Tery! Tsamba lang \'yon! Alam mo bang tamad talaga si Ate mag-basa? Mas gusto ko mag-trabaho para may pera tayo pang-Jollibee! Ayoko sumakit ulo ko sa Math \'no!"'

    'Naniwala siya. Simula noon, ang tingin niya sa akin ay "Si Ate na masipag lang mag-trabaho pero hindi gaanong matalino."\n\nTiningnan ko ang mga kamay ko ngayon. Magaspang, may paso ng mantika, may kalyo sa kakatayo maghapon. Ito dapat ang mga kamay na humahawak ng heringga, stethoscope, at BP apparatus ngayon. Ito dapat ang mga kamay na nag-aalaga at nagliligtas ng buhay.'

    'Pero tinupi ko ang sulat at hinalikan ito bago ibinalik sa kahon.'

    '"Okay lang," Bulong ko sa sarili ko habang sinasara ang takip. "Hindi ako nakapagpatayo ng building... pero nakapagpatayo naman ako ng tao."'

    'Si Tery ang masterpiece ko. Si Tery ang living proof na hindi nasayang ang talino ko. Sa bawat honor na nakukuha niya, sa bawat taas ng grades niya, pakiramdam ko... ako na rin ang may suot ng medalya.\n\nPinunasan ko ang luhang tumakas sa mata ko at humarap sa salamin. Inayos ko ang buhok ko at ibinalik ang pamilyar na masayahing ngiti ni Eliza.'

    '"Time to work, Ate Eliza. Para sa tuition ng future Doctor natin."'

    # POV CHANGE

    centered "{size=+10}TERY{/size}\n\n- Morning, Outside -"

    'Napahinga ako ng malalim sa mga nangyari kanina.'

    '\'Di ko pa talaga mahahandle iyon kaya I just snuck out of it at ito nga, hindi kami sabay. Ganito rin paminsan ang ginagawa ko kapag nangyayari yon.'

    'I feel sorry, pero mas ok ng ganito kaysa sa awkward ang sitwasyon naming dalawa diba?'

    'Napabuntong hininga muli ako. Patuloy lamang akong naglalakad papasok ng school ng biglang..'

    'PAK!'

    '"Aray!" Sigaw ko ng may bumatok sa ulo ko. Pakiramdam ko, bawat batok niya may kasamang quiz bee question. Laging paalala na second place lang ako sa kanya. "Oo na, honor student. Pero kahit anong taas ng grades mo, hindi mo pa rin ako tatalunin sa pogi points." sabi ko sa kanya na may ngisi.'

    '"Baliw. Grades ang puhunan, hindi mukha," Balik agad ni Mark habang nakataas kilay. Grabe \'tong lalaking \'to. "Aray, tinamaan ako dun ah," Biro ko, sabay tawa namin pareho. Habang naglalakad kami, nadaanan namin ang mga tindahan sa tabi ng kalsada. Ang bango ng tinapay at kape. Napangiti ako kahit busog pa. Si Ate talaga… kahit puro gulay ang ihain, hindi pa rin matatalo ng kahit anong tinapay ang luto niya.\n\nBigla siyang tumigil sandali, tapos tiningnan ako nang mabuti. "Oy, ba’t parang ang lutang ng mukha mo?" Napakunot ako ng noo, pero bago pa ako makasagot, ngumisi siya ulit. "Ang aga-aga, ang sama agad ng mood mo ngayong araw ha?" Sabi niya pagkatapos tumabi sa side ko at sabay na kaming naglalakad papasok ng school ngayon.'

    'Oo nga pala,'

    'Siya pala si Mark. Siya lang naman ang parati kong nakakasundo sa school. Siya rin pala ang pinakamatalino sa room namin. Parati lang akong Second Place dahil sa kanya. "Ikaw kaya bumangon na may free batok, sino kaya hindi sasama ang mood?" Sagot ko. Natawa lang siya at mas lalo pang binilisan ang lakad na parang nang-aasar.\n\n"Kasi.." Napahinto agad ako nang maalala kong hindi pwedeng ipagsigawan kung ano man ang problema ko ngayon. "O?" Hindi ko alam kung anong other problem ang pwedeng ipalit. At dahil sa tagal kong magsalita ay mukhang nanghula nalang siya.\n\nAT ang galing niya talagang manghula... "Ang Brocon mo na namang Ate?" Sabi niya na para bang normal lang ang salitang iyon para sa kanya.'

    '(Note: Brocon ay galing sa Japanese na ang ibig sabihin ay "Brother Complex" na meaning nito\'y may tingin or may gusto sayo ang sarili mong Sister. Siscon. "Sister Complex" kung si Tery ang nagkagusto sa kapatid niyang si Eliza.)'

    '"Tigilan mo nga yan Mark, hindi ganon ang Ate ko." Iritang sabi ko. "Hahaha ikaw talaga! Kaya ka ’di nagkakaroon ng GF dahil d’yan sa Ate mo eh! Eh di ako na lang crushin niya, solve na problema mo." Pinagdiinan pa eh \'no? "At least sure ako na may isang babae sa bahay na hindi ako iiwan." Balik ko. Sabay sabog ang tawa niya na parang siya lang nakaka-gets ng joke ko.'

    'Well..'

    'Kalokohan man pero totoo ang sinabi niya. Sa tuwing nakikita niya or may nababalitaan na may nagiging ka-close akong Girl sa School ay alam ko na ang pattern. Alam na alam ko na ang kasunod na mangyayari.\n\nBasta nalang lalayo ito bukas or sa makalawa at hindi na ko papansinin pa nito kahit kailan. Hindi ko alam kung paano niya nagagawa iyon, pero hanga ako sa katangiang iyon ng Ate ko.'

    'She\'s a stalker! "Ok lang din naman kahit wala pa eh, gusto ko lang ma-ibalik ang lahat nang nagawa niya sa\'kin." Nag-seryoso ako.'

    '"Basta yung disenteng pagbalik ha?" Biro niya.'

    '"Loko!" Pagkatapos ay tinawanan nalang namin ang usapang ito. Nakapasok na kami sa school at nagsimula ang klase. Ganyan siya palagi — isang seryosong linya, tapos babalutan ng biro. Kaya kahit anong kulit niya, hindi boring kasama si Mark.'

    'Kung pag-uusapan naman ang pag-aaral ko or status ko sa school, medyo ok naman. Hindi ako magkakaroon ng problema dahil maganda at mataas ang grades ko katulad ni Mark. Kaya iyon ang dahilan kung bakit ini-iwasan kami ng mga classmate namin. Minsan nga, kahit simpleng tanong lang sa recitation, parang ayaw nilang sumagot kapag nandiyan kami. Para bang nakakahawa ang pressure na dala namin ni Mark.\n\nIniisip nilang nagtutulungan kami kahit hindi dahil parati kaming magkalayo kapag Test na dahil sa mga oras na iyon ay magka-away kami. Dahil pataasan.\n\nPero sabi ko nga, siya ang parating nangunguna sa school kaya siya ang halos nananalo parati sa laban naming dalawa.'

    'Maraming nagkakagusto kay Mark, kaso marami rin ang natu-turn off sa kanya. Kumbaga sa matalino siya\'t kinaiinggitan iyon ay babaero itong bestfriend ko. Pero sa awa naman ng diyos, meron siyang seryosong napupusuan. Kaso, dahil nga sa nature ni Mark ay uma-ayaw ito sa kanya. Kawawa naman.\n\nMinsan nga naiisip ko, baka kaya siya ganyan ka-competitive sa lahat ng bagay — dahil gusto niyang patunayan na kaya niyang maging seryoso rin. Pero kung puso na ang kalaban, wala talagang formula si Mark.'

    'Kung tungkol naman sa\'kin, katulad nga noong sinabi ko.'

    'Dahil kay Ate Eliza ay hindi ko alam kung nakakakuha ba ko nang atensyon sa kanila. Mas magandang unahin ko at i-priority ko ang promise ko kay Ate. Tutulong na ko sa kanya pag nakapagtapos na ko. Hindi na siya pwedeng makatanggi pa. Kaso baka iniisip ng iba, ambisyoso ako. Pero para sa’kin, normal lang ’yon: sino ba namang kapatid ang hindi gugustuhin na gumaan ang buhay ng Ate niya?\n\nAyun. Hanggang doon lang. Well, dahil ayokong napag-uusapan ang storya ko tungkol sa school. Parati ko itong iski-skip simula ngayon din.'

    'Aral-Recess-Aral-Uwian.'

    'Walang special na nangyayari sa school life ko. Paano ba naman magkakaroon kung ganon ang Ate ko? Pero iyon lang ba ang way para maging special?'

    'Krrrrrnggggg!!!!'

    '"Ok Class, let\'s discuss this again tomorrow! For now you should go to your own places and don\'t play around." Sabi ng Teacher naming pinagpapatong-patong ang mga Notebooks and Books upang dalhin ito sa Faculty Room nila.\n\n"Yes sir!!!!" Synchronized.'

    'Habang sila nag-iingay, kami ni Mark nakatungo pa rin, nag-aayos ng gamit. "Ano ba ’yan, parang kami lang ang hindi excited umuwi." sabi niya. "Excited din naman ako, pero hindi sa bahay… sa kanya," Sagot ko in a wryly smile. Napa-iling na lang siya.\n\nGanito talaga kasaya ang mga classmate namin kapag uwian na. Pero kami ni Mark ay hindi katulad ng mga ito. Masasabi mo na ring geek kaming dalawa. Siya\'y para lang mapahanga ang kanyang crush kaya niya ginagawa lahat ito.'

    'Magiging successful kaya siya ng ganoon lamang??'

    'Habang ako nama\'y ginagawa ang lahat ng ito para kay Ate Eliza, simple lang ngunit malaki ang tatahakin at malayo pa ito bago ko maabot. Kakayanin naman eh.\n\nNoong malapit na kaming mag part ways...'

    '"Kita kits ulit Tery!" Sigaw niya sa\'kin habang palakad at malapit na sa kabilang eskinita. "Sige bukas ulit!" Sigaw ko rin habang masaya. Hinintay ko lang siyang mawala sa aking paningin.'

    'Napadaan ako sa lumang waiting shed malapit sa kanto namin. Walang tao, pero tuwing nakikita ko ‘to, bumabalik yung alaala ng hapon na ‘yon walong taon na ang nakararaan.\n\nIto yung eksaktong lugar kung saan kami ibinaba ng mga relatives namin pagkatapos ng libing nila Mama at Papa. Naalala ko, iyak ako nang iyak noon habang nakaupo kami sa gutter. Si Ate Eliza, tahimik lang, nakatulala sa kawalan.'

    'Takot na takot ako noon kasi pakiramdam ko, bibigay na rin siya. Pero bigla siyang tumayo. Pinunasan niya yung luha niya nang sobrang diin—yung parang galit siya sa sarili niyang kahinaan.\n\nHumarap siya sa’kin, at doon ko unang nakita yung ngiti niya na ginagamit niya hanggang ngayon. Yung ngiting nagsasabing, "Okay lang ang lahat." Hinawakan niya nang mahigpit ang kamay ko at sinabing, "Wag ka nang umiyak, Tery. Ako na ang bahala. Hinding-hindi kita pababayaan."\n\nIyon ang araw na namatay ang "Ate Eliza" na kalaro ko lang dati, at ipinanganak yung Ate Eliza na tumatayong magulang ko ngayon.'

    '…..Saka ko lang naramdam ang biglang katahimikan sa paligid.'

    'Pumasok agad sa isip ko si Ate Eliza. Naalala ko yung kanina. Gusto kong umiwas, kaso magkikita\'t magkikita rin naman kami sa loob ng bahay namin.\n\nSa tuwing nangyayari kasi sa\'min iyon ay ganito kami parati. Pero nagawan agad niya ito ng paraan at kinakausap niya lang ako ng normal na parang walang nangyari at kailanman ay hindi nangyari iyon.'

    'Hanga talaga ako kay Ate.\n\nBasta. Siguro baka ganito lang muli. Hihintayin kong siya ang mauna.'

    'Paghahandaan ko nalang muli ito!'

    'Tampuhan ngayon, bati bukas. Ganyan kami ni Ate. Hindi siya pwedeng tumagal na hindi ako kinakausap — kasi sino pa aasarin niya?\n\n- End of Episode -'
    return

# Glitch Text Effect for Inline Choices
# Creates realistic digital corruption with character scrambling, color shifts, and visual artifacts
# For use with Ren'Py inline choice displays

init python:
    import random
    import string
    
    class GlitchEffect:
        """
        A class to generate glitch text effects that simulate digital corruption.
        Includes character scrambling, color shifts, and visual artifacts.
        """
        
        def __init__(self):
            self.glitch_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/\\~`"
            self.control_chars = ["█", "▓", "▒", "░", "▀", "▄", "▌", "▐"]
            self.color_glitches = ["#ff00ff", "#00ffff", "#ffff00", "#ff0000", "#00ff00", "#0000ff"]
            
        def scramble_character(self, char, intensity=0.5):
            """
            Replace a character with a glitchy equivalent based on intensity.
            intensity: 0.0-1.0 (higher = more glitchy)
            """
            if random.random() < intensity:
                if random.random() < 0.3:
                    return random.choice(self.glitch_chars)
                elif random.random() < 0.5:
                    return random.choice(self.control_chars)
                else:
                    return char.upper() if char.islower() else char.lower()
            return char
        
        def apply_glitch_text(self, text, intensity=0.3):
            """
            Apply glitch effect to entire text string.
            intensity: 0.0-1.0 (recommended: 0.2-0.5 for readable text)
            """
            glitched = ""
            for char in text:
                if char == " ":
                    glitched += char
                else:
                    glitched += self.scramble_character(char, intensity)
            return glitched
        
        def get_color_shift(self, base_color="#ffffff"):
            """
            Generate a color shift for glitch effect.
            Returns a random cyberpunk-style color.
            """
            return random.choice(self.color_glitches)
        
        def create_multi_layer_glitch(self, text, num_layers=3):
            """
            Create multiple layers of glitch at different intensities.
            Returns a list of (text, color) tuples.
            """
            layers = []
            for i in range(num_layers):
                intensity = 0.1 + (i * 0.15)
                glitched_text = self.apply_glitch_text(text, intensity)
                color = self.get_color_shift()
                layers.append((glitched_text, color))
            return layers
        
        def create_pixel_corruption(self, num_pixels=5):
            """
            Generate pixel corruption artifacts.
            Returns a string of glitch characters.
            """
            corruption = ""
            for _ in range(num_pixels):
                corruption += random.choice(self.control_chars)
            return corruption
        
        def apply_screen_tear(self, text, tear_position=0.5):
            """
            Create a screen tear effect by duplicating and offsetting text.
            tear_position: 0.0-1.0 (where to place the tear)
            """
            tear_point = int(len(text) * tear_position)
            top_part = text[:tear_point]
            bottom_part = text[tear_point:]
            
            # Add glitch characters at tear point
            tear_glitch = random.choice(self.control_chars) * random.randint(2, 4)
            
            return top_part + tear_glitch + bottom_part

# Initialize glitch effect system
glitch_system = GlitchEffect()

# Display helper functions for inline choices
def glitch_choice_text(text, intensity=0.3, use_color_shift=False):
    """
    Apply glitch effect to choice text.
    Can be used directly in displayable definitions.
    """
    glitched = glitch_system.apply_glitch_text(text, intensity)
    
    if use_color_shift:
        color = glitch_system.get_color_shift()
        return "{color=%s}%s{/color}" % (color, glitched)
    return glitched

def glitch_choice_with_tear(text, intensity=0.3):
    """
    Apply glitch effect with screen tear artifact.
    """
    glitched = glitch_system.apply_glitch_text(text, intensity)
    torn = glitch_system.apply_screen_tear(glitched)
    return torn

# Animated glitch effect using Transform
transform glitch_flicker:
    """
    Flickering glitch effect for choice buttons.
    Simulates digital corruption artifacts appearing and disappearing.
    """
    alpha 1.0
    parallel:
        block:
            choice:
                xoffset renpy.random.randint(-2, 2) yoffset renpy.random.randint(-2, 2)
                pause 0.05
            choice:
                xoffset 0 yoffset 0
                pause 0.1
        repeat
    parallel:
        block:
            choice:
                color_matrix renpy.ColorMatrix() # Normal
                pause renpy.random.uniform(0.1, 0.4)
            choice:
                color_matrix renpy.ColorMatrix(
                    (1.0, -0.3, 0.3, 0.0),   # Red channel shift
                    (-0.3, 1.0, 0.3, 0.0),   # Green channel shift
                    (0.3, 0.3, 1.0, 0.0),    # Blue channel shift
                    (0.0, 0.0, 0.0, 1.0)
                )
                pause renpy.random.uniform(0.05, 0.2)
        repeat

# Color shift glitch effect
transform glitch_color_shift:
    """
    Rapid color shifts for intense glitch effect.
    """
    block:
        choice:
            color "#ff00ff"
            pause 0.1
        choice:
            color "#00ffff"
            pause 0.1
        choice:
            color "#ffff00"
            pause 0.1
        choice:
            color "#ff0000"
            pause 0.1
        choice:
            color "#00ff00"
            pause 0.1
    repeat

# Scanline glitch effect using displayable
init python:
    def create_scanline_glitch():
        """
        Create a displayable with scanline artifacts.
        """
        return Frame("gui/glitch_scanlines.png", 0, 0) if renpy.loadable("gui/glitch_scanlines.png") else None

# Choice button with glitch effect
screen glitchy_choice(items):
    """
    Custom choice screen with integrated glitch effects.
    Use with renpy.show_screen("glitchy_choice", items=choices)
    """
    vbox:
        spacing 10
        xalign 0.5
        yalign 0.5
        
        for caption, action in items:
            button:
                xysize (400, 50)
                background "#1a1a2e"
                hover_background "#16213e"
                xalign 0.5
                
                action action
                at glitch_flicker
                
                text glitch_choice_text(caption, intensity=0.2):
                    size 24
                    color "#00ff00"
                    xalign 0.5
                    yalign 0.5

# Advanced layered glitch effect for dramatic moments
def create_dramatic_glitch(text, glitch_intensity=0.5):
    """
    Create a more dramatic glitch effect for important choices.
    Returns formatted text with multiple corruption layers.
    """
    layers = glitch_system.create_multi_layer_glitch(text, num_layers=3)
    
    result = text + "\n"
    for glitched, color in layers:
        result += "{color=%s}%s{/color}\n" % (color, glitched)
    
    return result

# Utility: Random glitch intensity based on story state
def get_corruption_level(corruption_stat=0):
    """
    Determine glitch intensity based on a corruption stat.
    corruption_stat: 0-100 (0 = no glitch, 100 = severe glitch)
    """
    return min(corruption_stat / 200.0, 0.8)  # Cap at 0.8 for readability

# Example usage documentation:
"""
# Example 1: Simple glitchy choice
$ renpy.call_screen("choice", items=[
    ("Normal choice", Return("normal")),
    (glitch_choice_text("Glitchy choice", intensity=0.3), Return("glitch"))
])

# Example 2: Dramatic glitch with screen tear
$ caption = "Delete your memories?"
$ glitched_caption = glitch_choice_with_tear(caption, intensity=0.4)
$ renpy.call_screen("choice", items=[
    (glitched_caption, Return("delete"))
])

# Example 3: Using corruption level from game state
$ glitch_intensity = get_corruption_level(game.corruption)
$ choice_text = glitch_choice_text("Proceed", intensity=glitch_intensity)

# Example 4: Multi-layer dramatic effect
$ caption = glitch_choice_text("ENTER THE VOID", intensity=0.4)
# Result includes multiple layers of corruption
"""

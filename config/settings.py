# Configuration settings for EEG decoding dashboard

# Color Palette Definitions (Scientific Modern Dark Theme)
COLORS = {
    "background": "#0D1117",
    "card_bg": "#161B22",
    "border": "#30363D",
    "primary": "#00D4FF",      # Electric Blue
    "secondary": "#00FF9F",    # Neural Green
    "warning": "#FFB800",      # Amber
    "error": "#FF4444",        # Red
    "success": "#00CC66",      # Green
    "text_primary": "#E6EDF3", # Near White
    "text_secondary": "#8B949E"# Gray
}

# Frequency Band Colors (Consistent throughout the app)
BAND_COLORS = {
    "Delta": "#9D4EDD",   # Purple (0.5 - 4 Hz)
    "Theta": "#0077B6",   # Blue (4 - 8 Hz)
    "Alpha": "#00B4D8",   # Cyan (8 - 13 Hz)
    "Beta": "#00FF9F",    # Green (13 - 30 Hz) (Using neural green)
    "Gamma": "#FF5400",   # Orange/Red (30 - 50 Hz)
}

# 14 Language-specific channels selected in left hemisphere
CHANNELS = ['F7', 'F5', 'F3', 'FT7', 'FC5', 'T7', 'C5', 'C3', 'TP7', 'CP5', 'CP3', 'P7', 'P5', 'P3']

# Brain region mapping for each channel
CHANNEL_REGIONS = {
    'F7': 'Frontal (Broca Area)',
    'F5': 'Frontal (Broca Area)',
    'F3': 'Frontal (Broca Area)',
    'FT7': 'Frontolateral (Broca / Temporal)',
    'FC5': 'Frontocentral (Motor / Speech)',
    'T7': 'Temporal (Auditory / Wernicke)',
    'C5': 'Central (Motor / Speech)',
    'C3': 'Central (Motor / Speech)',
    'TP7': 'Temporoparietal (Wernicke)',
    'CP5': 'Centroparietal',
    'CP3': 'Centroparietal',
    'P7': 'Parietal',
    'P5': 'Parietal',
    'P3': 'Parietal'
}

# Color coding for channel groups in waveforms
REGION_COLORS = {
    'Frontal (Broca Area)': '#00D4FF',             # Blue
    'Frontolateral (Broca / Temporal)': '#0088FF',    # Mid-Blue
    'Frontocentral (Motor / Speech)': '#7000FF',      # Indigo
    'Temporal (Auditory / Wernicke)': '#00FF9F',      # Neural Green
    'Central (Motor / Speech)': '#38B000',           # Darker Green
    'Temporoparietal (Wernicke)': '#FFD60A',          # Yellow
    'Centroparietal': '#FF9F0A',                      # Amber
    'Parietal': '#FF3B30'                             # Red
}

# Subjects list present in NPZ / experiment
SUBJECTS = ['S2', 'S3', 'S6', 'S10', 'S11', 'S12', 'S13', 'S15', 'S16', 'S21', 'S23', 'S26']

# Condition descriptions
CONDITIONS = {
    'perception': 'Speech Perception (Listening)',
    'production': 'Imagined Speech (Silent Repeat)',
    'rest': 'Rest State (Fixation Cross)',
    'preparation': 'Preparation State (Blank Screen)'
}

# Sentence index to Spanish text mapping (from stimulus_dict.json)
SENTENCES = {
    1: "recién me dijeron que si",
    2: "La inteligencia artificial es real",
    3: "era terrible para mi estomago",
    4: "soy flojo para hacer ejercicios",
    5: "y yo voy al gimnasio",
    6: "voy caminando todos los días",
    7: "Estuve todo el invierno resfriado",
    8: "Cuando vaya saliendo te llamo",
    9: "Nunca hay que decir nunca",
    10: "pero mi abuela tiene siete hermanos",
    11: "No se puede posponer el plazo",
    12: "pero este temblor fue más fuerte",
    13: "Eso te pasa por estar nervioso", 
    14: "yo no vivo con mi esposa",
    15: "Me dan miedo los edificios altos",
    16: "Antes todos querían comprar una tele",
    17: "yo soy la mayor de los hermanos",
    18: "la música para mi es la vida",
    19: "Gracias a Dios tuve una buena educación",
    20: "No fui a ningun lado de vacaciones",
    21: "Ellos dijeron que el vino estaba malo",
    22: "Faltan pocos días  para salir de vacaciones",
    23: "Me gusta con dos cucharadas de azúcar",
    24: "Tengo una muy buena convivencia con mis vecinos",
    25: "Esa mochila no es igual a la mia",
    26: "Anda temprano a la tienda para que puedas comprar",
    27: "y todavía estoy esperando que me llamen para ir",
    28: "Si no pasa esa micro  me voy en metro",
    29: "Mi marido y yo jubilamos en el mismo año",
    30: "Cada día me pongo más nervioso con la prueba"
}

# English translations for the 30 daily Spanish phrases
SENTENCES_ENGLISH = {
    1: "I was just told yes",
    2: "Artificial intelligence is real",
    3: "It was terrible for my stomach",
    4: "I am lazy to do exercises",
    5: "And I go to the gym",
    6: "I walk every day",
    7: "I had a cold all winter",
    8: "When I'm leaving I'll call you",
    9: "Never say never",
    10: "But my grandmother has seven siblings",
    11: "The deadline cannot be postponed",
    12: "But this earthquake was stronger",
    13: "That's what happens to you for being nervous",
    14: "I do not live with my wife",
    15: "I am afraid of tall buildings",
    16: "Before, everyone wanted to buy a TV",
    17: "I am the oldest of the siblings",
    18: "Music is life to me",
    19: "Thank God I had a good education",
    20: "I didn't go anywhere on vacation",
    21: "They said the wine was bad",
    22: "There are only a few days left to go on vacation",
    23: "I like it with two spoonfuls of sugar",
    24: "I get along very well with my neighbors",
    25: "That backpack is not the same as mine",
    26: "Go to the store early so you can buy",
    27: "And I am still waiting for them to call me to go",
    28: "If that bus doesn't pass, I'll go by metro",
    29: "My husband and I retired in the same year",
    30: "Each day I get more nervous about the exam"
}

SAMPLING_RATE = 250
TRIAL_DURATION = 3.0 # seconds @ 250Hz (750 samples)

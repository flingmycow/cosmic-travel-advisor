# --- Data Definitions ---
horoscopes = {
    "Aries": ["General (No specific decan)", "1st Decan (Mars)", "2nd Decan (Sun)", "3rd Decan (Venus)"],
    "Taurus": ["General (No specific decan)", "1st Decan (Venus)", "2nd Decan (Mercury)", "3rd Decan (Saturn)"],
    "Gemini": ["General (No specific decan)", "1st Decan (Mercury)", "2nd Decan (Venus)", "3rd Decan (Uranus)"],
    "Cancer": ["General (No specific decan)", "1st Decan (Moon)", "2nd Decan (Pluto)", "3rd Decan (Neptune)"],
    "Leo": ["General (No specific decan)", "1st Decan (Sun)", "2nd Decan (Jupiter)", "3rd Decan (Mars)"],
    "Virgo": ["General (No specific decan)", "1st Decan (Mercury)", "2nd Decan (Saturn)", "3rd Decan (Venus)"],
    "Libra": ["General (No specific decan)", "1st Decan (Venus)", "2nd Decan (Uranus)", "3rd Decan (Mercury)"],
    "Scorpio": ["General (No specific decan)", "1st Decan (Pluto)", "2nd Decan (Neptune)", "3rd Decan (Moon)"],
    "Sagittarius": ["General (No specific decan)", "1st Decan (Jupiter)", "2nd Decan (Mars)", "3rd Decan (Sun)"],
    "Capricorn": ["General (No specific decan)", "1st Decan (Saturn)", "2nd Decan (Venus)", "3rd Decan (Mercury)"],
    "Aquarius": ["General (No specific decan)", "1st Decan (Uranus)", "2nd Decan (Mercury)", "3rd Decan (Venus)"],
    "Pisces": ["General (No specific decan)", "1st Decan (Neptune)", "2nd Decan (Moon)", "3rd Decan (Pluto)"]
}

chinese_zodiac = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
]

zodiac_colours = {
    "Aries": "#FF4B4B",       # Red
    "Taurus": "#2E7D32",      # Earth Green
    "Gemini": "#FBC02D",      # Yellow
    "Cancer": "#90A4AE",      # Silver/Grey
    "Leo": "#FFA000",         # Gold/Orange
    "Virgo": "#5D4037",       # Brown
    "Libra": "#F06292",       # Pink/Pastel
    "Scorpio": "#4A148C",      # Deep Purple
    "Sagittarius": "#1565C0", # Royal Blue
    "Capricorn": "#263238",   # Dark Charcoal
    "Aquarius": "#00BCD4",    # Cyan/Electric Blue
    "Pisces": "#4DB6AC",      # Seafoam Green
    "None": "#0E1117"         # Default Streamlit Dark
}

def get_western_sign(month, day):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Aries"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Taurus"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Gemini"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Leo"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Virgo"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Libra"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Scorpio"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Sagittarius"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Aquarius"
    return "Pisces"

def get_chinese_zodiac(year):
    animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    # The cycle starts with the Rat in 1924
    return animals[(year - 1924) % 12]

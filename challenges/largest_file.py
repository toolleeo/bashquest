from challenges.base import BaseChallenge
from pathlib import Path
import random
from state import State
from utils import hash_flag

NAMES = [
    # Countries
    "afghanistan", "albania", "algeria", "andorra", "angola", "argentina", "armenia",
    "australia", "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados", "belarus", "belgium",
    "belize", "benin", "bhutan", "bolivia", "bosnia_and_herzegovina", "botswana", "brazil", "brunei", "bulgaria",
    "burkina_faso", "burundi", "cabo_verde", "cambodia", "cameroon", "canada", "central_african_republic", "chad",
    "chile", "china", "colombia", "comoros", "congo_brazzaville", "congo_kinshasa", "costa_rica", "croatia", "cuba",
    "cyprus", "czech_republic", "denmark", "djibouti", "dominica", "ecuador", "egypt",
    "el_salvador", "equatorial_guinea", "eritrea", "estonia", "eswatini", "ethiopia", "fiji", "finland", "france",
    "gabon", "gambia", "georgia", "germany", "ghana", "greece", "grenada", "guatemala", "guinea", "guinea_bissau",
    "guyana", "haiti", "honduras", "hungary", "iceland", "india", "indonesia", "iran", "iraq", "ireland", "israel",
    "italy", "jamaica", "japan", "jordan", "kazakhstan", "kenya", "kiribati", "kosovo", "kuwait", "kyrgyzstan",
    "laos", "latvia", "lebanon", "lesotho", "liberia", "libya", "liechtenstein", "lithuania", "luxembourg", "madagascar",
    "malawi", "malaysia", "maldives", "mali", "malta", "marshall_islands", "mauritania", "mauritius", "mexico",
    "micronesia", "moldova", "monaco", "mongolia", "montenegro", "morocco", "mozambique", "myanmar", "namibia",
    "nauru", "nepal", "netherlands", "new_zealand", "nicaragua", "niger", "nigeria", "north_macedonia", "norway",
    "oman", "pakistan", "palau", "palestine", "panama", "papua_new_guinea", "paraguay", "peru", "philippines",
    "poland", "portugal", "qatar", "romania", "russia", "rwanda", "saint_lucia",
    "samoa", "san_marino", "saudi_arabia", "senegal",
    "serbia", "seychelles", "sierra_leone", "singapore", "slovakia", "slovenia", "solomon_islands", "somalia",
    "south_africa", "south_korea", "south_sudan", "spain", "sri_lanka", "sudan", "suriname", "sweden", "switzerland",
    "syria", "taiwan", "tajikistan", "tanzania", "thailand", "timor_leste", "togo", "tonga", "trinidad_and_tobago",
    "tunisia", "turkey", "turkmenistan", "tuvalu", "uganda", "ukraine", "united_arab_emirates", "united_kingdom",
    "united_states", "uruguay", "uzbekistan", "vanuatu", "vatican_city", "venezuela", "vietnam", "yemen", "zambia",
    "zimbabwe",
    # Cities
    "new_york", "los_angeles", "chicago", "houston", "phoenix", "philadelphia", "san_antonio", "san_diego",
    "dallas", "san_jose", "london", "paris", "berlin", "madrid", "rome", "buenos_aires", "sao_paulo", "rio_de_janeiro",
    "toronto", "vancouver", "sydney", "melbourne", "brisbane", "tokyo", "osaka", "kyoto", "beijing", "shanghai",
    "hong_kong", "singapore", "bangkok", "jakarta", "delhi", "mumbai", "kolkata", "karachi", "islamabad", "cairo",
    "nairobi", "cape_town", "durban", "lagos", "accra", "addis_ababa", "tehran", "baghdad", "riyadh", "doha",
    "abu_dhabi", "dubai", "moscow", "saint_petersburg", "kiev", "warsaw", "prague", "budapest", "vienna", "athens",
    "lisbon", "oslo", "stockholm", "helsinki", "copenhagen", "reykjavik", "brussels", "amsterdam", "zurich",
    "geneva", "monaco", "luxembourg_city", "valletta", "vilnius", "riga", "tallinn", "sarajevo", "belgrade", "podgorica",
    "skopje", "zagreb", "ljubljana", "bratislava", "bern", "san_salvador", "guatemala_city"
]

class LargestFileChallenge(BaseChallenge):
    id = "largest_file"
    title = "Find the largest file"
    description = [
        "Several files have been created in the workspace.",
        "Each file has a different size.",
        "The flag is the name of the largest file (without extension)."
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        files = NAMES

        # Generate strictly increasing file sizes
        sizes = []
        current_size = 10000
        for _ in files:
            increment = random.randint(5, 100)
            current_size += increment
            sizes.append(current_size)

        # Shuffle either files or sizes to randomize pairing
        random.shuffle(sizes)

        # Pair filenames and sizes
        for fname, size in zip(files, sizes):
            file_path = ws / f"{fname}.txt"
            file_path.write_text("X" * size)

        # Determine the largest file
        largest_index = sizes.index(max(sizes))
        largest_file = files[largest_index]

        state.flag_hash = hash_flag(largest_file)
        state.workspace = str(ws)
        state.current_flag_word = largest_file
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag) == state.flag_hash


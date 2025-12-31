from challenges.base import BaseChallenge
import random
from pathlib import Path
from state import State

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


NUM_FILES_MIN = 50
NUM_FILES_MAX = 150

class LsCountFilesChallenge(BaseChallenge):
    id = "ls_count_files"
    title = "Count files in a directory"
    description = [
        "A random number of files have been created in the workspace.",
        "Use the appropriate command(s) to count how many files are present.",
        "The flag is the number of files."
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        num_files = random.randint(NUM_FILES_MIN, NUM_FILES_MAX)
        file_names = random.sample(NAMES, num_files)

        for fname in file_names:
            (ws / fname).touch()

        state.ls_file_count = num_files
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        try:
            return int(flag) == getattr(state, "ls_file_count")
        except (ValueError, AttributeError):
            return False


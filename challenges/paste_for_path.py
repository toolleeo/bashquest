from challenges.base import BaseChallenge
from pathlib import Path
import random
from state import State
import string
from utils import hash_flag

ADJECTIVES = [
"ancient","angry","brave","bright","calm","cold","curious","dark","distant","eager",
"fancy","fast","fearless","gentle","giant","golden","happy","hidden","hollow","icy",
"jolly","kind","lazy","lively","lonely","lucky","massive","mighty","mysterious","narrow",
"nervous","noisy","odd","old","patient","peaceful","playful","polite","powerful","proud",
"quick","quiet","rapid","rare","restless","rich","rough","royal","rusty","shiny",
"silent","silver","sleepy","slow","small","smart","smooth","soft","solid","strange",
"strong","subtle","swift","tall","tame","tender","thick","thin","tiny","tired",
"tough","tranquil","vast","vivid","warm","wild","wise","young","zany","zealous",
"stormy","foggy","windy","sunny","dusty","frozen","glowing","ancient","fragile","gentle",
"shallow","steep","cosmic","stellar","urban","rural","wooden","crystal","iron","scarlet"
]
NOUNS = [
"wizard","pirate","robot","dragon","knight","king","queen","farmer","hunter","sailor",
"captain","soldier","poet","artist","scholar","monk","merchant","inventor","pilot","explorer",
"scientist","teacher","student","child","giant","ghost","shadow","traveler","wanderer","guardian",
"builder","smith","baker","cook","doctor","engineer","mechanic","miner","ranger","archer",
"lion","tiger","wolf","eagle","falcon","shark","whale","otter","panda","horse",
"dog","cat","fox","bear","deer","rabbit","turtle","owl","sparrow","crow",
"john","maria","alex","olivia","liam","noah","emma","lucas","sofia","leo",
"city","village","kingdom","empire","forest","desert","island","mountain","river","ocean",
"galaxy","planet","star","comet","nebula","station","colony","castle","tower","temple",
"machine","engine","device","artifact","relic","portal","bridge","library","garden","harbor"
]
VERBS = [
"finds","found","seeks","seeking","discovers","discovered","explores","explored","observes","observed",
"builds","built","creates","created","destroys","destroyed","protects","protected","guards","guarded",
"follows","followed","chases","chased","meets","met","greets","greeted","helps","helped",
"teaches","taught","learns","learned","writes","wrote","reads","studies","studied","measures",
"calculates","calculated","draws","drew","paints","painted","designs","designed","imagines","imagined",
"searches","searched","crosses","crossed","climbs","climbed","sails","sailed","flies","flew",
"travels","traveled","wanders","wandered","enters","entered","leaves","left","opens","opened",
"closes","closed","moves","moved","pushes","pushed","pulls","pulled","carries","carried",
"lifts","lifted","drops","dropped","throws","threw","catches","caught","builds","repairs",
"fixes","fixed","starts","started","stops","stopped","changes","changed","watches","watched"
]


def randword(length, use_printable=False):
    """
    Returns a random word of {length} characters, made up from lowercase
    letters, or from all printable characters if {use_printable} is True
    """
    # instead of string.printable we use only the non-space characters
    alphabet = string.printable[:-6] if use_printable else string.ascii_lowercase
    return "".join(random.choices(alphabet, k=length))

class SortSizeFlagChallenge(BaseChallenge):
    id = "sort_size_flag"
    title = "Paste for path"
    description = [
        "Reconstruct the file path",
        "",
        "There are many files in the workspace (and one folder).",
        "Put them all in alphabetical order, then reconstruct the path of the",
        "secret file by joining them all together (both files and folder).",
        "The address found like this is the address of the secret file",
        "containing the flag",
        "",
        "For instance, if `workspace` were to contain the files `rome`, ",
        "`turin`, `milan`, and the folder `domodossola`, then the secret ", 
        "file would be `domodossola/milan/rome/turin`.",
        "",
        "You can assume that the folder is always before all files",
        "alphabetically."
        "",
        "Note that, like the challenge `cd_permission`, your movements are",
        "restricted. However, unlike that other challenge, the path is too",
        "long to just cd into each directory manually"
    ]
    requires_flag = True

    def setup(self, state: State) -> State:
        ws = Path(state.workspace).resolve()
        ws.mkdir(parents=True, exist_ok=True)

        flag = random.choice(ADJECTIVES) + "-" + \
               random.choice(NOUNS)      + "-" + \
               random.choice(VERBS)      + "-" + \
               random.choice(ADJECTIVES) + "-" + \
               random.choice(NOUNS)
        state.flag_hash = hash_flag(flag)

        files = []
        for _ in range(100):
            while (r:=randword(8)) in files: pass
            files.append(r)
            (ws / r).touch()
        curr = ws / min(files)
        curr.unlink()
        for f in sorted(files)[1:]:
            curr.mkdir()
            curr /= f
        curr.write_text(flag + "\n")
        curr.chmod(0o444)
        curr = curr.parent
        while curr != ws:
            curr.chmod(0o111)
            curr = curr.parent
        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag) == state.flag_hash

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
    title = "Sort files in a maze by size"
    description = [
        "Navigate the directory maze.",
        "",
        "There are multiple paths, and throughout the maze there are multiple files.",
        "Files may have any random extensions, but they are all plain text files.",
        "You have to find all files, sort them by size in ascending order and then", 
        "get the last character of the content of each one in order.",
        "",
        "The flag is the concatenation of all the last character of the contents of all",
        "files in order",
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

        curr_path = ws
        size = 0 # it also serves the purpose of index for flag
        while size < len(flag): # that's why this weird thing
            x = random.random()
            if x < .1:
                curr_path /= f"{randword(5)}.{randword(3)}"
                curr_path.write_text(randword(size, True) + flag[size])
                size += 1;
                curr_path = curr_path.parent
            elif x < .7:
                curr_path /= randword(5)
                curr_path.mkdir()
            elif curr_path != ws: # we don't want to exit the workspace
                curr_path = curr_path.parent

        return state

    def evaluate(self, state: State, flag: str) -> bool:
        return hash_flag(flag) == state.flag_hash

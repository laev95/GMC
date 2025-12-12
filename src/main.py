from src.parser.parser import parse_gmc_history
from util import get_history_bytes

raw_hist = get_history_bytes()
start_index = raw_hist.find("55aa") 

if start_index == -1:
    print("Error no start sequence found!")
    quit()

parse_gmc_history(raw_hist[start_index:])

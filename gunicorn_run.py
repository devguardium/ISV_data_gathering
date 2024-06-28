import os

from isv_nlp_utils.constants import create_analyzers_for_every_alphabet
from isv_translate import get_slovnik

from server import create_app

# TODO: Make create_analyzers_for_every_alphabet work also when the path does not contain trailing "/"
current_directory = f"{os.getcwd()}/"

slovnik = get_slovnik()["words"]
etm_morph = create_analyzers_for_every_alphabet(current_directory)["etm"]

app = create_app(etm_morph, slovnik)

from collections import defaultdict

def UDPos2OpenCorpora(pos):
    if pos == "aux":
        return ["verb"]
    if pos == "det":
        return ["pron"]
    if pos == "adp":
        return ["prep"]
    if pos == "cconj":
        return ["conj"]
    if pos == "sconj":
        return ["conj", "adv"]
    if pos == "part":
        return ["part", "interjection", "conj"]
    if pos == "propn":
        return ["noun"]
    return [pos]

def UDFeats2OpenCorpora(feats):
    result = []
    for key, value in feats.items():
        if key == "Animacy":
            # fukken TODO
            pass
        if key == 'Case':
            CASES_MAP = {
                "Nom": 'nomn',
                "Gen": 'gent',
                "Dat": 'datv',
                "Acc": 'accs',
                "Ins": 'ablt',
                "Loc": 'loct',
                "Voc": 'voct',
            }
            result.append(CASES_MAP[value])
        if key == 'Gender':
            if value.lower() == "fem": 
                value = "femn"
            result.append(value.lower())
        if key == 'Number':
            result.append(value.lower())
        if key == 'Tense':
            result.append(value.lower())
        if key == 'Person':
            result.append(value.lower() + 'per')
        if key == 'Aspect':
            if value.lower() == "imp": 
                value = "impf"
            result.append(value.lower())
        if key == 'Degree':
            if value.lower() == "pos": 
                value = ""
            if value.lower() == "cmp": 
                value = "comp"
            if value.lower() == "sup": 
                value = "supr"
            result.append(value.lower())
        if key == 'VerbForm':
            if value.lower() == "fin": 
                result += ["~actv", "~pssv"]
            if value.lower() == "inf": 
                result += ["infn"]
            pass  # https://universaldependencies.org/ru/feat/VerbForm.html
        if key == 'Voice':
            if value.lower() == "act" and feats["VerbForm"] == "Part": 
                result.append("actv")
            if value.lower() == "pass": 
                result.append("pssv")
        # {'Mood': 'Ind', 'Tense': 'Past', 'VerbForm': 'Fin'}
    if len(result) < len(feats):
        print(f"Info loss? {feats} -> {result}")
    return set([x for x in result if x])


def infer_pos(details_string):
    arr = [
        x for x in details_string
        .replace("./", '/')
        .replace(" ", '')
        .split('.')
        if x != ''
    ]

    if 'adj' in arr:
        return 'adj'
    if set(arr) & {'f', 'n', 'm', 'm/f'}:
        return 'noun'
    if 'adv' in arr:
        return 'adv'
    if 'conj' in arr:
        return 'conj'
    if 'prep' in arr:
        return 'prep'
    if 'pron' in arr:
        return 'pron'
    if 'num' in arr:
        return 'num'
    if 'intj' in arr:
        return 'interjection'
    if 'v' in arr:
        return 'verb'

ryba = lambda x: x

transliteration = defaultdict(lambda: ryba)
transliteration['ru'] = lambda x: x.replace("ё", "е")
transliteration['uk'] = lambda x: x.replace('ґ', 'г')
transliteration['be'] = lambda x: x.replace('ґ', 'г')



def iskati2(jezyk, slovo, sheet, pos=None):
    if pos is not None:
        pos = UDPos2OpenCorpora(pos.lower())
    najdene_slova = []
    # could be done on loading
    sheet['isv'] = sheet['isv'].str.replace("!", "").str.replace("#", "").str.lower()
    slovo = transliteration[jezyk](slovo)
    sheet[jezyk] = sheet[jezyk].apply(transliteration[jezyk])

    # lang-specific logic

    for i, stroka in sheet.iterrows():
        cell = stroka[jezyk]

        if slovo in stroka[jezyk].split(", "):
            if pos is not None:
                if stroka["pos"] in pos:
                    najdene_slova.append(i)
                else:
                    print("~~~~", stroka['isv'], pos, ' != ', stroka['pos'])
            else:
                najdene_slova.append(i)
    # najdene_slova = reversed(sorted(najdene_slova, key=lambda x: x['type']))
    # return [x['isv'] for x in najdene_slova]
    return najdene_slova


def inflect_carefully(morph, isv_lemma, inflect_data):
    print(isv_lemma, inflect_data)
    parsed = morph.parse(isv_lemma)[0]
    lexeme = parsed.lexeme

    forbidden_tags = {tag[1:] for tag in inflect_data if tag[0] == "~"}
    inflect_data = {tag for tag in inflect_data if tag[0] != "~"}

    candidates = {
            form[1]: form.tag.grammemes & inflect_data for form in lexeme
            if not(form.tag.grammemes & forbidden_tags)
    }
    # rank each form according to the size of intersection
    best_fit = sorted(candidates.items(), key=lambda x: len(x[1]))[-1]
    best_candidates = {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])}
    if len(best_fit[1]) == 0 and len(inflect_data) > 0:
        print("have trouble in finding anything like ", inflect_data, " for ", isv_lemma)
        return []
    if len(best_fit[1]) != len(inflect_data):
        print("have trouble in finding ", inflect_data, " for ", isv_lemma)
        print("best_fit: ", best_fit)
        print("candidates: ", {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])})
        print([parsed.inflect(cand.grammemes) for cand in best_candidates])
    return [parsed.inflect(cand.grammemes) for cand in best_candidates]



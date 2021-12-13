# THIS IS A HORRIBLE PROTOTYPE
# DO NOT TOUCH

import pandas as pd
from isv_nlp_utils import constants

import ujson
from translation_aux import inflect_carefully, UDFeats2OpenCorpora, infer_pos, iskati2

import conllu
import requests
import os
import argparse


def download_slovnik():
    dfs = pd.read_excel(
        io='https://docs.google.com/spreadsheets/d/e/2PACX-1vRsEDDBEt3VXESqAgoQLUYHvsA5yMyujzGViXiamY7-yYrcORhrkEl5g6JZPorvJrgMk6sjUlFNT4Km/pub?output=xlsx',
        engine='openpyxl',
        sheet_name=['words', 'suggestions']
    )
    dfs['words']['id'] = dfs['words']['id'].fillna(0.0).astype(int)
    dfs['words']['pos'] = dfs['words'].partOfSpeech.apply(infer_pos)
    dfs['words'].to_pickle("slovnik.pkl")
    return dfs

etm_morph = constants.create_analyzers_for_every_alphabet()['etm']





def udpipe2df(data):
    parsed = conllu.parse(data)

    result = []
    for i, udpipe_sent in enumerate(parsed):
        df = pd.DataFrame(udpipe_sent)
        df['sent_id'] = i
        df = df.set_index(["sent_id", "id"])
        result.append(df)
    return pd.concat(result).rename(columns={"upos": "pos"}).drop(columns=["xpos", "deps"])

def slovnet2df(markup):
    result = []
    for i, natasha_sent in enumerate(markup):
        df = pd.DataFrame(natasha_sent.tokens)
        df.columns = ["form", "pos", "feats"]
        df['sent'] = i
        result.append(df)
    res = pd.concat(result)
    res['lemma'] = float("nan")
    res['head'] = float("nan")
    res['deprel'] = float("nan")
    res['misc'] = float("nan")
    return res

def prepare_parsing(text, model_name):
    if model_name == "ru_slovnet":

        from razdel import sentenize, tokenize
        from slovnet import Morph
        # from slovnet import Syntax
        from navec import Navec

        navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
        morph = Morph.load('slovnet_morph_news_v1.tar', batch_size=4)
        # syntax = Syntax.load('slovnet_syntax_news_v1.tar')

        # syntax.navec(navec)
        morph.navec(navec)

        chunk = []
        for sent in sentenize(text):
            tokens = [_.text for _ in tokenize(sent.text)]
            chunk.append(tokens)
        markup = morph.map(chunk)
        df = slovnet2df(markup)
        # then add lemmas
        # I use udpipe only for lemmas
        backup_model_name = "russian"
        r = requests.post(
            url="http://lindat.mff.cuni.cz/services/udpipe/api/process",
            data={
                "data": " ".join(df.form),
                "tagger": "",
                "tokenizer": "",
                "model": backup_model_name
            }
        )
        data = ujson.loads(r.text)['result']
        udpipe_df = udpipe2df(data)
        assert len(udpipe_df) == len(df)
        df['lemma'] = udpipe_df.lemma.values
        return df
    else:
        r = requests.post(
            url="http://lindat.mff.cuni.cz/services/udpipe/api/process",
            data={
                "data": text,
                "tagger": "",
                "parser": "",
                "tokenizer": "",
                "model": model_name
            }
        )
        data = ujson.loads(r.text)['result']
        return udpipe2df(data)


def translate_sentence(sent, src_lang, dfs):
    result = []
    for idx, token_row_data in sent.iterrows():
        subresult = []
        if token_row_data.pos in {"PROPN", "PUNCT"}:
            subresult.append(token_row_data.form)
            result.append(subresult)
            continue
        lemma = token_row_data['lemma']

        found = iskati2(src_lang, lemma, dfs['words'])
        rows_found = dfs['words'].loc[found, :].sort_values(by='type')
        if not found:
            subresult.append("[?" + token_row_data.form + "?]")
            translation_cands = []
        else:
            translation_cands = rows_found.isv.values

        for isv_lemma in translation_cands:
            # TODO: select one; split multi-entries

            # print(token['deprel'], token['upos'])
            # print(token, lemma, token['upos'], token['deprel'])
            # print(dfs['words'].loc[found, ['isv', 'partOfSpeech', 'type']])

            if token_row_data.feats:
                inflect_data = UDFeats2OpenCorpora(token_row_data.feats)
                inflected = inflect_carefully(etm_morph, isv_lemma, inflect_data)
                if not inflected:
                    subresult.append("[?" + isv_lemma + "?]")
                # print("####", [(x.word, x.tag) for x in inflected])
                subresult += ([x.word for x in inflected])
            else:
                subresult.append(isv_lemma)
        result.append(subresult)
    # print(["/".join(x).replace(", ", "/") for x in result])
    return result

def translation_candidates_as_html(translation_array):
    html_result = ""
    # html_result += '<form action="#">'
    html_result += '<p>'
    for i, cand in enumerate(translation_array):
        if len(cand) == 1:
            html_result += (cand[0] + " ")
        else:
            html_result += (f'<select name="word_{i}_select" id="word_{i}_select">')
            for j, word in enumerate(cand):
                html_result += (f'<option value="word_{i}_{j}">{word}</option>')
            html_result += ('</select> ')
    html_result += ('</p>')
    # html_result += ('<input type="submit" value="Submit" />')
    # html_result += ('</form>')
    return html_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('lang', choices=[
       'en',
       'ru', 'be', 'uk', 'pl', 'cs', 'sk', 'bg',
       'mk', 'sr', 'hr', 'sl', 'cu', 'de', 'nl', 'eo',
       'ru_slovnet'
    ])
    parser.add_argument(
       '--text', type=str, default="Этот текст стоит тут для примера.",
       help='The text that should be translated'
    )

    parser.add_argument('--outfile', '-o', nargs='?',
        type=argparse.FileType('w', encoding="utf8"),
        # default=sys.stdout,
        default="test.html",
        help='The output file'
    )

    args = parser.parse_args()

    if os.path.isfile("slovnik.pkl"):
        print("Found 'slovnik.pkl' file, using it")
        dfs = {"words": pd.read_pickle("slovnik.pkl")}
    else:
        print("Downloading dictionary data from Google Sheets...")
        dfs = download_slovnik()
        dfs['words'].to_pickle("slovnik.pkl")
        print("Download is completed succesfully.")
    parsed = prepare_parsing(args.text, args.lang)
    translated = translate_sentence(parsed, args.lang, dfs)
    html = translation_candidates_as_html(translated)

    args.outfile.write(html)

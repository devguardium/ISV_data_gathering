import numpy as np
from scipy.spatial import distance
from matplotlib import pyplot as plt
import seaborn as sbn

from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
# model = SentenceTransformer('sentence-transformers/LaBSE')
model = SentenceTransformer('sentence-transformers/paraphrase-xlm-r-multilingual-v1')

ISV_text = """Tut jest anglijsky kurs gramatiky.
Preporučajemo vsegda koristati toj slovnik medžuslovjanskogo jezyka za učenje slov i gramatiky.
(Až "najstarějši" govoritelji jego često koristajut)
Ako li potrěbno vam prěvoditi tekst na drugy alfabet (iz kirilice do latinice i naopak), možete koristati transliterator:
Slovnik ukazuje sklanjanje slov, a daže konkretno slovo možno najdti, koristajuči jego sklanjeny variant, napriměr, ne potrěbno iskati slovo "dělati" ale možno pokušati najdti slovo "dělaju". 
Čto vyše: tut sut linky za deklinatory i konjungatory, kake sut koristne vo fleksiji slov, ne jestvujučih vo medžuslovjanskom slovniku:
Razširjeny etimologičny alfabet na sajtu Jana van Steenbergena:
Dobry dokument ob etimologičnom izgovoru:
Na tutom serveru jestvuje trend daby pisati etimologičnym pravopisom.
To ne jest obvezno.
Ne trěbujete trvožiti se ako li ne znajete etimologičnogo pravopisa.
Ako li něčto jest za vas težko, preporučajemo čitati "čudne bukvy" kako jih najblizši, vizualny ekvivalent (ę jest prosto e, ć jest č, đ jest dž, ų jest u, å jest a, i tako dalje).
Tut takože brza pouka za kiriličske bukvy:
Vyše ob etimologiji možno pročitati v linkah v točkě 1.5.
Medžuslovjanska Besěda sbiraje mnogo različnyh ljudij, ale često sut to fanati jezykov, jezykoljubci i lingvisti.
Zato na tom serveru često sut dělajeme někake "lingvistične eksperimenty", kake mogut poněkogda izgledati čudno za ljudi kaki tut prihodet.
Medžuslovjansky ima prěd vsim byti razumlivy i my vsi to znajemo.
Naše eksperimenty sut dělane glavno zato aby tu razumlivost ulěpšati.
Vse veliko nerazumlive "standardy" imajut drugy cělj ili često sut ironične i sut jedino zasměški.
Daby uprostiti učenje jezyka novakam, kaki prihodžet na server jesmo ukryli eksperimentalne kanaly.
Ako li jeste interesovani tymi lingvističnymi eksperimentami tako možete idti vo kanal #deleted-channel i tam dodati odgovornu reakciju.
Na serveru pokušajemo tvoriti něčto, čto imenujemo Najvyše Razumlivym Standardom.
Razumlivost togo standarda jest v srědnom smyslu i znajemo, že medžuslovjansky ima mnogu kolikost variantov kaka jest koristna za govoriteljev.
Najvyše Razumlivy Standard jest hipotetičny variant medžuslovjanskogo jezyka kaky v srědnom smyslu jest najvyše razumlivy za najvysšu kolikost slovjanogovorečih ljudij voobče.
Preporučenja do Najvyše Razumlivogo Standarda sut v drugom kanalu (#deleted-channel) kaky jest dostupny za ljudi so rolju govoreči.
Ljudam so rolju učeči ne jest potrěbno měšati vo glavě, itak prosto prěporučajemo učiti se medžuslovjansky so osnovnyh iztokov, kake sut napisane vo prvoj poukě.
Dobra metoda učenja medžuslovjanskogo jezyka jest komunikacija so vyše izkušenymi govoriteljami, itak prizyvajemo vsih do učestvovanja vo besědah na glasovyh kanalah.
""".split('\n')
EN_text = """Here is grammar course of Interslavic Language.
We recommend always using this Interslavic dictionary for learning words and grammar.
(Even the "oldest" speakers use it often)
If you need to switch text to the second alphabet (from cyrrilic to latin and vice versa), you can use this transliterator:
The dictionary shows the flexion of of words, and you can even find a certain word by using it's inflected variant, for example, there is no need to search for the word "dělati" ("to do"), but you may choose to look for "dělaju" ("I do"). 
What more: here are links to declinators and conjugators, which are useful for inflecting words that aren't in the Interslavic dictionary:
The extended etimological alphabet on Jan van Steenbergen's site:
Good document about the etimological pronounciation:
There is a trend to write in the etimological alphabet on this server.
It is not necessary.
You don't need to be upset if you don't know the etimological alphabet.
If something is hard for you, we recommend reading "the weird letters" as their closest, visual equivalent (ę is simply e, ć is č, đ is dž, ų jest u, å is a, and so on).
Here's also a quick lesson on cyrrilic letters:
You can read more about etimology in the links gived in lesson 1.5
Medžuslovjanska Besěda ("Interslavic Conversation") gathers a lot of different people, but they are often languages fanatics and linguists.
Because of this there often are certain "linguistic expermiments”, which can sometimes look weird for people who come here.
First of all, Interslavic is supposed understandable and we all know it.
Our experiments are done mainly to improve this understandability.
All not understandable „standards” have a different purpose, or are often ironic and are only jokes.
To simplify teaching the language to newcomers who come to the server, we have hidden the experimental channels.
If you’re interested in these linguistic experiments, you can enter the #rolje (roles) channel and add a reaction.
We try to create something we call the Most Understandable Standard on this server.
The understandability of this standard has a central meaning and we know that Interslavic has a lot of variants which are useful for speakers.
The Most Understandable Standard is a hypothetical variant of the Interslavic language, which, in the central sense, is generally the most understandable to the highest number of Slavic speakers.
Recommendations for the Most Understandable Standard are in another channel (#deleted-channel), which is available to people with the govoreči role.
There is no need to confuse people with the učeči, so we simply recommend learning Interslavic from basic sources, which are written in the first lesson.
A good method for learning the Interslavic languages is communication with more experienced speakers, so we invite you to participate in conversations in voice channels. 
""".split("\n")

vectors1, vectors2 = [], []

lat_alphabet = "abcčdeěfghijjklmnoprsštuvyzž"
cyr_alphabet = "абцчдеєфгхийьклмнопрсштувызж"


cyr2lat_trans = str.maketrans(cyr_alphabet, lat_alphabet)
lat2cyr_trans = str.maketrans(lat_alphabet, cyr_alphabet)


def transliterate_lat2cyr(text):
    return text.translate(cyr2lat_trans)

print(len(ISV_text))
print(len(EN_text))
for line_isv, line_en in zip(ISV_text[:50], EN_text[:50]):
    # vectors1.append(model.encode(transliterate_lat2cyr(line_isv)))
    vectors1.append(model.encode(line_isv))
    vectors2.append(model.encode(line_en))

def get_sim_matrix(vec1, vec2, window=10):
    sim_matrix=np.zeros((len(vec1), len(vec2)))
    k = len(vec1)/len(vec2)
    for i in range(len(vec1)):
        for j in range(len(vec2)):
            if (j*k > i-window) & (j*k < i+window):
                sim = 1 - distance.cosine(vec1[i], vec2[j])
                sim_matrix[i,j] = sim
    return sim_matrix

sim_matrix = get_sim_matrix(vectors1, vectors2, window=50)

threshold = None
plt.figure(figsize=(6,5))
sbn.heatmap(sim_matrix, cmap="Greens", vmin=threshold)
plt.xlabel("interslavic", fontsize=9)
plt.ylabel("english", fontsize=9)
plt.show()



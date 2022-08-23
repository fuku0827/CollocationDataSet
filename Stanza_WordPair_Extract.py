import stanza
import re

def obj(doc):
    """extract VERB + OBJ pairs"""
    obj_pairs = []
    sentences = doc.sentences
    for sentence in sentences:
        for dep in sentence.dependencies:
            if 'obj' == dep[1] and dep[2].upos == 'NOUN':
                obj_pair = (dep[0].lemma, dep[2].lemma)
                obj_pairs.append(obj_pair)
            elif 'nsubj:pass' == dep[1] and dep[2].upos == 'NOUN':
                obj_pair = (dep[0].lemma, dep[2].lemma)
                obj_pairs.append(obj_pair)
            elif 'acl' == dep[1] and dep[2].xpos == 'VBN':
                obj_pair = (dep[2].lemma, dep[0].lemma)
                obj_pairs.append(obj_pair)
            else:
                pass
        for word in sentence.words:
            if word.deprel == 'conj' and re.compile('^NN').search(word.xpos):
                if sentence.words[word.head-1].deprel == 'obj':
                    pair = (sentence.words[sentence.words[word.head-1].head-1].lemma, word.lemma)
                    obj_pairs.append(pair)
    return obj_pairs


def amod(doc):
    """extract adjectively-modified noun pairs"""
    amod_pairs = []
    sentences = doc.sentences
    for sentence in sentences:
        for dep in sentence.dependencies:
            if 'amod' == dep[1] and dep[0].upos == 'NOUN' and dep[2].upos == 'ADJ':
                amod_pair = (dep[2].lemma, dep[0].lemma)
                amod_pairs.append(amod_pair)
            else:
                pass
        for word in sentence.words:
            if word.deprel == 'conj' and re.compile("^JJ").search(word.xpos):
                if sentence.words[word.head-1].deprel == 'amod':
                    pair = (word.lemma, sentence.words[sentence.words[word.head-1].head-1].lemma)
                    amod_pairs.append(pair)
    return amod_pairs


def advmod_verb(doc):
    """extract adverbially-modified verb pairs"""
    advmod_verb_pairs = []
    sentences = doc.sentences
    for sentence in sentences:
        for dep in sentence.dependencies:
            if 'advmod' == dep[1] and dep[0].upos == 'VERB' and re.compile("^RB").search(dep[2].xpos):
                advmod_verb_pair = (dep[2].lemma, dep[0].lemma)
                advmod_verb_pairs.append(advmod_verb_pair)
            else:
                pass
        for word in sentence.words:
            if word.deprel == 'conj' and re.compile("^RB").search(word.xpos):
                if sentence.words[word.head-1].deprel == 'advmod' and re.compile("^V").search(sentence.words[sentence.words[word.head-1].head-1].xpos):
                    pair = (word.lemma, sentence.words[sentence.words[word.head-1].head-1].lemma)
                    advmod_verb_pairs.append(pair)
    return advmod_verb_pairs


def advmod_adj(doc):
    """extract adverbial-modified adjective pairs"""
    advmod_adj_pairs = []
    sentences = doc.sentences
    for sentence in sentences:
        for dep in sentence.dependencies:
            if 'advmod' == dep[1] and dep[0].upos == 'ADJ' and re.compile("^RB").search(dep[2].xpos):
                advmod_adj_pair = (dep[2].lemma, dep[0].lemma)
                advmod_adj_pairs.append(advmod_adj_pair)
            else:
                pass
        for word in sentence.words:
            if word.deprel == 'conj' and re.compile("^RB").search(word.xpos):
                if sentence.words[word.head-1].deprel == 'advmod' and re.compile("^JJ").search(sentence.words[sentence.words[word.head-1].head-1].xpos):
                    pair = (word.lemma, sentence.words[sentence.words[word.head-1].head-1].lemma)
                    advmod_adj_pairs.append(pair)
    return advmod_adj_pairs


def nounmod(doc):
    """extract nominal-modified noun pairs"""
    nounmod_pairs = []
    sentences = doc.sentences
    for sentence in sentences:
        for dep in sentence.dependencies:
            if 'compound' == dep[1] and dep[0].upos == 'NOUN' and dep[2].upos == 'NOUN':
                nounmod_pair = (dep[2].lemma, dep[0].lemma)
                nounmod_pairs.append(nounmod_pair)
            else:
                pass
    return nounmod_pairs

def Check_deprel(doc):
    return print(*[f'id: {word.id}\tword: {word.text}\thead id: {word.head}\thead: {sent.words[word.head-1].text if word.head > 0 else "root"}\tdeprel: {word.deprel}' for sent in doc.sentences for word in sent.words], sep='\n')

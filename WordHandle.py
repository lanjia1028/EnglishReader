# -*- coding: utf-8 -*-
'''

'''

import sys
reload(sys)
#===============================================================================
# sys.setdefaultencoding("utf8")
#===============================================================================
import math
import pickle
import re
from copy import deepcopy
import os
from MdxFileHandle import MdxFileHandle
from VoiceHandle import VoiceHandle
import networkx as nx
#===============================================================================
# from nltk.stem import WordNetLemmatizer
#
# wnl = WordNetLemmatizer()
# # lemmatize nouns
# print(wnl.lemmatize('cars', 'n'))
# print(wnl.lemmatize('men', 'n'))
#
# # lemmatize verbs
# print(wnl.lemmatize('running', 'v'))
# print(wnl.lemmatize('ate', 'v'))
#
# # lemmatize adjectives
# print(wnl.lemmatize('saddest', 'a'))
# print(wnl.lemmatize('fancier', 'a'))
#===============================================================================
class WordLemma(object):
    def __init__(self):
        self.lemmas = {}
        self.lemmasPath = "lemmas.data"

    def get_lemmas_by_file(self, fileName):
        print fileName
        with open(fileName, "r") as f:
            for inum in range(10):
                print f.readline()
            for i, line in enumerate(f.readlines()):
                line = line.lower().strip()
                line = line.decode("utf-8")
                wordLemma, words = re.split(u" -> ", line)
                wordLemma = wordLemma.split(u'/')[0]
                words = words.split(u',')
                for word in words:
                    self.lemmas[word] = wordLemma
        print len(self.lemmas)
        file = open(self.lemmasPath, "wb")
        pickle.dump(self.lemmas, file)
        file.close()

    def load(self):
        file = open(self.lemmasPath, "rb")
        self.lemmas = pickle.load(file)
        file.close()
        return self.lemmas

class WordHandle(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.words = {}
        self.fileList = []
        self.lemmas = WordLemma().load()

    def _get_words_by_file(self, fileName):
        print fileName
        with open(fileName) as f:
            for i, line in enumerate(f.readlines()):
                line = line.lower()
                line = line.decode("utf-8")
                lineWords = re.findall(r'([a-z]+)', line)
                for word in lineWords:
                    self.words[word] = self.words.get(word, 0) + 1
                    word = self.lemmas.get(word, False)
                    if word:
                        self.words[word] = self.words.get(word, 0) + 1
            print i

    def show_words(self):
        return sorted(self.words.iteritems(), key=lambda word:word[1], reverse=True)

    def handle_words(self):
        for word in deepcopy(self.words.keys()):
            if len(word) < 3:
                del self.words[word]

    def _get_file_list(self, path, fileType):
        files = os.listdir(path)
        for f in files:
            if(os.path.isfile(path + '/' + f))and (f.endswith(fileType)) and ("~$" not in f):
                self.fileList.append(path + '/' + f)
            if not os.path.isfile(path + '/' + f):
                self._get_file_list(path + '/' + f, fileType)

    def get_words_by_path(self, path, fileType):
        self.path = path
        self._get_file_list(path, fileType)
        for eachfile in self.fileList:
            self._get_words_by_file(eachfile)
        self.handle_words()

    def write_word_to_youdao(self, tag):
        self.wordGraph = MdxFileHandle().load_by_pickle()
        self.wordGraph.remove_nodes_from(set(self.wordGraph.nodes) - set(self.words.keys()))
        self.add_edge()
        with open(tag + "dict.xml", "w+") as f:
            f.write(u"<wordbook>")
            for item in  self.show_words():
                word = item[0]
                tagSerieal = unicode(int(math.log(item[1] + 1) + 1))
                context = ""
                ph = "<![CDATA[]]>"
                phRelation = ""
                if not self.wordGraph.nodes.get(word, False):
                    word = self.lemmas.get(word, word)
                if self.wordGraph.nodes.get(word, False):
                    ph = self.wordGraph.nodes[word]["ph"]
                    phRelation = self.wordGraph[word].keys()
                    phRelation = u"; ".join([u', '.join([ngbword, self.wordGraph.nodes[ngbword]["ph"]])  for ngbword in phRelation])
                    context = self.wordGraph.nodes[word]["context"]
                f.write(u"""<item><word>{}</word><phonetic>{}</phonetic>
                <trans>Count{},ph-Relation: {}.\r\n {}</trans><tags>{}{}</tags>
                <progress>1</progress>
                </item>""".format(item[0], ph, unicode(item[1]) , phRelation , context, tag, tagSerieal))
            f.write(u"</wordbook>")

    def add_edge(self):
        self.voiceHandle = VoiceHandle()
        phonecticRelations = self.voiceHandle.class_phonetics(nx.get_node_attributes(self.wordGraph, "ph"))
#         phonecticEdges = {}
        for subphIndexs, words in phonecticRelations.iteritems():
            if len(subphIndexs) < 3: continue
            ph = self.voiceHandle.remap(subphIndexs)
            if len(words) > 2:
                print ph, words
            index = 0
            for wordF in words:
                index += 1
                for wordS in words[index:]:
                    edge = self.wordGraph[wordF].get(wordS)
                    if edge is None:
                        self.wordGraph.add_edge(wordF, wordS, subph=[ph])
                    else:
                        if ph not in self.wordGraph[wordF][wordS]["subph"]:
                            self.wordGraph[wordF][wordS]["subph"].append(ph)
                            print self.wordGraph[wordF][wordS]
            print self.wordGraph.number_of_edges()
#         print self.wordGraph.edges()
        nx.write_gpickle(self.wordGraph, self.path + "/word.graph")



if "__main__" == __name__:
    path = "D:\\deeplearn\\keras-master\\docs"
    fileType = "md"
    #===========================================================================
    # WordLemma().get_lemmas_by_file("lemma.en.txt")
    #===========================================================================
    wordHandle = WordHandle()
    wordHandle.get_words_by_path(path, fileType)
    wordHandle.write_word_to_youdao("tag-keras-en-")
    print "finish!"



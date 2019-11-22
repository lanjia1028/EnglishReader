# -*- coding: utf-8 -*-
'''

'''
import re

class VoiceHandle(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor /ɑ:/ /ɔ:/ / ɜ:/ /i:/ /u:/为长元音；/ ʌ/ /ɒ/ /ə/ /ɪ/ /ʊ/ /e/ /æ/ /aɪ/ /eɪ/ /aʊ/ /əʊ/ /ɔɪ/ /ɪə/ /eə/ /ʊə/。。
 u'g': ,
集中双元音

第二组成部分为中元音，即/ə/。英语中，集中双元音有3个，分别为：


        '''
        self.phoneticVowel = {u'ɑː':1, u'ɔː': 2, u'ɜː':3 , u'iː':4 , u'uː': 5, u'æ': 6, u'ʌ': 7, u'ɒ':8 , u'ə': 9, u'ɪ':10 ,
                              u'ʊ': 11, u'e': 12, u'eɪ':13 , u'aɪ':14 , u'ɔɪ':15 , u'əʊ':16 , u'aʊ':17 , u'uə': 18, u'eə': 19, u'ɪə':20 }
        self.phoneticVowelExt = { u'əː':3, u'ɪː':4, u'ɔ': 8, u'i':10 , u'u':11 , u'ɛ':12, 'əu':16 , u'au': 18}
        self.phoneticConsonant = {u'p': 21, u't':22, u'k': 23, u'b':24 , u'd':25 , u'ɡ':26 , u'f':27 , u's': 28, u'ʃ': 29, u'θ': 30,
                                   u'h': 31, u'v':32 , u'z':33 , u'ʒ':34 , u'ð':35 , u'r':36 , u'tʃ': 37, u'tr': 38, u'ts':39 , u'dʒ': 40,
                                   u'dr': 41, u'dz':42 , u'm':43 , u'n':44 , u'ŋ':45 , u'l':46 , u'j':47 , u'w':48}
        self.phoneticConsonantExt = { u'g': 26}
        self.phMapIndex = {}
        self.phMapIndex.update(self.phoneticVowel)
        self.phMapIndex.update(self.phoneticVowelExt)
        self.phMapIndex.update(self.phoneticConsonant)
        self.phMapIndex.update(self.phoneticConsonantExt)
        self.indexMapPh = {value:key for key, value in self.phoneticVowel.items()}
        self.indexMapPh.update({value:key for key, value in self.phoneticConsonant.items()})
        self.indexSplit = 20
        self.count = {}
        self.phoneticEdges = {}
        #=======================================================================
        # for key in  self.phMapIndex.keys():
        #     print key
        # print self.indexMapPh
        #=======================================================================


    def class_phonetics(self , phonetics):
        for word, ph in phonetics.iteritems():
#             print "Top ", word, ph
#             word = word.decode("utf-8")
#             ph = ph.decode("utf-8")
            ph = ph.split(u',')[0]
            ph = re.sub(u'\(|\)', "", ph)
            rep = re.compile(u"[ˈ|ˌ|,| |-]")
            phSecClass = re.split(rep, ph)
            subPhs = []
            for ph in phSecClass:
                subPhs.extend(self.get_subph(ph))
            self.set_edge(subPhs, word)
#             print "Top subphs", subPhs
        return self.phoneticEdges

    def out_sub_phonetic_count(self):
        for key in sorted(self.count.iteritems(), key=lambda x:x[1], reverse=True):
            print key[0], key[1]

    def remap(self, subphIndexs):
        return "".join([self.indexMapPh[index] for index in subphIndexs])

    def set_weight(self, subphIndexs, weight):
        phsymbol = tuple(subphIndexs)
        self.count[phsymbol] = self.count.get(phsymbol, 0) + weight

    def set_edge(self, subPhs, word):
        for subphIndexs in subPhs:
            phsymbol = tuple(subphIndexs)
            self.phoneticEdges[phsymbol] = self.phoneticEdges.get(phsymbol, [])
            self.phoneticEdges[phsymbol].append(word)


    def get_subph(self, ph):
        # the max unit is len = 2.
        # lʌptjʊəsnɪs  -> lʌ,lʌp,lʌptj,ptjʊə,tjʊə,ptjʊəsn,ptjʊəsn,ptjʊəsn
        subPhs = []
        phCharIndexs = self.make_map(ph)
        vowelIndexs = []
        for index in range(len(phCharIndexs)):
            if phCharIndexs[index] < self.indexSplit:
                vowelIndexs.append(index)
        if len(vowelIndexs) < 1:
#             print u" no Vowel Ph:", ph
            return subPhs
        if len(vowelIndexs) == 1:
            self.set_weight(phCharIndexs, 10000)
            subPhs.append(phCharIndexs)
            return subPhs
        if len(vowelIndexs) == 2:
            phstart = 0
            phWindowBegin = vowelIndexs[0]
            phWindowEnd = vowelIndexs[1]
            for phend in range(phWindowBegin, phWindowEnd):
                self.set_weight(phCharIndexs[phstart:phend + 1], 1000)
                subPhs.append(phCharIndexs[phstart:phend + 1])
            phWindowBegin = vowelIndexs[0] + 1
            phWindowEnd = vowelIndexs[1] + 1
            phend = len(phCharIndexs) - 1
            for phstart in range(phWindowBegin, phWindowEnd):
                self.set_weight(phCharIndexs[phstart:phend + 1], 1000)
                subPhs.append(phCharIndexs[phstart:phend + 1])
            return subPhs
        if len(vowelIndexs) > 2:
            phstart = 0
            phWindowBegin = vowelIndexs[0]
            phWindowEnd = vowelIndexs[1]
            for phend in range(phWindowBegin, phWindowEnd):
                self.set_weight(phCharIndexs[phstart:phend + 1], 1000)
                subPhs.append(phCharIndexs[phstart:phend + 1])
            phWindowBegin = vowelIndexs[-2] + 1
            phWindowEnd = vowelIndexs[-1] + 1
            phend = len(phCharIndexs) - 1
            for phstart in range(phWindowBegin, phWindowEnd):
                self.set_weight(phCharIndexs[phstart:phend + 1], 1000)
                subPhs.append(phCharIndexs[phstart:phend + 1])
            for vowelIndex in range(1, len(vowelIndexs) - 1):
                phLWindowBegin = vowelIndexs[vowelIndex - 1] + 1
                phLWindowEnd = vowelIndexs[vowelIndex] + 1
                phRWindowBegin = vowelIndexs[vowelIndex]
                phRWindowEnd = vowelIndexs[vowelIndex + 1]
                for phstart in range(phLWindowBegin, phLWindowEnd):
                    for phend in range(phRWindowBegin, phRWindowEnd):
                        self.set_weight(phCharIndexs[phstart:phend + 1], 1)
                        subPhs.append(phCharIndexs[phstart:phend + 1])
            return subPhs


    def make_map(self, ph):
        phCharIndexs = []
        passNextPhChar = False
        for index in range(len(ph)):
            if passNextPhChar:
                passNextPhChar = False
                continue
            if (index + 1) < len and ph[index:index + 2] in self.phMapIndex:
                phCharIndexs.append(self.phMapIndex[ph[index:index + 2]])
                passNextPhChar = True
                continue
            if ph[index] in self.phMapIndex:
                phCharIndexs.append(self.phMapIndex[ph[index]])
            else:
                print "Miss", ph[index], ph
                return []
        return phCharIndexs




if __name__ == '__main__':
    test = VoiceHandle()
#     wg = MdxFileHandle().load_by_pickle()
    #===========================================================================
    # for key , value in nx.get_node_attributes(wg, "ph").iteritems():
    #     print key , value
    #===========================================================================
    print test.get_subph(u"nʌnnər")

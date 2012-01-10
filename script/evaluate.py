#!/usr/bin/python
import re, operator, os
from collections import defaultdict

def process_testset( testfile, wordlist_out, reference_out ):
    """
      Process the testfile, a normal dictionary, output a wordlist for testing,
      and a reference file for results evaluation.  Handles cases where a single
      word has multiple pronunciations.
    """
    
    print "Preprocessing the testset dictionary file..."
    test_dict = defaultdict(list)
    for entry in open(testfile,"r"):
        word, pron = entry.strip().split("\t")
        test_dict[word].append(pron)

    wordlist_ofp  = open(wordlist_out,"w")
    reference_ofp = open(reference_out,"w")
    test_list = sorted(test_dict.iteritems(), key=operator.itemgetter(0))
    for entry in test_list:
        wordlist_ofp.write("%s\n"%entry[0])
        reference_ofp.write("%s\t%s\n"%(entry[0],"\t".join(entry[1])))
    wordlist_ofp.close()
    reference_ofp.close()
    return

def evaluate_testset( modelfile, wordlistfile, referencefile, hypothesisfile ):
    """
      Evaluate the Word Error Rate (WER) for the test set.
      Each word should only be evaluated once.  The word is counted as 
      'correct' if the pronunciation hypothesis exactly matches at least
      one of the pronunciations in the reference file.
      WER is then computed as:
         (1.0 - (WORDS_CORRECT / TOTAL_WORDS))
    """

    print "Executing evaluation with command:"
    command = "../phonetisaurus-g2p -m %s -o -t %s > %s" % (modelfile, wordlistfile, hypothesisfile)
    print command
    os.system(command)
    references = {}
    correct = 0.
    total   = 0.
    for entry in open(referencefile,"r"):
        parts = entry.strip().split("\t")
        word  = parts.pop(0)
        references[word] = parts
    for entry in open(hypothesisfile,"r"):
        word, score, hypothesis = entry.strip().split("\t")
        if hypothesis in references[word]:
            correct += 1.
        total += 1.
    print "Total words: %d\nCorrect: %d\nWER [1.0-(Correct/Total)]: %f" % (int(total), int(correct), (1.-(correct/total)))
    return
    
    
if __name__=="__main__":
    import sys, argparse


    example = """%s --modelfile someg2pmodel.fst --testfile test.dic --wordlist_out test.words --reference_out test.ref --hypothesisfile test.hyp""" % sys.argv[0]
    parser = argparse.ArgumentParser(description=example)
    parser.add_argument('--testfile',     "-t", help="The test file in dictionary format. 1 word, 1 pronunciation per line, separated by '\\t'.", required=True )
    parser.add_argument('--wordlist_out', "-w", help="Desired path to the wordlist file. Will be generated from --testfile.", required=True )
    parser.add_argument('--reference_out',  "-r", help="Desired path to the reference file.  Will be generated from --testfile.", required=True )
    parser.add_argument('--hypothesisfile', "-y", help="Desired path to the hypothesis file.  Will be generated by phonetisaurus-g2p.", required=True )
    parser.add_argument('--modelfile', "-m", help="Path to the phoneticizer model.", required=True )
    parser.add_argument('--verbose',  "-v", help='Verbose mode.', default=False, action="store_true")
    args = parser.parse_args()

    if args.verbose:
        for attr, value in args.__dict__.iteritems():
            print attr, value
        
    process_testset( args.testfile, args.wordlist_out, args.reference_out )
    evaluate_testset( args.modelfile, args.wordlist_out, args.reference_out, args.hypothesisfile ) 
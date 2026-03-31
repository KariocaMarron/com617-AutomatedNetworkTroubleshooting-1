import os
code = open('/home/cyber/Solent_Final_Lab/scripts/classifier_source.txt').read()
open('/home/cyber/Solent_Final_Lab/python-engine/classifier.py', 'w').write(code)
print('Written')

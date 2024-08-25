import os
import re
import keras
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from keras import callbacks
import numpy as np
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()
from keras_preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, GlobalMaxPooling1D, Embedding, Bidirectional, LSTM, Dropout



dataDir = './data'
valDataDir = './val_data'
genomes = []
indexTrack = []
y=[]

for folder in sorted(os.listdir(dataDir)): 
    index = len(indexTrack)
    pathFolder = os.path.join(dataDir, folder)
    for file in sorted(os.listdir(pathFolder)):
            pathFile = os.path.join(pathFolder, file)
            readFile = open(pathFile, "r")
            txt = readFile.read()
            readFile.close()
            txt = re.sub(r'[0-9]+', '', txt)
            txt = re.sub(r'\s+', '', txt, flags=re.I)
            genomes.append(txt)
            indexTrack.append(index)
            y.append(folder)
indexTrack2 = []
valGenomes = []
y2 = []
for folder in sorted(os.listdir(valDataDir)): 
    index = len(indexTrack2)
    pathFolder = os.path.join(valDataDir, folder)
    for file in sorted(os.listdir(pathFolder)):
            pathFile = os.path.join(pathFolder, file)
            readFile = open(pathFile, "r")
            txt = readFile.read()
            readFile.close()
            txt = re.sub(r'[0-9]+', '', txt)
            txt = re.sub(r'\s+', '', txt, flags=re.I)
            valGenomes.append(txt)
            indexTrack2.append(index)
            y2.append(folder)

def litering_by_three(a):
    return " ".join([a[::-1][i:i+3] for i in range(0, len(a), 3)])[::-1]
i=0
maxlen=1
for genome in genomes:
    if len(genome) > maxlen:
        maxlen=len(genome)
for genome in valGenomes:
    if len(genome) > maxlen:
        maxlen=len(genome)
x=np.zeros((len(y),int(maxlen/3)))
val_x=np.zeros((len(y2),int(maxlen/3)))

littered_genomes=[]
littered_valGenomes=[]
for genome in genomes:
    genome=litering_by_three(genome)
    littered_genomes.append(genome)
for genome in valGenomes:
    genome=litering_by_three(genome)
    littered_valGenomes.append(genome)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(littered_genomes)
vocab_size = len(tokenizer.word_index) + 1
encoded_genomes = tokenizer.texts_to_sequences(littered_genomes)
encoded_valGenomes = tokenizer.texts_to_sequences(littered_valGenomes)

binarizer = preprocessing.LabelBinarizer()
labels_encoded = binarizer.fit_transform(y)
val_labels = binarizer.fit_transform(y2)

i=0
j=0
for a in encoded_genomes:
    for b in encoded_genomes[i]:
        x[i][j]=b
        j+=1
    i+=1
    j=0
i=0
for a in encoded_valGenomes:
    for b in encoded_valGenomes[i]:
        val_x[i][j]=b
        j+=1
    i+=1
    j=0

# LSTM
'''
model = Sequential()
model.add(Embedding(vocab_size, 35))
model.add(Bidirectional(LSTM(32)))
model.add(Dense(30, activation = 'relu'))
model.add(Dropout(0.2))
model.add(Dense(20, activation = 'relu'))
model.add(Dropout(0.2))
model.add(Dense(7, activation = 'sigmoid'))
'''
# CNN
'''
model = Sequential()
model.add(Embedding(vocab_size, 35, input_length=int(maxlen/3)))
model.add(Conv1D(32, 7, activation='relu'))
model.add(MaxPooling1D(5))
model.add(Conv1D(32, 7, activation='relu'))
model.add(GlobalMaxPooling1D())
model.add(Dense(7, activation='sigmoid'))
'''

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()
earlystopping = callbacks.EarlyStopping(monitor="val_loss", mode="min", patience=5, restore_best_weights=True)
hist = model.fit(x, labels_encoded, validation_split=0.2, epochs=300, batch_size=100, validation_data=(val_x, val_labels), callbacks=[earlystopping])



acc = hist.history['accuracy']
val = hist.history['val_accuracy']
loss = hist.history['loss']
valLoss = hist.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, loss, '-', label='Training Loss')
plt.plot(epochs, valLoss, '-', label='Validation loss')
plt.plot(epochs, acc, '-', label='Training accuracy')
plt.plot(epochs, val, ':', label='Validation accuracy')
plt.title('Training and Validation Accuracy and Loss')
plt.xlabel('Epoch')
plt.ylabel('Percentage')
plt.legend(loc='lower right')
plt.plot()
plt.show()

print('Training Accuracy: '+str(acc[int(len(acc)-6)]))
print('Validation Accuracy: '+str(val[int(len(val)-6)]))
print('Training Loss: '+str(loss[int(len(loss)-6)]))
print('Validation Loss: '+str(valLoss[int(len(valLoss)-6)]))
print('Epochs: '+str(epochs[int(len(epochs)-6)]))
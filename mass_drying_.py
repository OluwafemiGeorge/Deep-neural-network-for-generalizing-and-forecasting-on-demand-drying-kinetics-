# -*- coding: utf-8 -*-
"""Mass_drying .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PeyHL4JVtmLSkVlp-l0uJ2DaWjBEHzXR
"""

import tensorflow as tf

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from tensorflow.keras.optimizers import Adam

# For LSTM model
from tensorflow import keras
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.layers import LSTM
#from keras.layers import Dropout
from tensorflow.keras import Sequential,layers,callbacks
from tensorflow.keras.layers import Dense,LSTM,Dropout,GRU,Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model

#df = pd.read_csv('df1.csv')
df = pd.read_excel('FULLMASS.xls')
#X = df.iloc[:, :-1].values
#y = df.iloc[:, -1].values
#y = np.reshape(-1, 1)

X = df
y = df.loc[:,['Mass']]
X_test = X[2532:2832]
y_test = y[2532:2832]
X_train= X[0:2531]
y_train =y[0:2531]

# Scale features
s1 = MinMaxScaler(feature_range =(-1, 1))
#Xs = s1.fit_transform(df[['Tair', 'RH', 'Vel', 'Size', 'Tsec', 'L', 'P', 'F', 'Tdrop']])
Xs = s1.fit_transform(X_train)
#Xs = s1.fit_transform(df(X)) alternative representation
#Scale predicted value
s2 = MinMaxScaler(feature_range=(-1, 1))
#Ys = s2.fit_transform(df[['Tdrop']])
Ys = s2.fit_transform(y_train)
#Ys = s2.fit_transform(df(y)) alternative representation
Ys

# Creating a data structure with 60 timesteps and 1 output
window = 60
X = []
Y = []
for i in range(window,len(Xs)):
    X.append(Xs[i-window:i,:])
    Y.append(Ys[i])



    # Reshape data to format accepted by LSTM
X, Y = np.array(X), np.array(Y)
# Reshaping
#X = np.reshape(X, (X.shape[0], X.shape[1], 9))
Y

# create and train LSTM model

# Initialize LSTM model
model = Sequential()

model.add(LSTM(units=15, return_sequences=True, \
          input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=15, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=15))
model.add(Dropout(0.2))
model.add(Dense(units=1))

#compile model
#model.compile(Adam(lr=0.003), 'mean_squared_error')
model.compile(optimizer = 'adam', loss = 'mean_squared_error',\
              metrics = ['accuracy'])
# Allow for early exit
es = EarlyStopping(monitor='loss',mode='min',verbose=1,patience=10)

# Fit (and time) LSTM model
t0 = time.time()
#history = model.fit(X, Y, epochs=500, validation_split=0.1, verbose=0)
history = model.fit(X, Y, epochs = 500, batch_size = 32, callbacks=[es], verbose=1)
t1 = time.time()
print('Runtime: %.2f s' %(t1-t0))

# Plot loss
plt.figure(figsize=(8,4))
plt.semilogy(history.history['loss'])
plt.xlabel('epoch'); plt.ylabel('loss')
plt.savefig('Tdrop_loss.png')
model.save('model.h5')

# Verify the fit of the model
Yp = model.predict(X)
Yp = Yp.reshape((Yp.shape[0],Yp.shape[1]))

# un-scale outputs
Yu = s2.inverse_transform(Yp)

Ym = s2.inverse_transform(Y)
Yu

Xts = s1.transform(X_test)
Yts = s2.transform(y_test)

Xti = []
Yti = []
for i in range(window,len(Xts)):
    Xti.append(Xts[i-window:i,:])
    Yti.append(Yts[i])

# Reshape data to format accepted by LSTM
Xti, Yti = np.array(Xti), np.array(Yti)
#Xti = np.reshape(Xti, (Xti.shape[0], Xti.shape[1], 9))

# Verify the fit of the model
Ytp = model.predict(Xti)
#Ytp = Ytp.reshape((Ytp.shape[0],Ytp.shape[1]))
# un-scale outputs
Ytu = s2.inverse_transform(Ytp)

Ytm = s2.inverse_transform(Yti)

plt.figure(figsize=(10,6))
plt.subplot(2,1,1)
plt.plot(Ytu,'r-',label='LSTM Predicted')
plt.plot(Ytm,'k--',label='Measured')
#plt.legend()
#plt.ylabel('Tdrop (°C)')
#plt.subplot(2,1,2)
#plt.plot(test['Time'],test['Q1'],'b-',label='Heater')
#plt.xlabel('Time (sec)'); plt.ylabel('Heater (%)')
#plt.legend()
#plt.savefig('tclab_validate.png')

from sklearn.metrics import r2_score

#calculates and print r_2 score of training and testing
print('The R2 score of the Training set is :\t{:0.3f}'.format(r2_score(Ym, Yu)))
print('The R2 score of the Testing set is :\t{:0.3f}'.format(r2_score(Ytm, Ytu)))

# Using predicted values to predict next step
Xtsq = Xts.copy()
for i in range(window,len(Xtsq)):
    Xin = Xtsq[i-window:i].reshape((1, window, 10))
    Xtsq[i][0] = model.predict(Xin)
    Yti[i-window] = Xtsq[i][0]

#Ytu = (Yti - s2.min_[0])/s2.scale_[0]
Ytu = s2.inverse_transform(Yti)

plt.figure(figsize=(10,6))
plt.subplot(2,1,1)
plt.plot(Ytu,'r-',label='LSTM Predicted')
plt.plot(Ytm,'k--',label='Measured')
plt.legend()
#plt.ylabel('Tdrop (°C)')
#plt.subplot(2,1,2)
#plt.plot(test['Tsec'],test['Q1'],'b-',label='Heater')
#plt.xlabel('Time (sec)'); plt.ylabel('Heater (%)')
#plt.legend()
#plt.savefig('tclab_forecast.png')
#plt.show()

from sklearn.metrics import r2_score

#calculates and print r_2 score of training and testing
print('The R2 score of the Training set is :\t{:0.3f}'.format(r2_score(Ym, Yu)))
print('The R2 score of the Testing set is :\t{:0.3f}'.format(r2_score(Ytm, Ytu)))




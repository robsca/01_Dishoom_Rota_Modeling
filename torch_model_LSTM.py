import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

df = pd.read_csv('covers_2019.csv')

restaurants = df['Store_Name'].unique()

restaurant = restaurants[0]
# filter out other restaurants
df = df[df['Store_Name'] == restaurant]
df = df[['Guest_Count']]


def train_test(df, test_periods):
    train = df[:-test_periods].values
    test = df[-test_periods:].values
    return train, test

look_future = 13
train, test = train_test(df, look_future)

# scaling
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(train)
train_scaled = scaler.transform(train)

print(train_scaled)

# to tensor
train_scaled = torch.FloatTensor(train_scaled)
print(f'Original dimensions : {train_scaled.shape}')
train_scaled = train_scaled.view(-1)
print(f'Correct dimensions : {train_scaled.shape}')


def get_x_y_pairs(train_scaled, train_periods, prediction_periods):
    """
    train_scaled - training sequence
    train_periods - How many data points to use as inputs
    prediction_periods - How many periods to ouput as predictions
    """
    x_train = [train_scaled[i:i+train_periods] for i in range(len(train_scaled)-train_periods-prediction_periods)]
    y_train = [train_scaled[i+train_periods:i+train_periods+prediction_periods] for i in range(len(train_scaled)-train_periods-prediction_periods)]
    
    #-- use the stack function to convert the list of 1D tensors
    # into a 2D tensor where each element of the list is now a row
    x_train = torch.stack(x_train)
    y_train = torch.stack(y_train)
    
    return x_train, y_train

look_back = 32 #-- number of quarters for input
prediction_periods = look_future
x_train, y_train = get_x_y_pairs(train_scaled, look_back, prediction_periods)
print(x_train.shape)
print(y_train.shape)

class LSTM(nn.Module):
    """
    input_size - will be 1 in this example since we have only 1 predictor (a sequence of previous values)
    hidden_size - Can be chosen to dictate how much hidden "long term memory" the network will have
    output_size - This will be equal to the prediciton_periods input to get_x_y_pairs
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTM, self).__init__()
        self.hidden_size = hidden_size
        
        self.lstm = nn.LSTM(input_size, hidden_size)
        
        self.linear = nn.Linear(hidden_size, output_size)
        
    def forward(self, x, hidden=None):
        if hidden==None:
            self.hidden = (torch.zeros(1,1,self.hidden_size),
                           torch.zeros(1,1,self.hidden_size))
        else:
            self.hidden = hidden
            
        """
        inputs need to be in the right shape as defined in documentation
        - https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html
        
        lstm_out - will contain the hidden states from all times in the sequence
        self.hidden - will contain the current hidden state and cell state
        """
        lstm_out, self.hidden = self.lstm(x.view(len(x),1,-1), 
                                          self.hidden)
        
        predictions = self.linear(lstm_out.view(len(x), -1))
        
        return predictions[-1], self.hidden

# try to open model
try:
    model = torch.load('model.pt')
    print('Model loaded')
    model_load = True
except:
    model = LSTM(input_size=1, hidden_size=50, output_size=look_future)
    model_load = False
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

if not model_load:
    epochs = 10
    model.train()
    print('Started Training')
    # open model if model is already trained

    for epoch in range(epochs+1):
        for x,y in zip(x_train, y_train):
            y_hat, _ = model(x, None)
            optimizer.zero_grad()
            loss = criterion(y_hat, y)
            loss.backward()
            optimizer.step()
            
        print(f'epoch: {epoch:4} loss:{loss.item():10.8f}')
    # save model parameters
    torch.save(model, 'model.pt')
    print('Model saved')
    print('Finished Training')

import numpy as np
model.eval()
with torch.no_grad():
    predictions, _ = model(train_scaled[-look_back:], None)
#-- Apply inverse transform to undo scaling
predictions = scaler.inverse_transform(np.array(predictions.reshape(-1,1)))

import matplotlib.pyplot as plt
plt.plot(predictions)
plt.show()
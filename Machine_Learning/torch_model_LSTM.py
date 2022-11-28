import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

df = pd.read_csv('covers_2019.csv')

import streamlit as st

restaurants = df['Store_Name'].unique()
restaurant = st.sidebar.selectbox('Select Restaurant', restaurants)
look_future = st.number_input('How many days in the future do you want to predict?', min_value = 1, max_value = 30, value = 7, step =1)
look_back = st.number_input('How many days in the past do you want to use to predict?', min_value = 1, max_value = 30, value = 7, step =1)
lr = st.sidebar.slider('Learning Rate', min_value = 0.001, max_value = 0.05, value = 0.001, step = 0.001)
# filter out other restaurants
df = df[df['Store_Name'] == restaurant]

# sort by date
df = df.sort_values(by=['Date'])
# group by day
df = df.groupby('Date').sum()
# get day timeseries
df = df['Guest_Count']
# index as date
df.index = pd.to_datetime(df.index)
import numpy as np
# transform data
df = np.array(df)
df = df.reshape(-1, 1)

def train_test(df, test_periods):
    train = df[:-test_periods]
    test = df[-test_periods:]
    return train, test

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

# create Functions to save and load model
def save_checkpoint(checkpoint, path = 'checkpoint.pth.tar'):
    print('Saving Checkpoint')
    torch.save(checkpoint, path)
    
def load_checkpoint(checkpoint):
    print('Loading Checkpoint')
    model.load_state_dict(checkpoint['parameters'])
    optimizer.load_state_dict(checkpoint['optimizer'])


model = LSTM(input_size=1, hidden_size=50, output_size=look_future)
criterion = nn.MSELoss()
# choose optimizer
options_name = ['Adam', 'SGD', 'RMSprop']
options_optim = [
    optim.Adam(model.parameters(), lr=lr),
    optim.SGD(model.parameters(), lr=lr),
    optim.RMSprop(model.parameters(), lr=lr),
    optim.Adadelta(model.parameters(), lr=lr),
    optim.Adagrad(model.parameters(), lr=lr),
    optim.AdamW(model.parameters(), lr=lr),
    optim.Adamax(model.parameters(), lr=lr),
    optim.ASGD(model.parameters(), lr=lr),
    optim.LBFGS(model.parameters(), lr=lr),
    optim.Rprop(model.parameters(), lr=lr),
    optim.SparseAdam(model.parameters(), lr=lr)
    ]
optimizer = st.sidebar.selectbox('Choose optimizer', options_optim, format_func=lambda x: x.__class__.__name__)

# choose loss function
options_loss = [
    nn.MSELoss(),
    nn.L1Loss(),
    nn.SmoothL1Loss(),
    nn.NLLLoss(),
    nn.CrossEntropyLoss(),
    nn.BCELoss(),
    nn.BCEWithLogitsLoss(),
    nn.MarginRankingLoss(),
    nn.HingeEmbeddingLoss(),
    nn.MultiLabelMarginLoss(),
    nn.SoftMarginLoss(),
    nn.MultiLabelSoftMarginLoss(),
    nn.CosineEmbeddingLoss(),
    nn.KLDivLoss(),
    nn.PoissonNLLLoss()
]
loss_function = st.selectbox('Choose loss function', options_loss, format_func=lambda x: x.__class__.__name__)
def training(epochs = 10):
    model.train()
    print('Started Training')
    # open model if model is already trained
    #7. training
    load = False
    losses = []
    if load:
        load_checkpoint(torch.load('checkpoint.pth.tar'))

    for epoch in range(epochs+1):
        for x,y in zip(x_train, y_train):
            y_hat, _ = model(x, None)
            optimizer.zero_grad()
            loss = criterion(y_hat, y)
            loss.backward()
            optimizer.step()
        losses.append(loss.item())
        print(f'epoch: {epoch:4} loss:{loss.item():10.8f}')
        if epoch+1 == epochs:
            checkpoint = {'parameters' : model.state_dict(), 'optimizer' : optimizer.state_dict()}
            save_checkpoint(checkpoint)
            print('Saving Model - Reached Checkpoint')
    print('Finished Training')
    # plot loss
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(epochs+1), y=losses, mode='lines', name='loss'))
    fig.update_layout(title='Loss', xaxis_title='Epochs', yaxis_title='Loss')
    st.plotly_chart(fig)


def predict(data_already_scaled, look_back, show = False):
    data = data_already_scaled[-look_back:]
    import numpy as np
    model.eval()
    with torch.no_grad():
        predictions, _ = model(data, None)
    #-- Apply inverse transform to undo scaling
    predictions = scaler.inverse_transform(np.array(predictions.reshape(-1,1)))
    if show:
        import matplotlib.pyplot as plt
        plt.plot(predictions)
        plt.show()
    return predictions

'''
data = train_scaled
look_back = 31
preds = predict(data, look_back)
'''
# create a button to start training
if st.button('Start Training'):
    epochs = st.sidebar.slider('Choose number of epochs', 1, 1000, 10)
    training(epochs = epochs)
    st.write('Training finished')
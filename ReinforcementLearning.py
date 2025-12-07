import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def make_actions(n=11):
    xs = np.linspace(0, 500, n)
    ys = np.linspace(0, 200, n)
    return [(float(x), float(y)) for x in xs for y in ys]

ACTIONS = make_actions(11)
NUM_ACTIONS = len(ACTIONS)




class QNet(nn.Module):
    def __init__(self, state_dim=3, num_actions=NUM_ACTIONS):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, num_actions)
        )

    def forward(self, s):
        return self.net(s)




class Agent:
    def __init__(self, lr=1e-3, gamma=0.99):
        self.model = QNet()
        self.opt = optim.Adam(self.model.parameters(), lr=lr)
        self.gamma = gamma

        # epsilon-greedy
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(NUM_ACTIONS)

        s = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q = self.model(s)[0]
        return int(q.argmax().item())

    def update(self, state, action, reward):
        # because episode ends after ONE throw, update rule simplifies:
        # Q(s,a) = reward (no next state term)

        s = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(s)
        q_val = q_values[0, action]

        target = torch.FloatTensor([reward])

        loss = (q_val - target)**2

        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        # decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
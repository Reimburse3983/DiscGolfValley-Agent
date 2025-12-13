import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def make_actions(n=15):
    """ Generate a list of (x, y) action coordinates evenly spaced in a grid for possible locations for throws. """
    xs = np.linspace(0, 500, n)
    ys = np.linspace(0, 300, n)
    return [(float(x), float(y)) for x in xs for y in ys]

ACTIONS = make_actions(15)
NUM_ACTIONS = len(ACTIONS)




class QNet(nn.Module):
    """Simple feedforward neural network for Q-learning."""
    def __init__(self, state_dim=3, num_actions=NUM_ACTIONS):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, num_actions)
        )
    def forward(self, x):
        """Forward pass to get Q-values for all actions."""
        return self.net(x)
    



class Agent:
    """Reinforcement Learning agent using Q-learning and epsilon-greedy policy."""
    def __init__(self, lr=1e-3, gamma=0.99):
        self.model = QNet()
        self.opt = optim.Adam(self.model.parameters(), lr=lr)
        self.gamma = gamma

        # epsilon-greedy
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995

    def act(self, state):
        """Select action using epsilon-greedy policy."""
        if np.random.rand() < self.epsilon:
            print("Taking random action")
            return np.random.randint(NUM_ACTIONS)
        print("Taking greedy action")
        s = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q = self.model(s)[0]
        return int(q.argmax().item())

    def update(self, state, action, reward):
        """Update Q-network based on state, action, reward."""
        
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
    
    def save(self, path):
        """Save model, optimizer, and training state."""
        checkpoint = {
            "model_state": self.model.state_dict(),
            "optimizer_state": self.opt.state_dict(),
            "epsilon": self.epsilon,
        }
        torch.save(checkpoint, path)
        print(f"Saved checkpoint to {path}")

    def load(self, path):
        """Load model, optimizer, and training state."""
        checkpoint = torch.load(path, map_location=torch.device("cpu"))
        self.model.load_state_dict(checkpoint["model_state"])
        self.opt.load_state_dict(checkpoint["optimizer_state"])
        self.epsilon = checkpoint["epsilon"]
        print(f"Loaded checkpoint from {path}")
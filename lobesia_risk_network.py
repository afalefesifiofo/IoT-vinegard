import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.model_selection import train_test_split

# Definizione della rete neurale
class RiskClassifier(nn.Module):
    def __init__(self):
        super(RiskClassifier, self).__init__()
        self.fc1 = nn.Linear(1, 10)  # Layer di input con 10 neuroni
        self.fc2 = nn.Linear(10, 10)  # Layer nascosto con 10 neuroni
        self.fc3 = nn.Linear(10, 3)   # Layer di output con 3 classi (low, moderate, high risk)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Istanziazione del modello
model = RiskClassifier()

# Funzione di perdita e ottimizzatore
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Funzione di addestramento
def train_model(file_path):
    # Lettura dei dati da file Excel
    df = pd.read_excel(file_path)

    # Conversione dei dati in tensori
    temperatures = df.iloc[:, 0].values
    labels = df.iloc[:, 1].values

    # Assicurati che ci siano almeno 499 righe nel file Excel
    if len(temperatures) < 499:
        raise ValueError("Il file Excel deve contenere almeno 499 righe di dati.")

    # Split casuale dei dati in training e test
    X_train, X_test, y_train, y_test = train_test_split(
        temperatures, labels, train_size=400, test_size=99, random_state=None
    )

    # Conversione dei dati in tensori
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
    y_test_tensor = torch.tensor(y_test, dtype=torch.long)

    model.train()
    # Ciclo di addestramento ridotto a 10 epoche
    for epoch in range(10):  # Ciclo di addestramento
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()

        # Opzionalmente, stampa la perdita ad ogni epoca
        print(f"Epoch [{epoch + 1}/10], Loss: {loss.item():.4f}")

    # Calcolo dell'accuracy sul set di test
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test_tensor)
        _, predicted = torch.max(test_outputs, 1)
        correct = (predicted == y_test_tensor).sum().item()
        accuracy = correct / y_test_tensor.size(0)
        print(f"Test Accuracy: {accuracy:.4f}")

# Addestramento e test del modello (specifica il percorso del file Excel)
train_model("Temperature_Labels.xlsx")

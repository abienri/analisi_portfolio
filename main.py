import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import yfinance as yf

# Crea un dizionario per memorizzare i dati di ciascun ticker
data_dict = {}

# Crea la finestra della GUI
window = tk.Tk()

# Crea un nuovo grafico
fig = plt.Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

# Aggiungi il grafico alla GUI
chart = FigureCanvasTkAgg(fig, master=window)
chart.get_tk_widget().pack(fill=tk.BOTH, expand=1)

# Aggiungi un campo di input per il capitale da investire
capital_label = tk.Label(window, text="Capitale da investire")
capital_entry = tk.Entry(window)
capital_label.pack()
capital_entry.pack()

# Definisci portfolio_total come variabile globale
portfolio_total = None

def download_and_plot():
    global portfolio_total
    # Controlla se il peso totale nel portafoglio supera 1
    total_weight = sum(info['weight'] for info in data_dict.values()) + float(weight_entry.get())
    if total_weight > 1:
        messagebox.showerror("Errore", "Il peso totale nel portafoglio non può superare 1.")
        return

    # Scarica i dati storici
    try:
        data = yf.download(ticker_entry.get(), start=start_date_entry.get(), end=end_date_entry.get())
        if data.empty:
            messagebox.showerror("Errore", "Non ci sono dati disponibili per questo ticker: " + ticker_entry.get())
            return
    except Exception as e:
        messagebox.showerror("Errore", "Impossibile scaricare i dati: " + str(e))
        return

    # Salva i dati in una variabile con il nome del ticker
    data_dict[ticker_entry.get()] = {
        'data': data['Close'],
        'weight': float(weight_entry.get())
    }

    # Pulisci il grafico
    ax.clear()

    # Aggiungi i dati di ciascun ticker al grafico
    portfolio_total = None
    for ticker, info in data_dict.items():
        normalized_data = info['data'] / info['data'].iloc[0]  # Normalizza i dati
        weighted_data = normalized_data * info['weight'] * float(capital_entry.get())
        ax.plot(weighted_data, label=ticker)
        if portfolio_total is None:
            portfolio_total = weighted_data
        else:
            portfolio_total += weighted_data

    # Aggiungi l'equity totale del portafoglio al grafico
    ax.plot(portfolio_total, label='Total Portfolio', linewidth=2, color='black')

    ax.legend()

    # Aggiorna il grafico
    fig.canvas.draw_idle()

def simulate_portfolio():
    global portfolio_total
    # Calcola il rendimento medio e la deviazione standard del portafoglio
    portfolio_returns = portfolio_total.pct_change()
    mean_return = portfolio_returns.mean()
    std_dev = portfolio_returns.std()

    # Numero di giorni per 2 anni
    num_days = 2 * 252

    # Simulazione di Monte Carlo
    simulations = np.zeros(num_days)
    simulations[0] = portfolio_total.iloc[-1]  # Parte dall'ultimo valore del portafoglio

    # Simula il portafoglio per i prossimi 2 anni
    for t in range(1, num_days):
        simulations[t] = simulations[t - 1] * (1 + np.random.normal(loc=mean_return, scale=std_dev))

    # Crea un indice di date per i prossimi 2 anni
    last_date = portfolio_total.index[-1]
    date_index = pd.date_range(start=last_date, periods=num_days)

    # Disegna le simulazioni
    ax.plot(date_index, simulations, label='Simulazione')

    # Fissa i limiti dell'asse y
    ax.set_ylim(bottom=0, top=portfolio_total.max() * 1.5)  # Modifica i valori come necessario

    # Disabilita la notazione scientifica
    ax.get_yaxis().get_major_formatter().set_scientific(False)

    # Aggiorna il grafico
    fig.canvas.draw_idle()

# Crea gli elementi della GUI
ticker_label = tk.Label(window, text="Ticker")
ticker_entry = tk.Entry(window)
start_date_label = tk.Label(window, text="Data di inizio (YYYY-MM-DD)")
start_date_entry = tk.Entry(window)
end_date_label = tk.Label(window, text="Data di fine (YYYY-MM-DD)")
end_date_entry = tk.Entry(window)
weight_label = tk.Label(window, text="Peso nel portafoglio (%)")
weight_entry = tk.Entry(window)
download_button = tk.Button(window, text="Scarica e traccia", command=download_and_plot)
simulate_button = tk.Button(window, text="Simula", command=simulate_portfolio)

# Posiziona gli elementi nella GUI
ticker_label.pack()
ticker_entry.pack()
start_date_label.pack()
start_date_entry.pack()
end_date_label.pack()
end_date_entry.pack()
weight_label.pack()
weight_entry.pack()
download_button.pack()
simulate_button.pack()

# Avvia la GUI
window.mainloop()

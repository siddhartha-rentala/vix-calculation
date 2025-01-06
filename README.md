## **VIX Calculation**

### **Project Overview:**
This project implements the VIX calculation methodology using SPX option chains. The analysis focuses on computing implied volatility and weighted option prices to replicate the VIX index.

### **Key Features:**
1. **SPX Option Chain Analysis:** Processes data from SPX option chains to estimate market volatility.
2. **T-Bill Quotes:** Uses T-bill data to adjust for risk-free discounting.
3. **Weighted Average of Options:** Combines out-of-the-money call and put options to compute the VIX index.

### **Installation:**
```bash
pip install pandas numpy matplotlib
```

### **Usage:**
```bash
python VIXCalculation.py
```

### **Results:**
1. **VIX Values vs Actual VIX:** A plot comparing the calculated VIX values with the actual VIX.
2. **Implied Volatility Surface:** A 3D surface plot showing implied volatilities across different strikes and expirations.

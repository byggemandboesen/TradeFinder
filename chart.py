import matplotlib.pyplot as plt

# Create chart and send in chat
class Charter:
    def __init__(self, symbol, candles):
        self.SYMBOL = symbol
        self.CANDLES = candles
        
        self.XLABEL = candles["Open time"][::32]
        self.TITLE_SIZE = 18
        self.LABEL_SIZE = 14
        self.TICK_SIZE = 8
    

    # Plot, save and return path to chart
    def create_chart(self):
        plt.figure(figsize=(12,6))
        plt.style.use('dark_background')

        # Plot bars
        width=1
        width2=0.15
        pricesup=self.CANDLES[self.CANDLES.close>=self.CANDLES.open]
        pricesdown=self.CANDLES[self.CANDLES.close<self.CANDLES.open]

        plt.bar(pricesup.index,pricesup.Close-pricesup.Open,width,bottom=pricesup.Open,color='g')
        plt.bar(pricesup.index,pricesup.High-pricesup.Close,width2,bottom=pricesup.Close,color='g')
        plt.bar(pricesup.index,pricesup.Low-pricesup.Open,width2,bottom=pricesup.Open,color='g')

        plt.bar(pricesdown.index,pricesdown.Close-pricesdown.Open,width,bottom=pricesdown.Open,color='r')
        plt.bar(pricesdown.index,pricesdown.High-pricesdown.Open,width2,bottom=pricesdown.Open,color='r')
        plt.bar(pricesdown.index,pricesdown.Low-pricesdown.Close,width2, bottom=pricesdown.Close,color='r')
        
        # Plot title, ticks and etc
        plt.title(f"24H chart for {self.SYMBOL} - 5m candles", fontsize = self.TITLE_SIZE)
        plt.ylabel(r"Price evaluation", fontsize = self.LABEL_SIZE)
        plt.xlabel("Time", fontsize = self.LABEL_SIZE)
        plt.xlim(0, 288)
        plt.xticks([32*i for i in range(9)], [label.split(" ")[1] for label in self.XLABEL.astype(str)], rotation = 45, ha = 'right', fontsize = self.TICK_SIZE)
        plt.yticks(fontsize = self.TICK_SIZE)
        plt.grid(alpha = 0.25)
        plt.tight_layout()

        path = f'./{self.SYMBOL}.png'
        plt.savefig(path, dpi = 250)
        plt.close()
        return path

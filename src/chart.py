import matplotlib.pyplot as plt

# Create chart and send in chat
class Charter:
    def __init__(self, symbol, candles):
        self.SYMBOL = symbol
        self.CANDLES = candles
        
        self.XLABEL = candles["Open time"][::32]
        self.TITLE_SIZE = 22
        self.LABEL_SIZE = 16
        self.TICK_SIZE = 12
    

    # Plot, save and return path to chart
    def createChart(self):
        
        fig = plt.figure(figsize=(16,10))
        grid = fig.add_gridspec(2,1, height_ratios = (3,1))
        plt.style.use('dark_background')
        fig.suptitle(f"24H chart for {self.SYMBOL} - 5m candles", fontsize = self.TITLE_SIZE)

        chart_ax = fig.add_subplot(grid[0,0])
        vol_ax = fig.add_subplot(grid[1,0])

        pricesup=self.CANDLES[self.CANDLES.Close>=self.CANDLES.Open]
        pricesdown=self.CANDLES[self.CANDLES.Close<self.CANDLES.Open]

        self.plotChart(chart_ax, pricesup, pricesdown)
        self.plotVol(vol_ax, pricesup, pricesdown)

        chart_ax.get_shared_x_axes().join(chart_ax, vol_ax)
        chart_ax.set_xticklabels([])
       
        plt.tight_layout()
        path = f'./{self.SYMBOL}.png'
        plt.savefig(path, dpi = 150)
        plt.close()
        return path

    def plotChart(self, ax, pricesup, pricesdown):
        width=1
        width2=0.15
        ax.bar(pricesup.index,pricesup.Close-pricesup.Open,width,bottom=pricesup.Open,color='g')
        ax.bar(pricesup.index,pricesup.High-pricesup.Close,width2,bottom=pricesup.Close,color='g')
        ax.bar(pricesup.index,pricesup.Low-pricesup.Open,width2,bottom=pricesup.Open,color='g')

        ax.bar(pricesdown.index,pricesdown.Close-pricesdown.Open,width,bottom=pricesdown.Open,color='r')
        ax.bar(pricesdown.index,pricesdown.High-pricesdown.Open,width2,bottom=pricesdown.Open,color='r')
        ax.bar(pricesdown.index,pricesdown.Low-pricesdown.Close,width2, bottom=pricesdown.Close,color='r')
        
        # Plot ticks and etc
        ax.set(xlim = [0, 288])
        ax.set_ylabel("Price evaluation", fontsize = self.LABEL_SIZE)
        ax.grid(alpha = 0.25)
    
    def plotVol(self, ax, pricesup, pricesdown):
        ax.bar(pricesup.index, pricesup.Volume, color='g')
        ax.bar(pricesdown.index, pricesdown.Volume, color='r')

        ax.set(xlim = [0, 288])
        ax.set_xticklabels(labels = [label.split(" ")[1] for label in self.XLABEL.astype(str)], fontsize = self.TICK_SIZE)
        ax.tick_params(axis = "y", labelsize = self.TICK_SIZE)
        ax.set_ylabel("Volume", fontsize = self.LABEL_SIZE)
        ax.set_xlabel("Time", fontsize = self.LABEL_SIZE)
        ax.grid(alpha = 0.25)

# TODO Add VPVR (Volume Profile Visible Range)
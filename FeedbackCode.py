#Helpful Site https://learn.sparkfun.com/tutorials/graph-sensor-data-with-python-and-matplotlib/speeding-up-the-plot-animation

import asyncio
import qtm
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

#GraphFormatting
style.use('fivethirtyeight')
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
x_len = 100 #Number of prior data points saved.
y_range = [0,40] #Y Axis
xs = list(range(0,100)) 
ys = [float(0)] * x_len 
tar = [5] * x_len #Change this to change the target line
ax.set_ylim(y_range)
line, = ax.plot(xs,ys)
line1, = ax.plot(xs,tar)
LastDataPoint = 0
LoopControl = 'True'
offset = -3.5 #Change this for offset

#Connect to qtm function
async def setup():
     "Main function"
     connection = await qtm.connect("127.0.0.1")
     if connection is None:
          return
     await connection.stream_frames(components=["analogsingle"], on_packet=on_packet)

#This brings in the packet of data
def on_packet(packet):
     "Callback function that is called everytime a data packet arrives from QTM"
     #print("Framenumber: {}".format(packet.framenumber))
     global Framenumber
     global DynoData
     global LastDataPoint
     global LoopControl
     global ys
     Framenumber = format(packet.framenumber)
     #print('Framenumber', Framenumber)
     header, analog = packet.get_analog_single()
     CompData=format(analog)
     #Extracting Just Channel 13
     SplitCompData = CompData.split(',')
     SplitSingleChannel = SplitCompData[14]
     SplitSingleChannel = re.sub('\)\)\)\]','',SplitSingleChannel)
     DynoData = SplitSingleChannel.lstrip(' ')
     #Occasionally, the data point will not be recieved from QTM. In this case, it will use the last point to graph. 
     if DynoData == "nan":
        DynoData = LastDataPoint
     LastDataPoint = DynoData
     stopqtmfunction()
     return DynoData,Framenumber

def stopqtmfunction():
    asyncio.get_event_loop().stop()

def animate(i,tar,ys):
    asyncio.ensure_future(setup())
    loop = asyncio.get_event_loop().run_forever()
    #Add x and y to lists
    DynoDataN = float(420.04)*float(DynoData) + float(211.4)+float(offset)
    ys.append(DynoDataN)
    #Limit Y to set number of items
    ys = ys[-x_len:]
    #Update line with new Y values
    line.set_ydata(ys)
    return line,
    #Format plot
    plt.title('Force')
    plt.ylabel('Force (N)')


anim = animation.FuncAnimation(fig, animate, fargs=(tar,ys), interval=50, blit=True) #Animateing to figure, animating animate, in ms. How often it updates
plt.show()

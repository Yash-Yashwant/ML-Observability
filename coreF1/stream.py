import fastf1


#create obejct
from fastf1 import livetiming
from fastf1.livetiming.client import SignalRClient
stream = SignalRClient(filename="output.json",
                       filemode='a',
                       timeout=0,
                       no_auth=False
                       


)

stream.start()

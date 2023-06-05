import ta

amplitude = 2
channelDeviation = 2
showArrows = True
showChannels = True

trend = 0
nextTrend = 0

def halftrend():
    # experimental (untested) function (may change in the future), ported from:
    # data = [high, close, low]
    data = [[100,97,90],[101,98,94],[103,96,92],[106,100,95],[110,101,100],[112,110,105],[110,100,90],[103,100,97],[95,90,85],[94,80,80],[90,82,81],[85,80,70]];
    atrlen = 6
    amplitude = 3
    deviation = 2
    output = ta.halftrend(data, atrlen, amplitude, deviation)
    print(output)
# output (array)
# [
#   [ 115.14, 105, 94.86, 'long' ],
#   [ 100.77, 90, 79.22, 'long' ],
#   [ 116.32, 105, 93.68, 'long' ],
#   [ 101.1, 90, 78.89, 'long' ],
#   [ 116.25, 105, 93.75, 'long' ],
#   [ 99.77, 90, 80.23, 'long' ]
# ]

halftrend()
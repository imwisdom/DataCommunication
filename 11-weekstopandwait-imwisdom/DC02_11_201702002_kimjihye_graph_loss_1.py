import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi']=300

plt.plot([0.1, 1, 10, 100], [1.68, 63.94, 569.33, 8309.73], '.-', label='sample1')
plt.plot([0.1, 1, 10, 100], [8.81, 41.28, 630.58, 6835.45], 'o-', label='stop')
plt.xlabel('M byte', fontsize=10)
plt.ylabel('time(s)', fontsize=10)
plt.title('my loss 1% graphs')
plt.legend(('StopAndWait', 'GoBackN'))

plt.show()

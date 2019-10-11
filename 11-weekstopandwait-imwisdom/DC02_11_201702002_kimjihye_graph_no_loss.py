import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi']=300

plt.plot([0.1, 1, 10, 100], [1.60, 7.30, 91.31, 1083.93], '.-', label='sample1')
plt.plot([0.1, 1, 10, 100], [1.36, 8.61, 82.65, 1160.55], 'o-', label='stop')
plt.xlabel('M byte', fontsize=10)
plt.ylabel('time(s)', fontsize=10)
plt.title('my no loss graphs')
plt.legend(('StopAndWait', 'GoBackN'))

plt.show()

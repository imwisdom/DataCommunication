import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi']=300

plt.plot([0.1, 1, 10, 100], [17.04, 360.18, 2680.71, 28137.47], '.-', label='sample1')
plt.plot([0.1, 1, 10, 100], [28.70, 319.77, 2859.56, 27586.78], 'o-', label='stop')
plt.xlabel('M byte', fontsize=10)
plt.ylabel('time(s)', fontsize=10)
plt.title('my loss 5% graphs')
plt.legend(('StopAndWait', 'GoBackN'))

plt.show()

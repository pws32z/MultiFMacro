import sys, types as _types

# ── Stub autoit FIRST before anything else loads ──────────────────────────
# pyautogui (and some of its deps) try to import 'autoit' on Windows.
# Inject a dummy module so the import succeeds without autoit installed.
if "autoit" not in sys.modules:
    _autoit_stub = _types.ModuleType("autoit")
    _autoit_stub.click       = lambda *a, **k: None
    _autoit_stub.double_click= lambda *a, **k: None
    _autoit_stub.right_click = lambda *a, **k: None
    _autoit_stub.mouse_move  = lambda *a, **k: None
    _autoit_stub.key_send    = lambda *a, **k: None
    _autoit_stub.type        = lambda *a, **k: None
    _autoit_stub.win_active  = lambda *a, **k: False
    sys.modules["autoit"]    = _autoit_stub
# ─────────────────────────────────────────────────────────────────────────

import os, re, time, glob, json, shutil, tempfile, threading, configparser, webbrowser
import tkinter as tk
from tkinter import messagebox, ttk
import requests

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.05
    PAG_OK = True
except Exception:
    PAG_OK = False

try:
    from screeninfo import get_monitors
    def get_screen_size():
        try: m = get_monitors()[0]; return m.width, m.height
        except: return 1920, 1080
except ImportError:
    def get_screen_size(): return 1920, 1080


# ── Embedded icon (base64 PNG/ICO) ───────────────────────────────────────
import base64 as _b64
_ICON_ICO_B64 = "AAABAAcAEBAAAAAAIADpAAAAdgAAABAQAAAAACAA6QAAAF8BAAAgIAAAAAAgAMcBAABIAgAAMDAAAAAAIAA3AgAADwQAAEBAAAAAACAAzAIAAEYGAACAgAAAAAAgAJ8FAAASCQAAAAAAAAAAIADZCwAAsQ4AAIlQTkcNChoKAAAADUlIRFIAAAAQAAAAEAgGAAAAH/P/YQAAALBJREFUeJxjZGBgYODlFfnPQAb4/PkNIyM+zfmxjxkYGBgYJi6WxWkICz6N01aoEjQIxQXoGtFBVsRtDIPgBuTHPsapEZtBMEOYiFGMD+A1ICviNsOD8vdb8RmC0wCYZkIuxGoAumZ8rsBqwLQVqgzbDM28FToFvRkYGBgUOgW9cQUw1nSAbFAWw22cmjFcgM2ZhKIWIynjS0x4ExI6QDYIm0aCBiAbhC8zMTIwUJadAagLVmX447koAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAsElEQVR4nGNkYGBg4OUV+c9ABvj8+Q0jIz7N+bGPGRgYGBgmLpbFaQgLPo3TVqgSNAjFBega0UFWxG0Mg+AG5Mc+xqkRm0EwQ5iIUYwP4DUgK+I2w4Py91vxGYLTAJhmQi7EagC6ZnyuwGrAtBWqDNsMzbwVOgW9GRgYGBQ6Bb1xBTDWdIBsUBbDbZyaMVyAzZmEohYjKeNLTHgTEjpANgibRoIGIBuELzMxMjBQlp0BqAtWZfjjuSgAAAAASUVORK5CYIKJUE5HDQoaCgAAAA1JSERSAAAAIAAAACAIBgAAAHN6evQAAAGOSURBVHiczZe/SgNBEMa/NYJVBMEmhWBzD3AWeYhYpUuTFwhCGsHOIp1gIxz3AjZ2V5mHSGEeII2QwiYgeJWFaDUwrHuT2dl4cZq723/f775ddnccWHS7p99oIep64+jdtSkcAjlIHWQ6Xif1d9a/J+HyKcNktAIAPDyeRY9zmCIMAIPlYljmWUV1sRBqgJAwAMzzfkXvZZ5V1E4LopqC6XgdFPbbDZaLIZVrp0UECP11SNiH4ICT0UqECAJIdkviPojGjV8AWru1ELx/yI3GRaixmwYlYD+ovzRW0kZE1tLTEmYAEn29eX9OgTAB+OL0tET0TsjF74+OL6i8gLwemiLKgSZxALi6/XrjbXYO4NseCst6UAOQted3J5dNbaguZhqipoBDFLNOj9fR95+uARIgkWLW6V1/frxYxU0AHASw2b4TAC5qFQeEfYBfNKQzQRLX9P9/x/E2kFYuJBJIq1eyEIh0KZ3n/Sr2ih6dF0jTss3unQCEQFISk+Tc0JKMUNT1xu09OXW8YB/p+Q+19yP2ifIgzwAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAAAwAAAAMAgGAAAAVwL5hwAAAf5JREFUeJzdmjFOwzAUhv9ESExFQmJFYukBytBDwMSWpRfI0gWpZ0BiYekFWLp1ag/BAAfIUqkrUiU6McGADE+P+NWu36Mxv1S1cVzn+xqnSewUYOn1zj54WZey3b4WdLmkC12HB34zlr4VXQ5lLXmBdsajtUm7jrmwgnfg01kfddUAAB4ez9W3oy5AwXksRNQEJHCeumrUJJIFdoFfvTzdLAfDOS/X2htJAuPRWgQHgOVgOKefeb1Ukb0EpF9dgrUQiRLYFzymbuzxESSgBd723dS9IQpYgYe2EyLiFfAdoFrgMe1K3epIYwMace3GbidIwNdXQ1JXTdDJzYWKhGyz3FUhJa4Pu3eLmAlwaCsJEwEKu5psFm3lWlEXaIO3lFAV8P3ybctaUROQ4KW6qVER8MHfH59cuhdfpyWRLCDB03pWEkkCMd2GRlMiSYCeYS/uTq9Dv0frxpyl25LchXwSt+9vz7SeW9aEByIu5qTQoRMHuJpsFlxCGx5Q/Budzvpil7KABwzOxG0SVvCA0bWQb09owwOGV6Mc1gIeML4fcNBW8EDgv9CuwSkpsfAmt5S0wUPc1Ev5v8MqNNkObPFkO7TIk+3gLk+2w+s0WU9w0GQ7xcST7SQfz59NswL2E90W4MDXcxPfD07k9KgB8PPQR8kLcghlLX0ruhrO+AmOdKuQQtlizAAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAABAAAAAQAgGAAAAqmlx3gAAApNJREFUeJztmzFOwzAUhv9ESExFQmJFYukBytBDwMTWpRfo0gWJMyCxsPQCLN060UMwwAG6IHWthEQmJhiQhfVqx3Hi916a8EuI1knqfF9iK3GcDJ4MBmffvmWHmKLYZa7yvcKugdNQEbn9pevwwD5j7lvQ5disOS3oSwxzHlqRO/PpVrX+TOvoG/DFcojZZAMAeHw6F98PcQE2OI2GCDEBZeA0kiLYBYTAr95ebtaj8cq1bDbZsEtgE1AFHADWo/HK/kzX4z4bkguIAY9ZxiUiqYD5dFsLPGbd1CKSCCg76jHgrm3L+geguYhGArjAY36naUdZS0CTnr1uuJpFlIAmHVyqpG4WlQS0ATymvhgRQQGpenaOpOgfjjgqloqpv8n+RAtI3cHNJptK9wdlsUXE7pvqeIBpq+a/RtQEUGgtCSoCfLAaEsQFUMj3u4/nsuXcERXgg9eUICYgdOTpd6mICAjBu8qlzgJ2AVXhq2zLEVYBIfiH45NL8+dbh1sCm4Aq8L7vkhJYBMTCu8qlJCQX0KTN00hISC6A3thc3J9e1/0tum3TmyZXWJpASMLt1+erazu7XAIeYOwEYyVowAM1B0Sqxn7yC/yBmbbtOhMk4QGBCyEXgK9fkIYHhC6FF8thsElowAPCd4M+CVrwgMJ4QOhMkIQHlEaEfJDS8IDimCCF1YAHlEeFDbQWPFDjOiA0oyM2KeBFH4zYFWk/IUpR///D0f/H40wTJIC0IloxQYJGYqZIK6fI0PR2khRNKhEHN02Opu6skoOfKGmnt1NlaXo7WZqmt9PlaXr7wgRNa16ZAXTfGptPtyrgwO9LlOoCNFMUuyw3H7R3RjqGOacFfYjNmvsWdDWU0QvctX7Bd3B/ACE2Pmugzz2TAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAFZklEQVR4nO2dPW4UQRCF31pIjkCyRIpEwgEg4BAQkTnxBZw4scQZLJGQcAESMiJ8CAI4gBMkpysheSNHEFhljcc9sz3dPd1Vr/qLjOfX+76u6plddjZI4OnT5/9Stuusy2633SzdJnqDHrotYmXYu1IP3jb7RDiYW9jDt8++DIN29OA5CVWDRxWgh89LKNvZFtDh54EAffTzM874YGpBh5dh1r0FOOcA8D36z06uW59CEyTzJ61PpBUS/Jdvr+5//vz1RctTasIG8FUBhsGPOT2+AuBHhN1uu9l4CX8u+DGnx1duJHAhwNnJdVTwQ7xUA2oBloz6KdhFoBSgRPBjWEWgEmCN4MewzQ9oBEjp86kwVQPzAuSO+ne/f364fP32e8q2DCKYFaBE8ABw+frt9+HPKfuy3BbMCVAy+CXL9mG1GpgSIKfPLwnXkwgmBGjV53PnBxYkUC3AmuW+xj4sVAO1AtQq9zX2qVkEdQLkjPo1gg8dg+myUY0A2oMveTxN84PmArS8kZMLQ1toKoC2Pp+KZRGaCGCp3C/B4mVjVQFYgx9irRpUEcByn0/FigirC8DS51PRLsJqAngo90vQOj8oLkAPfhqN1aCYAD34eDSJUESA3D7vJfgxGtpCs/8a5m3UhyjxaaRcqgvQ+g/WhrwOrV6XagJoDf70+Krap4nnaCVCFQG09nmZUGmRAHgoQo3XzO0XREj4U//2gksBpsL2KIE7AfaF7E0CVwLEhutJAjcCLA3ViwQuBEgN04ME9ALkhsguAbUAMeH9+fj3R4n9WIVWgCXhe5aAUoCUke9VAjoBcsp+jARsUAlQoufvW85WBWgEKDXhi1mPSQIKAUqGH7s+iwTmBVgj/NjtGCQw/W3hOeF/Onz2Zvy789ubXynnoOWzBCmYrQCp4X86fPYmFP7UMvbLQ5MC5IQfs39PEpgTYO3wp9ZnlcCUAGtO+GJglMCMAKUnfDGEtmOTwIQArUd+yrGsSKBeAG3hLzmmBQnUCxBzjf3y4uh9hVNZfEwL9wfUCwDok4AlfMCIAECeBCl3+Ka2YwofMCQA0L4SsIUPGBMASJdgaRUYr88YPmBQAGB9CbyEDxgVAIiXYBze+e3NrykRQsuYwweMvx385durqGvtlxdH78fX7THVgD18wHAFEGIDWDo59BA+QCAAUF4CL+EDJAIA5STwFD5AJABwF0zOvQJv4QNkAggpEngMHyAVAFgmgdfwAWIBgHK3jlnDB8gFAPLDYw4fcCAAkB4ie/iAEwGA5WF6CB9wJAAQH6qX8AFnAgD7w/UUPuBQAGA6ZG/hA04FAB6H7TF8oNLbwRoejBBC3k7WFD7l18UD7R+MMIWW8OkfGCFoFaEVrV+HZp8Iqv1gBI1o+Nv7Y+MaQPfYuCFdhGk0BS/0R8dWQsMzAkP0h0evjMZRP6Q/Pn4ltAcvVBFA8NAWrAQvVBVAYBVBa5+fo4kAAsv8wNqoH9JUAMD2/MBy8EJzAQRLbSH3eK3KfQg1AgjaRcjt80D7UT9EnQCCtvkBQ7kPoVYAoMz8AMgTganch1AtgNBqoshW7kOYEECo1RZYy30IUwIA67YFT8EL5gQQSorA3ufnMCuA0PJGktVRP8S8AELO/GApDMELNAIA+dUgBsvlPgSVAMIaIjCN+iGUAgglRGANXqAWQEiZH7AHL7gQAFhWDdj6/BwbAPAiATAvgpdRL+x22407AYShCN6CF1wLIJydXLsLXrgXAPAtgUd2u+0GcPwFEZ077gUQIzr8DLM+mFrQ4WSccW8BznkkQK8CvISynQ27XxlwMDeoZ1tArwb22ZdhdMC9GtgidvAmjfAug05SKvZ/yN9/uVRQSm0AAAAASUVORK5CYIKJUE5HDQoaCgAAAA1JSERSAAABAAAAAQAIBgAAAFxyqGYAAAugSURBVHic7d09rlRXFobhVciSIyxZcmrJCQPAAYPAERkJEyAhsdRjsOTECRNwQkbUDILADICkJVIkS67IkR3QG4qifs6ps/de31rrfSJ329wqbt3vPfsUXNjZRHfvfvfPzMcDItrv3+9mPdbQB2LwwHYjg9D9AzN6YJzeMej2wRg+ME+vEGz+IAwf8LM1BHe2/GDGD/jausGb6sHwAT23nAZWnwAYP6Dplm2uCgDjB7St3ejiADB+IIY1W10UAMYPxLJ0s1cDwPiBmJZs92IAGD8Q27UNnw0A4wdyuLTlTb8RCEBsJwPA1R/I5dymvwgA4wdyOrVtbgGAwj4LAFd/ILfjjXMCAAr7GACu/jU9e/LO+ylgssOtf+X5ROCnDf/5i3sf//m337/3fEpw8PH7hzkB1HA4/GNPH781M0JQQfuzA3ZmjL+CS8M/Rghq2O/f7whAAc+evFs0/GNPH78lAokRgOTWXPXP4TSQFwFIqsfwjxGCfPb797sd489jxPCPcVuQCwFI4tb7/FtwGsiDAAQ346p/DiGIjwAE5Tn8Y4QgLgIQjNLwj/H+QDwEIJCZ9/m34jQQCwEIQPmqfw4hiIEACIs4/GPcFmgjAKIiHPeX4jSgiwCIyXDVP4cQ6CEAIjIP/xgh0EEAnFUa/jHeH/BHABwp3Oc/fPP60av7D156PT6nAV8EwIHCVf/hm9ePzMxe3X/w8vCfvZ4PIfBBACZSG/6afzcLIZiLAEygPvwt/+0ovD8wBwEYLPJ9Pu8P5EcABol21R/5MbYiBOMQgM6yDH/Gx1yL24L+CEAnWYd/6jG8I2DGaaAXAtBB5Pv8Wx/LzP80YEYItiIAG1S56is+dkMItiEAN6g+fMXnwvsDtyEAKzD8y3h/IB4CsFC1+/xbKQSKECxHAK7gqn8bhefMbcF1BOAMht+H98+B08BlBOAIwx/D+/aFEJxGAA5wnz+WQtgIwecIgHHVn03h58r7Ax+UDgDD9+V92uE0UDQADF+HwuehcgjKBYD7fE2EwEeZAHDVj0Hhc1Tp/YH0AWD4MXmfkqqcBlIHwPu4z/C3Ufj8ZQ9BygCoXPUZfh8qIcgYgVQBUBm+GVf9Ebw/txlPAykCwPBr8T5dZQpB+ABwn1+Twuc9QwjCBkDlqs/wfamEIGoEwgVAZfhmXPWVeMc46mkgTAAYPq5ReH2ihSBEALjPxxoKr1eU2wLpAKhc9Rl+TN4hiHAakAyAyvDNuOpn4B1x5RBIBYDhYxSF11UxBDIB4D4fMyi8zkrvD3zl/QQUeB8RMU97nRVCoKB0APgiqOswBJVf/5IBYPhoXt1/8LLy10OpAFR+oXFe5duCMgGoftTDdRVvC9IHoGLVsU2l24K0AajyAm719PFb9z8lWVGV24J0Acj+gvXUfmMKETgvewhSBaDSvdtWbfyH/5sInJf1/YE73k8A8x2P/9r/j7wIQDHXRk4EaiEAhSwdNxGogwAUsXbURKAGAlDArWMmAvkRgOS2jpgI5EYAEus1XiKQFwFIqvdoiUBOBCChUWMlAvkQgGRGj5QI5EIAEpk1TiKQBwFIYvYoiUAOBCABrzESgfgIQHDeI/R+fGxDAAJTGZ/K88B6BCCoXqP733/+/G+Pj0MEYiIAAfUePxGoiwAEM+rKTwRqIgCBjD72E4F6CEAQs+75iUAtBCCA2W/4EYE6CIA4r3f7e0UA2giAMO9f6usRAU4B2giAKO/x9/rxZkRAGQEQpDL+nh+HCGgiAGLUxt/z4xEBPQRAiOr4e35cIqCFAIhQH3/Pj08EdBAAAVHG3/NxiICGVH87cEQe4//1629+PPfvfv77rz+WPt4Pv3z709LHPIW/kdgfAXA0c/yXRn/uv1sagy2IgC9uAZzMGv+vX3/z49Lxr/2x/Jbh+AiAg5nj7/E4RCAvAjBZtPEv+XhEIC4CMFHU8S/5uEQgJgIwSfTxL/n4RCAeAjBBlvEveRwiEAsBGCzab/LpgQjEQQAGUvx1/l6uPR4RiIEADFLxyn+MCOgjAAMw/k+IgDYC0Jna7+0faenjEgFdBKAjrvznEQFNBKATxn8dEdBDADpg/MsRAS0EoINe38669fvrI+j1c+RbiPsgAJ0QgesYvx4C0BEROI/xayIAnXlEYMaf3LPlcRm/LgIwACeBTxi/NgIwCBFg/BEQgIFmRmD2bcC1x2P8MRCAwSqeBBh/HARgglkRmHUKuPQ4jD8WAjBJlggw/lwIwETRI8D48yEAk0WNAOPPiQA4iBYBxp8XAXDSMwKXRvjz33/9cWsIrv1Yxh8ffzmoo+cv7nX7ttYffvn2p0vfans45B5/OzDjz4EAOJsZgWbrrQHjz4NbAAE9hzD6Nwwx/lwIgIgIEWD8+RAAIcoRYPw5EQAxihFg/HkRAEFKEWD8uREAUQoRYPz5EQBhz1/cc/t2YsZfAwEIYHYEGH8dBCCIWRFg/LUQgEBGR4Dx10MAghkVAcZfEwEIqHcEGH9dBCAotT9slPHHRAACUxmdyvPAegQgOO/xeT8+tiEACXiNkPHHRwCSmD1Gxp8DAUhk1igZfx4EIJnR42T8uRCAhEaNlPHnQwCS6j1Wxp8TAUis12gZf14EILmt42X8uRGAAm4dMePPjwAUsXbMjL8GAlDI0lEz/joIQDHXxs34ayEABZ0bOeOvJ9VfDvrq/oOXD9+8ftT+2fv5KDv+S0kZ/2VZv65SBcDs0wuU9QXrqUWA8Z+X/esoXQAaQrAM4z+tytdN2gA0hyHI/mKij0pfK+kD0PD+AK6p+PVRJgBm3BbgtMpfD6UC0BACNJWO+6eUDEDD+wN1Ef8PSgeg4f2BOnidP7e7e/e7f7yfRPPsyTsz8/2lKb5AclJ4XdtvvPrt9++9nsIXpALQEAL05H2Lpzj8RjIAjUoIiEBM3hFXHn4jHYDm2ZN37hEw4zQQhcLr9fTxW+nhNyECYKZzGjAjBKoUXp8IV/1DYQLQEAKc4n2rFm34TbgANCohIAK+FGIc5bh/StgANLw/UJPC5z3qVf9Q+ACY6ZwGzAjBDN4nrwzDb1IEoCEEuXl/bjMNv0kVgEYlBESgD+/hm8W+z78kZQAa3h+ITeHzl/Gqfyh1AMx0TgNmhGAN7xNU9uE36QPQEIIYFD5HWY/7p5QJQON9W2Dmf3VTpDJ8s/xX/UPlAmDGaUCJwueh4vCbkgFoCIEv75NQ5eE3pQPQEIK5FH6ule7zLyEAB3h/YCyV4ZvVvuofIgBHOA2M4R02hn8aATiDEPTh/XNg+JcRgCsIwW0UnjP3+dcRgIV4f2AZleGbcdVfggCswGngMu9AMfz1CMANCIHec+G4fxsCsEH1EKgM34yr/q0IQAfV3h9g+HkQgE6qnAa4z8+FAHSWNQQqV32G3xcBGCRLCFSGb8ZVfwQCMFjk9wc47udHACaIdhpQueoz/PEIwETqIVAZvhlX/VkIgAO1EDD8ugiAo8jvD/TC8H0RAGcKpwEv3Of7IwAiKoWAq74OAiAmcwgYvh4CIErh/YFeGL4uAiAsw2mA+3xtBCCAiCHgqh8DAQgkwm0Bw4+FAASjfBrguB8PAQhKKQRc9eMiAMF5hoDhx0cAkpj5/gDDz4MAJDLjNMB9fi47MzMikMuIEHDVz2e/f78jAIn1CAHDz4sAFHHr+wMc93MjAIWsOQ1w1a/hYwDMiEAVl0LA8OvY79/vzP7/JqAZAajmMAQMvx4CADP7EAKGX88XATAjAkAFbfxmZnc8nwgAX58F4LAMAPI53jgnAKCwLwLAKQDI6dS2T54AiACQy7lNcwsAFHY2AJwCgBwubfniCYAIALFd2/DVWwAiAMS0ZLuL3gMgAkAsSze7+E1AIgDEsGarq34VgAgA2tZudPUvAxIBQNMt29w0Zr57EPC35aK86TcCcRoAfG3dYLcBcxoA5ul18e1+BScEwDi9T91Dj/DEANhu5K321Ht4ggBcN/O9tX8BtBgE8JxH5YIAAAAASUVORK5CYII="
_ICON_32_B64  = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABjklEQVR4nM2Xv0oDQRDGvzWCVQTBJoVgcw9wFnmIWKVLkxcIQhrBziKdYCMc9wI2dleZh0hhHiCNkMImIHiVhWg1MKx7k9nZeHGau9t/3+++XXZ3HFh0u6ffaCHqeuPo3bUpHAI5SB1kOl4n9XfWvyfh8inDZLQCADw8nkWPc5giDACD5WJY5llFdbEQaoCQMADM835F72WeVdROC6Kagul4HRT22w2WiyGVa6dFBAj9dUjYh+CAk9FKhAgCSHZL4j6Ixo1fAFq7tRC8f8iNxkWosZsGJWA/qL80VtJGRNbS0xJmABJ9vXl/ToEwAfji9LRE9E7Ixe+Pji+ovIC8HpoiyoEmcQC4uv164212DuDbHgrLelADkLXndyeXTW2oLmYaoqaAQxSzTo/X0fefrgESIJFi1uldf368WMVNABwEsNm+EwAuahUHhH2AXzSkM0ES1/T/f8fxNpBWLiQSSKtXshCIdCmd5/0q9ooenRdI07LN7p0AhEBSEpPk3NCSjFDU9cbtPTl1vGAf6fkPtfcj9onyIM8AAAAASUVORK5CYII="
_ICON_64_B64  = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACk0lEQVR4nO2bMU7DMBSG/0RITEVCYkVi6QHK0EPAxNalF+jSBYkzILGw9AIs3TrRQzDAAbogda2ERCYmGJCF9WrHceL3XprwS4jWSep8X2IrcZwMngwGZ9++ZYeYothlrvK9wq6B01ARuf2l6/DAPmPuW9Dl2Kw5LehLDHMeWpE78+lWtf5M6+gb8MVyiNlkAwB4fDoX3w9xATY4jYYIMQFl4DSSItgFhMCv3l5u1qPxyrVsNtmwS2ATUAUcANaj8cr+TNfjPhuSC4gBj1nGJSKpgPl0Wws8Zt3UIpIIKDvqMeCubcv6B6C5iEYCuMBjfqdpR1lLQJOevW64mkWUgCYdXKqkbhaVBLQBPKa+GBFBAal6do6k6B+OOCqWiqm/yf5EC0jdwc0mm0r3B2WxRcTum+p4gGmr5r9G1ARQaC0JKgJ8sBoSxAVQyPe7j+ey5dwRFeCD15QgJiB05Ol3qYgICMG7yqXOAnYBVeGrbMsRVgEh+Ifjk0vz51uHWwKbgCrwvu+SElgExMK7yqUkJBfQpM3TSEhILoDe2Fzcn17X/S26bdObJldYmkBIwu3X56trO7tcAh5g7ARjJWjAAzUHRKrGfvIL/IGZtu06EyThAYELIReAr1+QhgeELoUXy2GwSWjAA8J3gz4JWvCAwnhA6EyQhAeURoR8kNLwgOKYIIXVgAeUR4UNtBY8UOM6IDSjIzYp4EUfjNgVaT8hSlH//8PR/8fjTBMkgLQiWjFBgkZipkgrp8jQ9HaSFE0qEQc3TY6m7qySg58oaae3U2VpejtZmqa30+VpevvCBE1rXpkBdN8am0+3KuDA70uU6gI0UxS7LDcftHdGOoY5pwV9iM2a+xZ0NZTRC9y1fsF3cH8AITY+a6DPPZMAAAAASUVORK5CYII="
_ICON_128_B64 = "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAFZklEQVR4nO2dPW4UQRCF31pIjkCyRIpEwgEg4BAQkTnxBZw4scQZLJGQcAESMiJ8CAI4gBMkpysheSNHEFhljcc9sz3dPd1Vr/qLjOfX+76u6plddjZI4OnT5/9Stuusy2633SzdJnqDHrotYmXYu1IP3jb7RDiYW9jDt8++DIN29OA5CVWDRxWgh89LKNvZFtDh54EAffTzM874YGpBh5dh1r0FOOcA8D36z06uW59CEyTzJ61PpBUS/Jdvr+5//vz1RctTasIG8FUBhsGPOT2+AuBHhN1uu9l4CX8u+DGnx1duJHAhwNnJdVTwQ7xUA2oBloz6KdhFoBSgRPBjWEWgEmCN4MewzQ9oBEjp86kwVQPzAuSO+ne/f364fP32e8q2DCKYFaBE8ABw+frt9+HPKfuy3BbMCVAy+CXL9mG1GpgSIKfPLwnXkwgmBGjV53PnBxYkUC3AmuW+xj4sVAO1AtQq9zX2qVkEdQLkjPo1gg8dg+myUY0A2oMveTxN84PmArS8kZMLQ1toKoC2Pp+KZRGaCGCp3C/B4mVjVQFYgx9irRpUEcByn0/FigirC8DS51PRLsJqAngo90vQOj8oLkAPfhqN1aCYAD34eDSJUESA3D7vJfgxGtpCs/8a5m3UhyjxaaRcqgvQ+g/WhrwOrV6XagJoDf70+Krap4nnaCVCFQG09nmZUGmRAHgoQo3XzO0XREj4U//2gksBpsL2KIE7AfaF7E0CVwLEhutJAjcCLA3ViwQuBEgN04ME9ALkhsguAbUAMeH9+fj3R4n9WIVWgCXhe5aAUoCUke9VAjoBcsp+jARsUAlQoufvW85WBWgEKDXhi1mPSQIKAUqGH7s+iwTmBVgj/NjtGCQw/W3hOeF/Onz2Zvy789ubXynnoOWzBCmYrQCp4X86fPYmFP7UMvbLQ5MC5IQfs39PEpgTYO3wp9ZnlcCUAGtO+GJglMCMAKUnfDGEtmOTwIQArUd+yrGsSKBeAG3hLzmmBQnUCxBzjf3y4uh9hVNZfEwL9wfUCwDok4AlfMCIAECeBCl3+Ka2YwofMCQA0L4SsIUPGBMASJdgaRUYr88YPmBQAGB9CbyEDxgVAIiXYBze+e3NrykRQsuYwweMvx385durqGvtlxdH78fX7THVgD18wHAFEGIDWDo59BA+QCAAUF4CL+EDJAIA5STwFD5AJABwF0zOvQJv4QNkAggpEngMHyAVAFgmgdfwAWIBgHK3jlnDB8gFAPLDYw4fcCAAkB4ie/iAEwGA5WF6CB9wJAAQH6qX8AFnAgD7w/UUPuBQAGA6ZG/hA04FAB6H7TF8oNLbwRoejBBC3k7WFD7l18UD7R+MMIWW8OkfGCFoFaEVrV+HZp8Iqv1gBI1o+Nv7Y+MaQPfYuCFdhGk0BS/0R8dWQsMzAkP0h0evjMZRP6Q/Pn4ltAcvVBFA8NAWrAQvVBVAYBVBa5+fo4kAAsv8wNqoH9JUAMD2/MBy8EJzAQRLbSH3eK3KfQg1AgjaRcjt80D7UT9EnQCCtvkBQ7kPoVYAoMz8AMgTganch1AtgNBqoshW7kOYEECo1RZYy30IUwIA67YFT8EL5gQQSorA3ufnMCuA0PJGktVRP8S8AELO/GApDMELNAIA+dUgBsvlPgSVAMIaIjCN+iGUAgglRGANXqAWQEiZH7AHL7gQAFhWDdj6/BwbAPAiATAvgpdRL+x22407AYShCN6CF1wLIJydXLsLXrgXAPAtgUd2u+0GcPwFEZ077gUQIzr8DLM+mFrQ4WSccW8BznkkQK8CvISynQ27XxlwMDeoZ1tArwb22ZdhdMC9GtgidvAmjfAug05SKvZ/yN9/uVRQSm0AAAAASUVORK5CYII="

def _get_photo(b64, master):
    """Decode base64 PNG into a tkinter PhotoImage."""
    import io
    from PIL import Image, ImageTk
    data = _b64.b64decode(b64)
    img  = Image.open(io.BytesIO(data))
    return ImageTk.PhotoImage(img, master=master)

def _set_window_icon(root):
    """Set .ico as window icon (Windows taskbar + titlebar)."""
    try:
        import io, tempfile
        data = _b64.b64decode(_ICON_ICO_B64)
        tmp  = tempfile.NamedTemporaryFile(suffix=".ico", delete=False)
        tmp.write(data); tmp.close()
        root.iconbitmap(tmp.name)
    except Exception:
        pass

# ── Constants ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(sys.executable if getattr(sys,'frozen',False) else __file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
LOCAL_APP   = os.environ.get("LOCALAPPDATA","")
FOOTER      = "MultiFMacro | discord.gg/qGBB8T6xsw"
VERSION     = "v3.2"

BIOME_COLORS = {
    "WINDY":0x90F7FF,"SNOWY":0xC4F5F6,"RAINY":0x4385FF,"SAND STORM":0xF4C27C,
    "HELL":0x5C1219,"STARFALL":0x6784E0,"CORRUPTION":0x9042FF,"NULL":0x000001,
    "GLITCHED":0x65FF00,"DREAMSPACE":0xFF7DFF,
}

BASE_IMG = "https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/img/biome/"
BIOME_IMAGES = {
    "WINDY":        BASE_IMG + "WINDY.png",
    "SNOWY":        BASE_IMG + "SNOWY.png",
    "RAINY":        BASE_IMG + "RAINY.png",
    "SAND STORM":   BASE_IMG + "SANDSTORM.png",
    "HELL":         BASE_IMG + "HELL.png",
    "STARFALL":     BASE_IMG + "STARFALL.png",
    "CORRUPTION":   BASE_IMG + "CORRUPTION.png",
    "NULL":         BASE_IMG + "NULL.png",
    "GLITCHED":     BASE_IMG + "GLITCHED.png",
    "DREAMSPACE":   BASE_IMG + "DREAMSPACE.png",
}
CYBERSPACE_ALWAYS_ON = {"GLITCHED", "DREAMSPACE", "CYBERSPACE"}
KNOWN_BIOMES = set(BIOME_COLORS.keys()) | {"NORMAL", "CYBERSPACE"}

CAL = {
    "open_inventory":(38,511),"items_btn":(1272,335),"search_bar":(890,364),
    "first_inv_item":(844,443),"item_amount":(566,575),"use_item":(686,578),
    "close_menu":(1414,296),
    "autocraft_search":(940,336),"autocraft_first_potion":(1157,408),
    "autocraft_craft":(580,574),
    "merchant_amount":(683,596),"merchant_purchase":(747,642),
    "merchant_slot_1":(577,719),"merchant_slot_2":(767,719),
    "merchant_slot_3":(954,718),"merchant_slot_4":(1154,719),
    "merchant_slot_5":(1337,716),"merchant_close":(1408,335),
}

AURA_LIST = [  # (name, rarity_display) sorted by rarity ascending
    ("Memory, The Fallen", "Oblivion Potion"),
    ("Oblivion: The truth seeker", "Oblivion Potion"),
    ("Exotic", "1/99,999"),
    ("Diaboli: Void", "1/100,400"),
    ("Undead: Devil", "1/120,000"),
    ("Comet", "1/120,000"),
    ("Jade", "1/125,000"),
    ("Spectre", "1/140,000"),
    ("Jazz", "1/160,000"),
    ("Aether", "1/180,000"),
    ("Bounded", "1/200,000"),
    ("Celestial", "1/350,000"),
    ("Kyawthuite", "1/850,000"),
    ("Arcane", "1/1,000,000"),
    ("Magnetic: Reverse Polarity", "1/1,024,000"),
    ("Undefined", "1/1,111,000"),
    ("Rage: Brawler", "1/1,280,000"),
    ("Astral", "1/1,336,000"),
    ("Gravitational", "1/2,000,000"),
    ("Bounded: Unbound", "1/2,000,000"),
    ("Virtual", "1/2,500,000"),
    ("Savior", "1/3,200,000"),
    ("Poseidon", "1/4,000,000"),
    ("Aquatic: Flame", "1/4,000,000"),
    ("Zeus", "1/4,500,000"),
    ("Lunar: Full Moon", "1/5,000,000"),
    ("Solar: Solstice", "1/5,000,000"),
    ("Galaxy", "1/5,000,000"),
    ("Twilight", "1/6,000,000"),
    ("Origin", "1/6,500,000"),
    ("Hades", "1/6,666,666"),
    ("Celestial: Divine", "1/7,000,000"),
    ("Hyper-volt", "1/7,500,000"),
    ("Nihility", "1/9,000,000"),
    ("Starscourge", "1/10,000,000"),
    ("Sailor", "1/12,000,000"),
    ("Glitch", "1/12,000,000"),
    ("Stormal: Hurricane", "1/13,500,000"),
    ("Sirius", "1/14,000,000"),
    ("Arcane: Legacy", "1/15,000,000"),
    ("Chromatic", "1/20,000,000"),
    ("Aviator", "1/24,000,000"),
    ("Arcane: Dark", "1/30,000,000"),
    ("Ethereal", "1/35,000,000"),
    ("Overseer", "1/45,000,000"),
    ("Exotic: Apex", "1/49,999,500"),
    ("Matrix", "1/50,000,000"),
    ("Twilight: Iridescent Memory", "1/60,000,000"),
    ("Sailor: Flying Dutchman", "1/80,000,000"),
    ("Chromatic: Genesis", "1/99,999,999"),
    ("Spectraflow", "1/100,000,000"),
    ("Starscourge: Radiant", "1/100,000,000"),
    ("Overture", "1/150,000,000"),
    ("Symphony", "1/175,000,000"),
    ("Felled", "1/180,000,000"),
    ("Twilight: Withering Grace", "1/180,000,000"),
    ("Impeached", "1/200,000,000"),
    ("Lumenpool", "1/220,000,000"),
    ("Oppression", "1/220,000,000"),
    ("Hyper-Volt: Ever-Storm", "1/225,000,000"),
    ("Shard Surfer", "1/225,000,000"),
    ("Archangel", "1/250,000,000"),
    ("Astral: Zodiac", "1/267,200,000"),
    ("Prophecy", "1/275,649,430"),
    ("Exotic: Void", "1/299,999,999"),
    ("Bloodlust", "1/300,000,000"),
    ("Overture: History", "1/300,000,000"),
    ("Maelstrom", "1/309,999,999"),
    ("Perpetual", "1/315,000,000"),
    ("Orchestra", "1/336,870,912"),
    ("Atlas", "1/360,000,000"),
    ("Flora: Evergreen", "1/370,073,730"),
    ("Chillsear", "1/375,000,000"),
    ("Abyssal Hunter", "1/400,000,000"),
    ("Gargantua", "1/430,000,000"),
    ("Apostolos", "1/444,000,000"),
    ("Unknown", "1/444,444,444"),
    ("Kyawthuite: Remembrance", "1/450,000,000"),
    ("Ruins", "1/500,000,000"),
    ("Matrix: Overdrive", "1/503,000,000"),
    ("Elude", "1/555,555,555"),
    ("Sophyra", "1/570,000,000"),
    ("Matrix: Reality", "1/601,020,102"),
    ("Prologue", "1/666,616,111"),
    ("Pythios", "1/666,666,666"),
    ("Aegis", "1/825,000,000"),
    ("dreamscape", "1/850,000,000"),
    ("Ruins: Withered", "1/800,000,000"),
    ("Ascendant", "1/935,000,000"),
    ("Nyctophobia", "1/1,011,111,010"),
    ("Pixelation", "1/1,073,741,824"),
    ("Luminosity", "1/1,200,000,000"),
    ("Leviathan", "1/1,730,400,000"),
    ("Breakthrough", "1/1,999,999,999"),
    ("Equinox", "1/2,500,000,000"),
    ("Monarch", "1/3,000,000,000"),
    ("Sovereign", "1/750,000,000"),
]

# ── Design tokens ─────────────────────────────────────────────────────────
BG0="#0d0d0d"; BG1="#111111"; BG2="#171717"; BG3="#1e1e1e"; BDR="#252525"
BORDER_OUTER="#0d0d0d"
ACC="#7c6af7"; ACC2="#5ce1e6"; ACC3="#ff6b9d"
TXT="#ddddf0"; TXT2="#666680"; TXT3="#363648"
GREEN="#2ecc71"; GOLD="#f0a500"
FONT_H=("Segoe UI",11,"bold"); FONT_B=("Segoe UI",9)
FONT_S=("Segoe UI",9); FONT_MONO=("Consolas",9)
FONT_LABEL=("Segoe UI",8)

# ── Config ────────────────────────────────────────────────────────────────
def _cfg_key(name):
    """Sanitize a name into a safe configparser key (no colons, spaces, or special chars)."""
    return re.sub(r'[^a-z0-9_]', '_', name.lower().replace(" ", "_"))

def load_config():
    cfg = configparser.ConfigParser()
    D = {
        "Webhook":   {"webhook_url":"","private_server":"","discord_user_id":""},
        "Biomes":    {_cfg_key(b):"Message" for b in BIOME_COLORS},
        "Aura":      {"enabled":"1","ping_on_aura":"1"},
        "AuraFilter": {},
        "AntiKick":  {"enabled":"1","interval_sec":"600"},
        "Fishing":   {"loop_count":"15","sell_all":"0","pathing":"VIP"},
        "Merchant":  {"log_detection":"1","ping_mari":"0","ping_jester":"0"},
        "Player":    {"roblox_username":""},
        "BiomePing": {},
        "BiomeCounts": {},
    }
    if not os.path.exists(CONFIG_FILE):
        for s,v in D.items(): cfg[s]=v
        with open(CONFIG_FILE,"w") as f: cfg.write(f)
    cfg.read(CONFIG_FILE)
    changed=False
    for s,v in D.items():
        if not cfg.has_section(s): cfg[s]=v; changed=True
    if changed:
        with open(CONFIG_FILE,"w") as f: cfg.write(f)
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE,"w") as f: cfg.write(f)

# ══════════════════════════════════════════════════════════════════════════
#  Log reading — ported directly from SolsScope roblox_utils.py
# ══════════════════════════════════════════════════════════════════════════
def _get_log_dir():
    """Return Roblox log directory (Player or MS Store)."""
    p = os.path.join(LOCAL_APP,"Roblox","logs")
    if os.path.isdir(p): return p
    ms = os.path.join(LOCAL_APP,"Packages",
                      "ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr","LocalState","logs")
    if os.path.isdir(ms): return ms
    # fallback: scan Packages
    pkg = os.path.join(LOCAL_APP,"Packages")
    if os.path.isdir(pkg):
        for folder in os.listdir(pkg):
            if "ROBLOX" in folder.upper():
                lp = os.path.join(pkg,folder,"LocalState","logs")
                if os.path.isdir(lp): return lp
    return None

def fetch_avatar_url(user_id):
    """Fetch headshot URL from Roblox thumbnails API."""
    try:
        r = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=48x48&format=Png",
            timeout=5
        )
        data = r.json()
        return data["data"][0]["imageUrl"]
    except Exception as e:
        print(f"[Avatar] {e}")
    return None

def _get_latest_log_content():
    """
    Copy latest log to temp and return lines.
    Mirrors SolsScope _get_latest_log_content().
    """
    d = _get_log_dir()
    if not d: return None
    try:
        logs = [f for f in glob.glob(os.path.join(d,"*.log"))
                if "Installer" not in f and "bootstrapper" not in f]
        if not logs: return None
        latest = max(logs, key=os.path.getctime)
        tmp = os.path.join(tempfile.gettempdir(), f"biomemacro_{os.path.basename(latest)}")
        shutil.copy2(latest, tmp)
        with open(tmp,"r",encoding="utf-8",errors="ignore") as f:
            content = f.readlines()
        try: os.remove(tmp)
        except: pass
        return content
    except Exception:
        return None

def get_latest_hovertext():
    """
    Extract current biome from log.
    SolsScope reads data.largeImage.hoverText from JSON in the log line.
    """
    content = _get_latest_log_content()
    if not content: return None
    json_pattern = re.compile(r'\{.*\}')
    for line in reversed(content):
        m = json_pattern.search(line)
        if not m: continue
        try:
            j = json.loads(m.group())
            # SolsScope checks message.properties.HoverText first, then data.largeImage.hoverText
            ht = (j.get("message",{}).get("properties",{}).get("HoverText")
                  or j.get("data",{}).get("largeImage",{}).get("hoverText"))
            if ht:
                return ht.strip().upper()
        except (json.JSONDecodeError, Exception):
            continue
    return None

def get_latest_equipped_aura():
    """
    Extract the most recently equipped aura from the Roblox log.
    """
    content = _get_latest_log_content()
    if not content: return None
    json_pattern = re.compile(r'\{.*\}')
    for line in reversed(content):
        m = json_pattern.search(line)
        if not m: continue
        try:
            j = json.loads(m.group())
            state = (j.get("message",{}).get("properties",{}).get("State")
                     or j.get("data",{}).get("state"))
            if not state: continue
            state = state.strip()
            if state == "In Main Menu": continue
            if state.startswith('Equipped "') and state.endswith('"'):
                aura = state[len('Equipped "'):-1]
                return aura.replace("_",": ")
        except (json.JSONDecodeError, Exception):
            continue
    return None

def get_latest_merchant(previous_ts: float):
    """
    Extract merchant spawn from log.
    NOTE: Requires Roblox FastFlags to be enabled. If Roblox has disabled
    FastFlags (which they do periodically), this will not detect merchants.
    """
    content = _get_latest_log_content()
    if not content: return None
    from datetime import datetime

    merchant_pattern = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z),.*'
        r'\[FLog::Output\]\s+\[ExpChat/mountClientApp\s+\(Debug\)\]\s+-\s+Incoming MessageReceived Status: Success Text:\s*'
        r'(?:<.*?>)?\[Merchant\]:\s*(?P<n>[A-Za-z]+)\s+has arrived on the island',
        re.IGNORECASE
    )
    # Broader fallback pattern in case log format varies
    fallback_pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z).*'
        r'\[Merchant\]:\s*(?P<n>Mari|Jester)\s+has arrived',
        re.IGNORECASE
    )

    try:
        for line in reversed(content):
            for pat in (merchant_pattern, fallback_pattern):
                match = pat.search(line)
                if not match: continue
                try:
                    name = match.group("n").strip().capitalize()
                    timestamp_str = match.group("timestamp").strip()
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    unix_ts = dt.timestamp()
                    if unix_ts > previous_ts:
                        print(f"[Merchant] Detected: {name} at {timestamp_str}")
                        return name, unix_ts
                except Exception:
                    continue
    except Exception as e:
        print(f"[Merchant] Error: {e}")
    return None

# ── Webhook ───────────────────────────────────────────────────────────────
def send_webhook(url, payload):
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[Webhook] HTTP error: {e} — response: {e.response.text if e.response else 'N/A'}")
    except Exception as e:
        print(f"[Webhook] Failed to send: {e}")

def get_roblox_user_id(username):
    """Get Roblox userId from username via API."""
    try:
        r = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": False},
            timeout=8
        )
        data = r.json().get("data", [])
        if data:
            return str(data[0].get("id", ""))
    except Exception as e:
        print(f"[RobloxAPI] {e}")
    return None

def fetch_avatar_image(user_id, size=48):
    """Fetch Roblox headshot via API, return PIL Image or None."""
    try:
        from PIL import Image, ImageTk
        import io
        url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=48x48&format=Png"
        resp = requests.get(url, timeout=5)
        img_url = resp.json()["data"][0]["imageUrl"]
        img_data = requests.get(img_url, timeout=5).content
        img = Image.open(io.BytesIO(img_data)).resize((size, size))
        return img
    except Exception as e:
        print(f"[Avatar] Error: {e}")
    return None

def make_embed(desc="", color=0x7c6af7, title=None):
    e = {"description":desc,"color":color,"footer":{"text":FOOTER}}
    if title: e["title"] = title
    return {"embeds":[e]}

def make_biome_embed(biome, is_start, ps, disc_id, setting, ping_biomes=None):
    ts = time.strftime("%H:%M:%S")
    color = BIOME_COLORS.get(biome, 0x7c6af7)
    ps_ln = f"\n{ps}" if (ps and is_start) else ""
    label = "Biome Started" if is_start else "Biome Ended"
    embed = {
        "title": f"[{ts}]",
        "color": color,
        "description": f"> ## {label} - {biome}{ps_ln}",
        "footer": {"text": FOOTER},
    }
    img = BIOME_IMAGES.get(biome)
    if img:
        embed["thumbnail"] = {"url": img}
    payload = {"embeds": [embed]}
    if is_start:
        if biome in CYBERSPACE_ALWAYS_ON:
            payload["content"] = "@everyone"
        elif ping_biomes and biome in ping_biomes and disc_id:
            payload["content"] = f"<@{disc_id}>"
        elif setting == "Ping" and disc_id and not ping_biomes:
            payload["content"] = f"<@{disc_id}>"
    return payload

def _get_aura_rarity_number(aura_name):
    """Return the 1-in-X number for an aura, or 0 if unknown/special."""
    rarity = _get_aura_rarity(aura_name)
    if rarity.startswith("1/"):
        try:
            return int(rarity[2:].replace(",", ""))
        except ValueError:
            return 0
    return 0  # special auras like Oblivion Potion

def _get_aura_rarity(aura_name):
    """Look up rarity string from AURA_LIST for a given aura name."""
    name_lower = aura_name.lower()
    for name, rarity in AURA_LIST:
        if name.lower() == name_lower:
            return rarity
    # fuzzy fallback — check if aura_name is contained in a known name
    for name, rarity in AURA_LIST:
        if name_lower in name.lower() or name.lower() in name_lower:
            return rarity
    return "Unknown"

def make_aura_embed(aura, disc_id, ping):
    ts = time.strftime("%H:%M:%S")
    rarity = _get_aura_rarity(aura)
    desc = f"> ✨ **{aura}**\n> 🎲 **Rarity:** {rarity}"
    payload = {"embeds":[{
        "title": f"[{ts}] Aura Detected",
        "color": 0xf5a623,
        "description": desc,
        "footer": {"text": FOOTER}
    }]}
    if ping and disc_id: payload["content"] = f"<@{disc_id}>"
    return payload

MERCHANT_IMAGES = {
    "Mari":   "https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest",
    "Jester": "https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest",
}

def make_merchant_embed(name, ps=""):
    ts = time.strftime("%H:%M:%S")
    colors = {"Mari":0xFFFFFF,"Jester":0xB031FF}
    desc = f"**{name}** has arrived!\n**Time:** <t:{int(time.time())}>"
    if ps: desc += f"\n{ps}"
    embed = {"title":f"[{ts}] 🛒 Merchant","color":colors.get(name,0x7c6af7),
             "description":desc,"footer":{"text":FOOTER}}
    img = MERCHANT_IMAGES.get(name)
    if img:
        embed["thumbnail"] = {"url": img}
    return {"embeds":[embed]}

# ── pyautogui helpers ─────────────────────────────────────────────────────
def _activate_roblox():
    try:
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None,"Roblox")
        if hwnd: ctypes.windll.user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)
    except: time.sleep(0.3)

def _click(x, y, d=0.3):
    if not PAG_OK: return
    pyautogui.moveTo(x, y, duration=0.15)
    pyautogui.click()
    time.sleep(d)

def _paste(text):
    """Paste text via clipboard — works with spaces and special chars."""
    import pyperclip
    pyperclip.copy(str(text))
    pyautogui.hotkey("ctrl","v")
    time.sleep(0.2)

def do_anti_kick():
    if not PAG_OK: return
    try:
        _activate_roblox()
        pyautogui.keyDown("space"); time.sleep(0.1); pyautogui.keyUp("space")
    except: pass

# Relative coords as fractions of the Roblox window (1920x1080 reference).
# These work in ANY resolution and both fullscreen and windowed mode.
AHK_ITEM_REL = {
    "open_inventory": (46/1920,  520/1080),
    "items_btn":      (1279/1920, 342/1080),
    "search_bar":     (1104/1920, 368/1080),
    "first_item":     (848/1920,  479/1080),
    "use_item":       (682/1920,  578/1080),
    "close_menu":     (1413/1920, 297/1080),
}

def _get_roblox_window():
    """Return (x, y, w, h) of the Roblox window, or None if not found."""
    try:
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, "Roblox")
        if not hwnd:
            return None
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
        pt = ctypes.wintypes.POINT(0, 0)
        ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w < 100 or h < 100:
            return None
        return pt.x, pt.y, w, h
    except Exception:
        return None

def _rel_click(key, D=0.3):
    """Click a relative coord key, scaled to actual Roblox window size/position."""
    rx, ry = AHK_ITEM_REL[key]
    win = _get_roblox_window()
    if win:
        wx, wy, ww, wh = win
        x = int(wx + rx * ww)
        y = int(wy + ry * wh)
    else:
        # Fallback: use raw 1920x1080 absolute coords (fullscreen)
        sw, sh = get_screen_size()
        x = int(rx * sw)
        y = int(ry * sh)
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    time.sleep(D)

def use_item(item_name, amount, cb=None):
    """
    Use an inventory item. Works in both fullscreen and windowed Roblox.
    Coords are relative to the Roblox client window so resolution/mode doesn't matter.
    Steps: open_inventory -> items_btn -> search_bar -> paste name ->
           first_item -> use_item -> close_menu
    """
    def st(m):
        if cb: cb(m)
    if not PAG_OK: st("pyautogui not installed"); return False
    D = 0.3
    try:
        _activate_roblox()
        st(f"Using {item_name}...")
        _rel_click("open_inventory", D)
        _rel_click("items_btn",      D)
        _rel_click("search_bar",     D)
        _paste(item_name); time.sleep(D)
        _rel_click("first_item",     D)
        _rel_click("use_item",       D)
        _rel_click("close_menu",     D)
        st(f"✓ Used {item_name}"); return True
    except Exception as e:
        st(f"Error: {e}")
        try:
            _rel_click("close_menu", 0)
        except: pass
        return False
# ══════════════════════════════════════════════════════════════════════════
#  UI helpers
# ══════════════════════════════════════════════════════════════════════════
def entry(parent, var, width=28, **kw):
    return tk.Entry(parent, textvariable=var, bg=BG3, fg=TXT,
                    insertbackground=ACC2, font=FONT_MONO, relief="flat",
                    highlightthickness=1, highlightbackground=BDR,
                    highlightcolor=ACC, bd=0, width=width, **kw)

def check(parent, text, var, bg=BG2, **kw):
    return tk.Checkbutton(parent, text=text, variable=var, bg=bg, fg=TXT2,
                          selectcolor=BG3, activebackground=bg,
                          activeforeground=TXT, font=FONT_S, cursor="hand2", **kw)

def card(parent, **kw):
    return tk.Frame(parent, bg=BG2, **kw)

def sec(parent, text, row=0, cs=4):
    tk.Label(parent, text=text, bg=BG2, fg=TXT3,
             font=("Segoe UI",7,"bold")).grid(
        row=row, column=0, columnspan=cs, sticky="w", padx=12, pady=(6,2))

def div(parent, row, cs=4):
    tk.Frame(parent, bg=BDR, height=1).grid(
        row=row, column=0, columnspan=cs, sticky="ew", padx=10, pady=0)

def btn(parent, text, cmd, color=ACC, **kw):
    return tk.Button(parent, text=text, command=cmd, bg=color, fg=TXT,
                     font=FONT_LABEL, relief="flat", bd=0,
                     padx=10, pady=5, activebackground=BG3,
                     activeforeground=TXT, cursor="hand2", **kw)

def lbl(parent, text, fg=TXT2, bg=BG2, **kw):
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=FONT_S, **kw)

def note_box(parent, text, bg=BG1):
    f = tk.Frame(parent, bg=BG3, highlightthickness=1, highlightbackground=BDR)
    f.pack(fill="x", pady=(4,0))
    tk.Label(f, text=text, bg=BG3, fg=TXT2, font=FONT_S,
             wraplength=720, justify="left").pack(padx=12, pady=8, anchor="w")

def page_header(parent, title, subtitle=None):
    tk.Label(parent, text=title, bg=BG1, fg=TXT,
             font=("Segoe UI",11,"bold")).pack(anchor="w")
    if subtitle:
        tk.Label(parent, text=subtitle, bg=BG1, fg=TXT3, font=FONT_S).pack(anchor="w", pady=(1,0))
    tk.Frame(parent, bg=BDR, height=1).pack(fill="x", pady=(6,10))

# ══════════════════════════════════════════════════════════════════════════
#  App
# ══════════════════════════════════════════════════════════════════════════

AURA_LIST = [
    ("Memory, The Fallen", "Oblivion Potion"),
    ("Oblivion: The truth seeker", "Oblivion Potion"),
    ("Exotic", "1/99,999"),
    ("Diaboli: Void", "1/100,400"),
    ("Undead: Devil", "1/120,000"),
    ("Comet", "1/120,000"),
    ("Jade", "1/125,000"),
    ("Spectre", "1/140,000"),
    ("Jazz", "1/160,000"),
    ("Aether", "1/180,000"),
    ("Bounded", "1/200,000"),
    ("Celestial", "1/350,000"),
    ("Kyawthuite", "1/850,000"),
    ("Arcane", "1/1,000,000"),
    ("Magnetic: Reverse Polarity", "1/1,024,000"),
    ("Undefined", "1/1,111,000"),
    ("Rage: Brawler", "1/1,280,000"),
    ("Astral", "1/1,336,000"),
    ("Gravitational", "1/2,000,000"),
    ("Bounded: Unbound", "1/2,000,000"),
    ("Virtual", "1/2,500,000"),
    ("Savior", "1/3,200,000"),
    ("Poseidon", "1/4,000,000"),
    ("Aquatic: Flame", "1/4,000,000"),
    ("Zeus", "1/4,500,000"),
    ("Lunar: Full Moon", "1/5,000,000"),
    ("Solar: Solstice", "1/5,000,000"),
    ("Galaxy", "1/5,000,000"),
    ("Twilight", "1/6,000,000"),
    ("Origin", "1/6,500,000"),
    ("Hades", "1/6,666,666"),
    ("Celestial: Divine", "1/7,000,000"),
    ("Hyper-volt", "1/7,500,000"),
    ("Nihility", "1/9,000,000"),
    ("Starscourge", "1/10,000,000"),
    ("Sailor", "1/12,000,000"),
    ("Glitch", "1/12,000,000"),
    ("Stormal: Hurricane", "1/13,500,000"),
    ("Sirius", "1/14,000,000"),
    ("Arcane: Legacy", "1/15,000,000"),
    ("Chromatic", "1/20,000,000"),
    ("Aviator", "1/24,000,000"),
    ("Arcane: Dark", "1/30,000,000"),
    ("Ethereal", "1/35,000,000"),
    ("Overseer", "1/45,000,000"),
    ("Exotic: Apex", "1/49,999,500"),
    ("Matrix", "1/50,000,000"),
    ("Twilight: Iridescent Memory", "1/60,000,000"),
    ("Sailor: Flying Dutchman", "1/80,000,000"),
    ("Chromatic: Genesis", "1/99,999,999"),
    ("Spectraflow", "1/100,000,000"),
    ("Starscourge: Radiant", "1/100,000,000"),
    ("Overture", "1/150,000,000"),
    ("Symphony", "1/175,000,000"),
    ("Felled", "1/180,000,000"),
    ("Twilight: Withering Grace", "1/180,000,000"),
    ("Impeached", "1/200,000,000"),
    ("Lumenpool", "1/220,000,000"),
    ("Oppression", "1/220,000,000"),
    ("Hyper-Volt: Ever-Storm", "1/225,000,000"),
    ("Shard Surfer", "1/225,000,000"),
    ("Archangel", "1/250,000,000"),
    ("Astral: Zodiac", "1/267,200,000"),
    ("Prophecy", "1/275,649,430"),
    ("Exotic: Void", "1/299,999,999"),
    ("Bloodlust", "1/300,000,000"),
    ("Overture: History", "1/300,000,000"),
    ("Maelstrom", "1/309,999,999"),
    ("Perpetual", "1/315,000,000"),
    ("Orchestra", "1/336,870,912"),
    ("Atlas", "1/360,000,000"),
    ("Flora: Evergreen", "1/370,073,730"),
    ("Chillsear", "1/375,000,000"),
    ("Abyssal Hunter", "1/400,000,000"),
    ("Gargantua", "1/430,000,000"),
    ("Apostolos", "1/444,000,000"),
    ("Unknown", "1/444,444,444"),
    ("Kyawthuite: Remembrance", "1/450,000,000"),
    ("Ruins", "1/500,000,000"),
    ("Matrix: Overdrive", "1/503,000,000"),
    ("Elude", "1/555,555,555"),
    ("Sophyra", "1/570,000,000"),
    ("Matrix: Reality", "1/601,020,102"),
    ("Prologue", "1/666,616,111"),
    ("Pythios", "1/666,666,666"),
    ("Aegis", "1/825,000,000"),
    ("dreamscape", "1/850,000,000"),
    ("Ruins: Withered", "1/800,000,000"),
    ("Ascendant", "1/935,000,000"),
    ("Nyctophobia", "1/1,011,111,010"),
    ("Pixelation", "1/1,073,741,824"),
    ("Luminosity", "1/1,200,000,000"),
    ("Leviathan", "1/1,730,400,000"),
    ("Breakthrough", "1/1,999,999,999"),
    ("Equinox", "1/2,500,000,000"),
    ("Monarch", "1/3,000,000,000"),
    ("Sovereign", "1/750,000,000"),
]

# ── Leaderboard ───────────────────────────────────────────────────────────
# Uses JSONBin.io public bin — free shared leaderboard for all users
LB_BIN_ID  = "69bc2143aa77b81da9fcb1a9"
LB_API_KEY = "$2a$10$4/dlQeOTb63xwjnB01i.ye.PCRxsC0Zvbm6FXwYu/s57hGrt4qjl."
LB_URL     = f"https://api.jsonbin.io/v3/b/{LB_BIN_ID}"
LB_HEADERS_READ  = {"X-Master-Key": LB_API_KEY}
LB_HEADERS_WRITE = {"X-Master-Key": LB_API_KEY, "Content-Type": "application/json"}

def lb_fetch():
    """Fetch leaderboard dict {username: seconds} from JSONBin."""
    try:
        r = requests.get(LB_URL + "/latest", headers=LB_HEADERS_READ, timeout=8)
        print(f"[LB] fetch status={r.status_code} body={r.text[:200]}")
        record = r.json().get("record", {})
        return record.get("players", {})
    except Exception as e:
        print(f"[LB] fetch error: {e}")
    return {}

def lb_update(username, seconds_to_add):
    """Add seconds to username's total on the shared leaderboard."""
    if not username or seconds_to_add < 1:
        print(f"[LB] skipped: username={username!r} seconds={seconds_to_add}")
        return
    try:
        players = lb_fetch()
        players[username] = players.get(username, 0) + int(seconds_to_add)
        resp = requests.put(LB_URL, json={"players": players}, headers=LB_HEADERS_WRITE, timeout=8)
        print(f"[LB] updated {username} += {int(seconds_to_add)}s  total={players[username]}s  status={resp.status_code} body={resp.text[:100]}")
    except Exception as e:
        print(f"[LB] update error: {e}")

def fmt_time(seconds):
    """Format seconds into readable string."""
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    if h: return f"{h}h {m}m"
    if m: return f"{m}m {s}s"
    return f"{s}s"

class MultiFMacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"MultiFMacro  {VERSION}")
        self.root.resizable(False, False)
        self.root.configure(bg=BORDER_OUTER)
        _set_window_icon(self.root)
        try:
            self._icon32  = _get_photo(_ICON_32_B64,  self.root)
            self._icon64  = _get_photo(_ICON_64_B64,  self.root)
            self._icon128 = _get_photo(_ICON_128_B64, self.root)
            self.root.iconphoto(True, self._icon64)
        except Exception:
            self._icon32 = self._icon64 = self._icon128 = None
        self.cfg = load_config()

        self.started = False; self.paused = False
        self.start_ts = 0.0
        self._session_start = 0.0
        self._session_accum = 0.0
        self._last_lb_upload = 0.0
        self._timer_job = None
        self.last_biome = ""; self.last_aura = ""
        self.last_merchant_ts = 0.0
        # Load persistent biome counts from config
        self.biome_counts = {}
        if self.cfg.has_section("BiomeCounts"):
            for k, v in self.cfg.items("BiomeCounts"):
                try: self.biome_counts[k.upper().replace("_"," ")] = int(v)
                except: pass
        self._poll_job = None
        self._ak_job = None
        self._fish_running = False
        self._fish_proc = None

        self._build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Root layout ───────────────────────────────────────────────────────
    def _build_gui(self):
        W, H = 940, 520

        # Get real screen dimensions BEFORE overrideredirect (still has WM context)
        self.root.withdraw()          # hide briefly so no flash
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        # Fallback via screeninfo/ctypes helper if Tk returns junk
        if sw < 100 or sh < 100:
            sw, sh = get_screen_size()

        x = max(0, (sw - W) // 2)
        y = max(0, (sh - H) // 2)

        self.root.geometry(f"{W}x{H}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.configure(bg=BG0)
        self.root.minsize(W, H)
        self.root.deiconify()         # show now with correct size+pos
        self.root.update()

        # ── Titlebar ──────────────────────────────────────────────────────
        TB = BG0
        titlebar = tk.Frame(self.root, bg=TB, height=38)
        titlebar.pack(fill="x"); titlebar.pack_propagate(False)

        def _ds(e): titlebar._x=e.x; titlebar._y=e.y
        def _dm(e): self.root.geometry(f"+{self.root.winfo_x()+e.x-titlebar._x}+{self.root.winfo_y()+e.y-titlebar._y}")
        titlebar.bind("<ButtonPress-1>",_ds); titlebar.bind("<B1-Motion>",_dm)

        # Right side: window controls
        tk.Button(titlebar, text="×", command=self._on_close,
                  bg=TB, fg=TXT3, font=("Segoe UI",13), relief="flat", bd=0, padx=14, pady=0,
                  cursor="hand2", activebackground="#2a0a0a", activeforeground="#e05555").pack(side="right", fill="y")
        tk.Button(titlebar, text="–",
                  command=lambda: getattr(self, "_minimize_fn", self.root.withdraw)(),
                  bg=TB, fg=TXT3, font=("Segoe UI",12), relief="flat", bd=0, padx=12, pady=0,
                  cursor="hand2", activebackground=BG2, activeforeground=TXT).pack(side="right", fill="y")

        # Right side: status + timer
        tk.Frame(titlebar, bg=BDR, width=1).pack(side="right", fill="y", pady=8)
        self.status_var = tk.StringVar(value="● idle")
        tk.Label(titlebar, textvariable=self.status_var, bg=TB, fg=TXT3,
                 font=("Segoe UI",8)).pack(side="right", padx=(0,12))
        self.timer_var = tk.StringVar(value="00:00:00")
        tk.Label(titlebar, textvariable=self.timer_var, bg=TB, fg=ACC2,
                 font=FONT_MONO).pack(side="right", padx=(0,2))
        tk.Label(titlebar, text="session", bg=TB, fg=TXT3, font=("Segoe UI",7)).pack(side="right", padx=(0,4))
        tk.Frame(titlebar, bg=BDR, width=1).pack(side="right", fill="y", pady=8)

        # Left side: icon + app name
        if self._icon32:
            il = tk.Label(titlebar, image=self._icon32, bg=TB)
            il.pack(side="left", padx=(12,6))
            il.bind("<ButtonPress-1>",_ds); il.bind("<B1-Motion>",_dm)
        tl = tk.Label(titlebar, text="MultiFMacro", bg=TB, fg=TXT,
                      font=("Segoe UI",9,"bold"))
        tl.pack(side="left"); tl.bind("<ButtonPress-1>",_ds); tl.bind("<B1-Motion>",_dm)
        vl = tk.Label(titlebar, text=f"  {VERSION}", bg=TB, fg=TXT3, font=("Segoe UI",8))
        vl.pack(side="left"); vl.bind("<ButtonPress-1>",_ds); vl.bind("<B1-Motion>",_dm)

        # Center: player info
        self._player_frame = tk.Frame(titlebar, bg=TB)
        self._player_frame.pack(side="left", expand=True, anchor="center", padx=(20,0))
        self._player_frame.bind("<ButtonPress-1>",_ds); self._player_frame.bind("<B1-Motion>",_dm)
        self._avatar_label = tk.Label(self._player_frame, bg=TB)
        self._avatar_label.pack(side="left", padx=(0,6))
        self._avatar_label.bind("<ButtonPress-1>",_ds); self._avatar_label.bind("<B1-Motion>",_dm)
        pf = tk.Frame(self._player_frame, bg=TB); pf.pack(side="left", anchor="center")
        pf.bind("<ButtonPress-1>",_ds); pf.bind("<B1-Motion>",_dm)
        self._player_status_var = tk.StringVar(value="")
        self._player_name_var   = tk.StringVar(value="")
        sl = tk.Label(pf, textvariable=self._player_status_var, bg=TB, fg=GREEN,
                      font=("Segoe UI",7)); sl.pack(anchor="w")
        sl.bind("<ButtonPress-1>",_ds); sl.bind("<B1-Motion>",_dm)
        nl = tk.Label(pf, textvariable=self._player_name_var, bg=TB, fg=TXT,
                      font=("Segoe UI",8,"bold")); nl.pack(anchor="w")
        nl.bind("<ButtonPress-1>",_ds); nl.bind("<B1-Motion>",_dm)
        for w in [titlebar] + list(titlebar.winfo_children()):
            try: w.bind("<ButtonPress-1>",_ds); w.bind("<B1-Motion>",_dm)
            except: pass
        threading.Thread(target=self._load_player_info, daemon=True).start()

        # Separator under titlebar
        tk.Frame(self.root, bg=BDR, height=1).pack(fill="x")

        # ── Body ─────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=BG0); body.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────────────────────────────────
        self.nav = tk.Frame(body, bg=BG0, width=120)
        self.nav.pack(side="left", fill="y"); self.nav.pack_propagate(False)
        tk.Frame(body, bg=BDR, width=1).pack(side="left", fill="y")

        # Content area
        self.content_area = tk.Frame(body, bg=BG1)
        self.content_area.pack(side="left", fill="both", expand=True)
        self.content_area.pack_propagate(False)

        # ── Nav tabs ─────────────────────────────────────────────────────
        self._tab_frames = {}; self._tab_btns = {}
        TABS = ["WEBHOOK","AURA","MERCHANT","ANTIKICK","FISHING","STATS","LEADERBOARD","CREDITS"]
        tk.Frame(self.nav, bg=BG0, height=14).pack()
        for name in TABS:
            f = tk.Frame(self.nav, bg=BG0, cursor="hand2")
            f.pack(fill="x")
            bar = tk.Frame(f, bg=BG0, width=2); bar.pack(side="left", fill="y")
            b = tk.Label(f, text=name, bg=BG0, fg=TXT3,
                         font=("Segoe UI",8), anchor="w", padx=12, pady=7, cursor="hand2")
            b.pack(fill="x", side="left", expand=True)
            b.bind("<Button-1>", lambda e,n=name: self._show_tab(n))
            f.bind("<Button-1>", lambda e,n=name: self._show_tab(n))
            bar.bind("<Button-1>", lambda e,n=name: self._show_tab(n))
            self._tab_btns[name] = (f, b, bar)

        # ── Sidebar controls ──────────────────────────────────────────────
        tk.Frame(self.nav, bg=BG0, height=8).pack()
        tk.Frame(self.nav, bg=BDR, height=1).pack(fill="x", padx=12)
        tk.Frame(self.nav, bg=BG0, height=8).pack()

        ctrl = tk.Frame(self.nav, bg=BG0); ctrl.pack(fill="x", padx=8)
        def nb(t, c, col=ACC, fg=TXT):
            b = tk.Button(ctrl, text=t, command=c, bg=col, fg=fg,
                          font=("Segoe UI",8,"bold"), relief="flat", bd=0,
                          pady=7, cursor="hand2", activebackground=BG3, activeforeground=TXT)
            b.pack(fill="x", pady=2); return b
        self._start_btn = nb("START",  self._start, ACC)
        self._pause_btn = nb("PAUSE",  self._pause, BG2, TXT2)
        nb("STOP", self._stop, BG2, "#cc4444")

        tk.Frame(self.nav, bg=BG0, height=6).pack()
        tk.Frame(self.nav, bg=BDR, height=1).pack(fill="x", padx=12)
        tk.Frame(self.nav, bg=BG0, height=6).pack()

        util = tk.Frame(self.nav, bg=BG0); util.pack(fill="x", padx=8)
        for txt, cmd in [("Test Webhook", self._test_hook), ("Save Config", self._save_config)]:
            tk.Button(util, text=txt, command=cmd, bg=BG0, fg=TXT3,
                      font=("Segoe UI",7), relief="flat", bd=0, pady=5,
                      cursor="hand2", activebackground=BG2, activeforeground=TXT).pack(fill="x", pady=1)

        tk.Frame(self.nav, bg=BG0, height=8).pack()
        tk.Frame(self.nav, bg=BDR, height=1).pack(fill="x", padx=12)
        tk.Frame(self.nav, bg=BG0, height=8).pack()
        self.biome_var = tk.StringVar(value="NORMAL")
        tk.Label(self.nav, text="BIOME", bg=BG0, fg=TXT3,
                 font=("Segoe UI",6,"bold")).pack()
        tk.Label(self.nav, textvariable=self.biome_var, bg=BG0, fg=ACC2,
                 font=("Segoe UI",8,"bold"), wraplength=110).pack(pady=(3,6))

        self._build_webhook_tab()
        self._build_aura_tab()
        self._build_merchant_tab()
        self._build_antikick_tab()
        self._build_fishing_tab()
        self._build_stats_tab()
        self._build_leaderboard_tab()
        self._build_credits_tab()

        self._show_tab("WEBHOOK")
        self.root.update_idletasks()

    def _show_tab(self, name):
        for n,(f,b,bar) in self._tab_btns.items():
            active = n == name
            f.configure(bg=BG1 if active else BG0)
            b.configure(bg=BG1 if active else BG0,
                        fg=TXT if active else TXT3,
                        font=("Segoe UI",8,"bold") if active else ("Segoe UI",8))
            bar.configure(bg=ACC if active else BG0)
        for frm in self._tab_frames.values(): frm.place_forget()
        target = self._tab_frames[name]
        target.place(x=0, y=0, relwidth=1, relheight=1)
        self._fade_in(target)

    def _fade_in(self, frame, step=0):
        """Slide-in from slight offset + fade via bg blend steps."""
        steps = 6
        offsets = [18, 13, 9, 5, 2, 0]
        if step < len(offsets):
            x = offsets[step]
            frame.place(x=x, y=0, relwidth=1, relheight=1)
            self.root.after(16, lambda: self._fade_in(frame, step+1))
        else:
            frame.place(x=0, y=0, relwidth=1, relheight=1)

    def _reg(self, name, frame): self._tab_frames[name] = frame

    # ── WEBHOOK ───────────────────────────────────────────────────────────
    def _build_webhook_tab(self):
        outer = tk.Frame(self.content_area, bg=BG1); self._reg("WEBHOOK", outer)
        outer.columnconfigure(0, weight=1); outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)

        # ── Left pane ─────────────────────────────────────────────────────
        left = tk.Frame(outer, bg=BG1, padx=18, pady=16)
        left.grid(row=0, column=0, sticky="nsew")

        page_header(left, "Webhook Config")

        c = card(left); c.pack(fill="x")
        sec(c, "CONNECTION", 0, 2); div(c, 1, 2)

        self.wh_url  = tk.StringVar(value=self.cfg.get("Webhook","webhook_url",    fallback=""))
        self.ps_url  = tk.StringVar(value=self.cfg.get("Webhook","private_server", fallback=""))
        self.disc_id = tk.StringVar(value=self.cfg.get("Webhook","discord_user_id",fallback=""))
        self.roblox_username = tk.StringVar(value=self.cfg.get("Player","roblox_username",fallback=""))

        fields = [
            ("Webhook URL",    self.wh_url),
            ("Private Server", self.ps_url),
            ("Discord ID",     self.disc_id),
            ("Roblox User",    self.roblox_username),
        ]
        for r, (lb, var) in enumerate(fields):
            tk.Label(c, text=lb, bg=BG2, fg=TXT2, font=FONT_LABEL, anchor="w").grid(
                row=r+2, column=0, sticky="w", padx=(12,6), pady=5)
            entry(c, var, width=32).grid(
                row=r+2, column=1, sticky="ew", padx=(0,12), pady=5)
        c.columnconfigure(1, weight=1)

        apply_status = tk.StringVar(value="")
        bf = tk.Frame(c, bg=BG2); bf.grid(row=6, column=0, columnspan=2, sticky="w", padx=12, pady=(4,10))
        def _apply_username():
            uname = self.roblox_username.get().strip()
            if not uname: apply_status.set("Enter a username first."); return
            apply_status.set("validating...")
            def do():
                try:
                    r = requests.post("https://users.roblox.com/v1/usernames/users",
                        json={"usernames":[uname],"excludeBannedUsers":False}, timeout=8)
                    data = r.json().get("data",[])
                    if not data:
                        self.root.after(0, lambda: apply_status.set("not found"))
                        self.root.after(0, lambda: self.roblox_username.set("")); return
                    vname = data[0].get("name", uname)
                    uid   = str(data[0].get("id",""))
                    self.root.after(0, lambda: self.roblox_username.set(vname))
                    self.root.after(0, lambda: self._player_name_var.set(vname))
                    self.root.after(0, lambda: self._player_status_var.set("● active"))
                    self.root.after(0, lambda: apply_status.set(f"✓ {vname}"))
                    self._save_config()
                    if uid:
                        try:
                            from PIL import ImageTk
                            img = fetch_avatar_image(uid, size=28)
                            if img:
                                photo = ImageTk.PhotoImage(img)
                                self._avatar_photo = photo
                                self.root.after(0, lambda p=photo: self._avatar_label.configure(image=p))
                        except: pass
                except Exception as e:
                    self.root.after(0, lambda: apply_status.set(f"error: {e}"))
            threading.Thread(target=do, daemon=True).start()
        btn(bf, "Apply Username", _apply_username, ACC).pack(side="left")
        tk.Label(bf, textvariable=apply_status, bg=BG2, fg=GREEN, font=FONT_LABEL).pack(side="left", padx=(10,0))

        # ── Right pane: Biome Ping ─────────────────────────────────────────
        tk.Frame(outer, bg=BDR, width=1).grid(row=0, column=0, sticky="nse", padx=(0,0), pady=16)
        right = tk.Frame(outer, bg=BG1, padx=18, pady=16)
        right.grid(row=0, column=1, sticky="nsew")

        page_header(right, "Biome Ping", "ping you when a biome starts")

        ao = tk.Frame(right, bg=BG1); ao.pack(anchor="w", pady=(0,6))
        tk.Label(ao, text="@everyone — always on:", bg=BG1, fg=TXT2, font=FONT_LABEL).pack(side="left")
        for b in sorted(CYBERSPACE_ALWAYS_ON):
            color = "#%06x" % BIOME_COLORS.get(b, 0x8888aa)
            tk.Label(ao, text=f"  ● {b.title()}", bg=BG1, fg=color,
                     font=("Segoe UI",8,"bold")).pack(side="left")
        tk.Frame(right, bg=BDR, height=1).pack(fill="x", pady=(0,8))

        self._ping_biome_vars = {}
        PINGABLE = sorted(b for b in BIOME_COLORS if b not in CYBERSPACE_ALWAYS_ON)
        grid = tk.Frame(right, bg=BG1); grid.pack(anchor="w", fill="x")
        for i, biome in enumerate(PINGABLE):
            saved = self.cfg.getboolean("BiomePing", _cfg_key(biome), fallback=False)
            var = tk.BooleanVar(value=saved)
            self._ping_biome_vars[biome] = var
            bcolor = "#%06x" % BIOME_COLORS.get(biome, 0x8888aa)
            row_f = tk.Frame(grid, bg=BG1)
            row_f.grid(row=i//2, column=i%2, sticky="w", padx=(0,20), pady=2)
            tk.Label(row_f, text="●", bg=BG1, fg=bcolor, font=FONT_LABEL).pack(side="left")
            tk.Checkbutton(row_f, text=f" {biome.title()}", variable=var,
                           bg=BG1, fg=TXT2, selectcolor=BG3,
                           activebackground=BG1, activeforeground=TXT,
                           font=FONT_LABEL, cursor="hand2").pack(side="left")

        self.root.after(100, self._refresh_biome_stats)

    # ── Biome stats helpers ───────────────────────────────────────────
    def _refresh_biome_stats(self):
        for w in self._stats_frame.winfo_children():
            w.destroy()
        bg = self._stats_frame.cget("bg")
        if not self.biome_counts:
            tk.Label(self._stats_frame, text="No biomes detected yet.",
                     bg=bg, fg=TXT3, font=FONT_LABEL).pack(anchor="w")
            return
        sorted_biomes = sorted(self.biome_counts.items(), key=lambda x: -x[1])
        cols = 4
        for i, (biome, count) in enumerate(sorted_biomes):
            color = "#%06x" % BIOME_COLORS.get(biome, 0x8888aa)
            chip = tk.Frame(self._stats_frame, bg=BG2,
                            highlightthickness=1, highlightbackground=BDR)
            chip.grid(row=i//cols, column=i%cols, sticky="w", padx=(0,8), pady=4, ipadx=8, ipady=5)
            tk.Label(chip, text="●", bg=BG2, fg=color, font=FONT_LABEL).pack(side="left", padx=(6,2))
            tk.Label(chip, text=biome.title(), bg=BG2, fg=TXT2, font=FONT_LABEL).pack(side="left")
            tk.Label(chip, text=f"  {count}", bg=BG2, fg=GOLD,
                     font=("Segoe UI",9,"bold")).pack(side="left", padx=(2,0))

    def _get_ping_biomes(self):
        if not hasattr(self, "_ping_biome_vars"): return set()
        return {b for b,v in self._ping_biome_vars.items() if v.get()}

    def _reset_biome_stats(self):
        self.biome_counts.clear()
        self._refresh_biome_stats()

    # ── AURA ──────────────────────────────────────────────────────────────
    def _build_aura_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("AURA", root)
        root.configure(padx=18, pady=16)

        page_header(root, "Aura Detection", "notifies you when rare auras are rolled")

        c = card(root); c.pack(fill="x", pady=(0,10))
        sec(c, "SETTINGS", 0, 3); div(c, 1, 3)
        self.aura_enabled = tk.BooleanVar(value=self.cfg.getboolean("Aura","enabled",     fallback=True))
        self.aura_ping    = tk.BooleanVar(value=self.cfg.getboolean("Aura","ping_on_aura",fallback=True))
        check(c,"  Enable aura detection",        self.aura_enabled).grid(row=2,column=0,columnspan=3,sticky="w",padx=12,pady=(6,2))
        check(c,"  Ping Discord ID on detection", self.aura_ping).grid(   row=3,column=0,columnspan=3,sticky="w",padx=12,pady=(0,4))
        div(c,4,3)
        self.aura_status_var = tk.StringVar(value="No aura detected yet")
        tk.Label(c,text="Last detected:",bg=BG2,fg=TXT3,font=FONT_LABEL).grid(row=5,column=0,sticky="w",padx=(12,4),pady=(6,8))
        tk.Label(c,textvariable=self.aura_status_var,bg=BG2,fg=GOLD,
                 font=("Segoe UI",9,"bold")).grid(row=5,column=1,sticky="w",pady=(6,8))

        ctrl = tk.Frame(root,bg=BG1); ctrl.pack(fill="x",pady=(0,6))
        tk.Label(ctrl,text="Aura Filter",bg=BG1,fg=TXT,
                 font=("Segoe UI",9,"bold")).pack(side="left")
        tk.Label(ctrl,text="  checked = notify",bg=BG1,fg=TXT3,font=FONT_LABEL).pack(side="left")
        tk.Button(ctrl,text="All On", command=lambda:self._aura_select_all(True),
                  bg=BG3,fg=TXT,font=FONT_LABEL,relief="flat",bd=0,padx=10,pady=4,cursor="hand2").pack(side="right",padx=(4,0))
        tk.Button(ctrl,text="All Off",command=lambda:self._aura_select_all(False),
                  bg=BG3,fg=TXT,font=FONT_LABEL,relief="flat",bd=0,padx=10,pady=4,cursor="hand2").pack(side="right",padx=(4,0))
        self.aura_search_var = tk.StringVar()
        self.aura_search_var.trace_add("write",lambda *_:self._aura_filter_list())
        se = tk.Entry(ctrl,textvariable=self.aura_search_var,bg=BG3,fg=TXT,
                      insertbackground=ACC2,font=FONT_LABEL,relief="flat",
                      highlightthickness=1,highlightbackground=BDR,
                      highlightcolor=ACC,bd=0,width=18)
        se.pack(side="right",padx=(4,10))
        tk.Label(ctrl,text="Search:",bg=BG1,fg=TXT3,font=FONT_LABEL).pack(side="right")

        lf = tk.Frame(root,bg=BG1); lf.pack(fill="both",expand=True)
        self._aura_canvas = tk.Canvas(lf,bg=BG2,bd=0,highlightthickness=0)
        sb = tk.Scrollbar(lf,orient="vertical",command=self._aura_canvas.yview,
                          bg=BG2, troughcolor=BG2, width=8)
        self._aura_inner = tk.Frame(self._aura_canvas,bg=BG2)
        self._aura_inner.bind("<Configure>",
            lambda e:self._aura_canvas.configure(scrollregion=self._aura_canvas.bbox("all")))
        self._aura_canvas.create_window((0,0),window=self._aura_inner,anchor="nw")
        self._aura_canvas.configure(yscrollcommand=sb.set)
        self._aura_canvas.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        self._aura_canvas.bind("<MouseWheel>",
            lambda e:self._aura_canvas.yview_scroll(-1*(e.delta//120),"units"))

        # init vars from config
        self._aura_vars = {}
        if not self.cfg.has_section("AuraFilter"):
            self.cfg["AuraFilter"] = {}
        for name,rarity in AURA_LIST:
            key = _cfg_key(name)
            saved = self.cfg.get("AuraFilter",key,fallback="1")
            self._aura_vars[name] = (tk.BooleanVar(value=saved=="1"), rarity)

        self._aura_build_rows()

    def _aura_build_rows(self):
        for w in self._aura_inner.winfo_children():
            w.destroy()
        search = self.aura_search_var.get().lower()
        for name,rarity in AURA_LIST:
            if search and search not in name.lower():
                continue
            var,_ = self._aura_vars[name]
            row = tk.Frame(self._aura_inner,bg=BG2); row.pack(fill="x")
            tk.Checkbutton(row,variable=var,bg=BG2,fg=TXT,selectcolor=BG3,
                           activebackground=BG2,activeforeground=TXT,
                           cursor="hand2",command=self._save_config).pack(side="left",padx=(10,4),pady=3)
            tk.Label(row,text=name,bg=BG2,fg=TXT,font=FONT_LABEL,
                     anchor="w",width=28).pack(side="left")
            tk.Label(row,text=rarity,bg=BG2,fg=TXT3,font=FONT_LABEL,
                     anchor="w").pack(side="left",padx=(4,10))
            tk.Frame(self._aura_inner,bg=BDR,height=1).pack(fill="x",padx=10)

    def _aura_filter_list(self):
        self._aura_build_rows()

    def _aura_select_all(self,state):
        search = self.aura_search_var.get().lower()
        for name,_ in AURA_LIST:
            if search and search not in name.lower():
                continue
            self._aura_vars[name][0].set(state)
        self._save_config()

    # ── MERCHANT ──────────────────────────────────────────────────────────
    def _build_merchant_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("MERCHANT", root)
        root.configure(padx=18, pady=16)

        page_header(root, "Merchant Detection", "detects Mari and Jester spawns via log")

        # Warning box
        wf = tk.Frame(root, bg="#141200", highlightthickness=1, highlightbackground="#3a2e00")
        wf.pack(fill="x", pady=(0,12))
        tk.Label(wf, text="SETUP REQUIRED",
                 bg="#141200", fg=GOLD, font=("Segoe UI",8,"bold")).pack(anchor="w", padx=12, pady=(8,2))
        msg = (
            "Merchant detection requires a Roblox FastFlag via Bloxstrap:\n"
            "1. Install Bloxstrap  →  Fast Flags  →  Add flag:\n"
            "       Name: FStringDebugLuaLogPattern   Value: ExpChat/mountClientApp\n"
            "2. Save and launch Roblox through Bloxstrap. Detection works automatically."
        )
        tk.Label(wf, text=msg, bg="#141200", fg="#aa9030", font=FONT_LABEL,
                 justify="left", wraplength=800).pack(anchor="w", padx=16, pady=(0,10))

        c = card(root); c.pack(fill="x")
        sec(c,"SETTINGS", 0, 2); div(c, 1, 2)
        self.merch_log         = tk.BooleanVar(value=self.cfg.getboolean("Merchant","log_detection",fallback=True))
        self.merch_ping_mari   = tk.BooleanVar(value=self.cfg.getboolean("Merchant","ping_mari",    fallback=False))
        self.merch_ping_jester = tk.BooleanVar(value=self.cfg.getboolean("Merchant","ping_jester",  fallback=False))
        check(c,"  Enable merchant detection",          self.merch_log).grid(        row=2,column=0,columnspan=2,sticky="w",padx=12,pady=(6,2))
        check(c,"  Ping Discord ID when Mari spawns",   self.merch_ping_mari).grid(  row=3,column=0,columnspan=2,sticky="w",padx=12,pady=2)
        check(c,"  Ping Discord ID when Jester spawns", self.merch_ping_jester).grid(row=4,column=0,columnspan=2,sticky="w",padx=12,pady=(2,4))
        self.merch_status_var = tk.StringVar(value="No merchant detected yet")
        div(c,5,2)
        tk.Label(c, textvariable=self.merch_status_var, bg=BG2, fg=GOLD,
                 font=FONT_LABEL).grid(row=6,column=0,columnspan=2,sticky="w",padx=14,pady=(6,10))

    # ── ANTIKICK ──────────────────────────────────────────────────────────
    def _build_antikick_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("ANTIKICK", root)
        root.configure(padx=18, pady=16)

        page_header(root, "Anti-Kick", "prevents idle disconnect by pressing Space periodically")

        c = card(root); c.pack(fill="x", pady=(0,10))
        sec(c,"SETTINGS", 0, 2); div(c, 1, 2)
        self.ak_enabled  = tk.BooleanVar(value=self.cfg.getboolean("AntiKick","enabled",     fallback=True))
        self.ak_interval = tk.StringVar(value=self.cfg.get("AntiKick","interval_sec", fallback="600"))
        check(c,"  Press Space periodically to prevent idle disconnect",
              self.ak_enabled).grid(row=2,column=0,columnspan=2,sticky="w",padx=12,pady=(6,4))
        tk.Label(c, text="Interval (seconds)", bg=BG2, fg=TXT2, font=FONT_LABEL, anchor="w").grid(
            row=3,column=0,sticky="w",padx=(12,6),pady=4)
        entry(c,self.ak_interval,width=10).grid(row=3,column=1,sticky="w",padx=(0,12),pady=4)
        div(c,4,2)
        self.ak_status_var = tk.StringVar(value="Idle")
        tk.Label(c,textvariable=self.ak_status_var,bg=BG2,fg=GREEN,font=FONT_LABEL).grid(
            row=5,column=0,columnspan=2,sticky="w",padx=14,pady=(6,10))

        note_box(root,"Anti-kick fires automatically while the macro is running. It will not press Space immediately on start — it waits the full interval first.")




    # ── FISHING ───────────────────────────────────────────────────────────
    def _build_fishing_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("FISHING", root)
        root.configure(padx=18, pady=16)

        page_header(root, "Fishing — FishScope", "launch FishScope as a companion window")

        c = card(root); c.pack(fill="x", pady=(0,10))
        sec(c, "LAUNCHER", 0, 2); div(c, 1, 2)
        tk.Label(c, text=(
            "Place the FishScope folder next to this file, then click Launch.\n"
            "FishScope opens in its own window — use F1/F2 inside it."
        ), bg=BG2, fg=TXT2, font=FONT_LABEL, justify="left").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=14, pady=(8,4))

        fr = tk.Frame(c, bg=BG2); fr.grid(row=3, column=0, columnspan=2, sticky="ew", padx=14, pady=(2,6))
        tk.Label(fr, text="Folder:", bg=BG2, fg=TXT3, font=FONT_LABEL).pack(side="left")
        self.fish_folder_var = tk.StringVar(value="Not detected — place 'fishscope' folder here")
        self._fish_folder_lbl = tk.Label(fr, textvariable=self.fish_folder_var,
                                          bg=BG2, fg=TXT3, font=FONT_LABEL, wraplength=640)
        self._fish_folder_lbl.pack(side="left", padx=(6,0))

        div(c, 4, 2)
        bf = tk.Frame(c, bg=BG2); bf.grid(row=5, column=0, columnspan=2, sticky="w", padx=14, pady=(10,8))
        self._fish_launch_btn = btn(bf, "Launch FishScope", self._fish_install_launch, GREEN)
        self._fish_launch_btn.pack(side="left", padx=(0,8))
        btn(bf, "Stop", self._fish_kill, "#3d1010").pack(side="left", padx=(0,8))
        btn(bf, "Detect Folder", self._fish_detect_folder, BG3).pack(side="left")

        self.fish_status_var = tk.StringVar(value="● Idle")
        self._fish_status_lbl = tk.Label(c, textvariable=self.fish_status_var,
                                          bg=BG2, fg=TXT3, font=FONT_LABEL, wraplength=700)
        self._fish_status_lbl.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(0,10))
        c.columnconfigure(1, weight=1)

        sc = card(root); sc.pack(fill="x")
        sec(sc, "SETUP INSTRUCTIONS", 0, 1); div(sc, 1, 1)
        for i, step in enumerate([
            "1. Extract the FishScope zip you downloaded.",
            "2. Rename the extracted folder to:  fishscope",
            "3. Place it in the same folder as BiomeMacro.py (or .exe).",
            "4. Click Launch FishScope — deps install automatically on first run.",
            "5. FishScope opens in its own window. Use F1/F2 inside it.",
        ]):
            tk.Label(sc, text=step, bg=BG2, fg=TXT2, font=FONT_LABEL, anchor="w").grid(
                row=i+2, column=0, sticky="w", padx=14, pady=3)
        tk.Frame(sc, bg=BG2, height=8).grid(row=8, column=0)

        self._fish_detect_folder(silent=True)

    def _fish_st(self, msg, color=None):
        """Thread-safe status + colour update."""
        def _apply():
            self.fish_status_var.set(msg)
            if hasattr(self, "_fish_status_lbl"):
                if color:
                    self._fish_status_lbl.configure(fg=color)
                elif "Error" in msg or "failed" in msg.lower():
                    self._fish_status_lbl.configure(fg=ACC3)
                elif "Running" in msg or "✓" in msg or "installed" in msg.lower():
                    self._fish_status_lbl.configure(fg=GREEN)
                elif "Stopped" in msg:
                    self._fish_status_lbl.configure(fg=TXT3)
                else:
                    self._fish_status_lbl.configure(fg=TXT2)
        self.root.after(0, _apply)

    def _fish_find_folder(self):
        """Return (folder_path, main_py) or (None, None). Searches for any FishScope folder."""
        search_dirs = [BASE_DIR, os.getcwd()]
        # Exact name first, then any folder containing main.py with fishscope in name
        exact_names = ["fishscope", "FishScope"]
        for base in search_dirs:
            for name in exact_names:
                p = os.path.join(base, name)
                if os.path.isdir(p) and os.path.exists(os.path.join(p, "main.py")):
                    return p, os.path.join(p, "main.py")
        # Fuzzy: any sub-folder whose name contains 'fishscope' (case-insensitive)
        for base in search_dirs:
            try:
                for entry in os.listdir(base):
                    if "fishscope" in entry.lower():
                        p = os.path.join(base, entry)
                        main_py = os.path.join(p, "main.py")
                        if os.path.isdir(p) and os.path.exists(main_py):
                            return p, main_py
            except Exception:
                pass
        return None, None

    def _fish_find_python(self):
        """
        Find the actual python.exe to use — never the Windows Store stub or py.EXE proxy.
        We resolve py.EXE → real python.exe so pip install and launch use IDENTICAL Python.
        """
        import subprocess as sp, shutil, glob

        STORE_STUB = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft", "WindowsApps"
        ).lower()

        def is_real_python(path):
            """True only if path is a working python.exe (not Store stub, not py launcher)."""
            if not path or not os.path.isfile(path):
                return False
            p = path.lower()
            if STORE_STUB in p:
                return False
            if os.path.basename(p) in ("py.exe", "py"):
                return False   # don't use the launcher itself
            try:
                r = sp.run([path, "-c", "import sys; print(sys.executable)"],
                           capture_output=True, text=True, timeout=5)
                return r.returncode == 0 and r.stdout.strip() != ""
            except Exception:
                return False

        # 1. If NOT frozen, sys.executable is the real Python already
        if not getattr(sys, 'frozen', False) and is_real_python(sys.executable):
            return sys.executable

        # 2. Ask the py launcher where its Python lives, then use THAT path directly
        py_launcher = shutil.which("py")
        if py_launcher and "windowsapps" not in py_launcher.lower():
            try:
                r = sp.run([py_launcher, "-c", "import sys; print(sys.executable)"],
                           capture_output=True, text=True, timeout=5)
                resolved = r.stdout.strip()
                if resolved and is_real_python(resolved):
                    return resolved
            except Exception:
                pass

        # 3. Search PATH for python3 / python (skip Store stub)
        for name in ("python3", "python"):
            found = shutil.which(name)
            if is_real_python(found):
                return found

        # 4. Scan common Windows install directories for python.exe
        candidates = []
        for base in [
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("APPDATA", ""),
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
            "C:\\", "D:\\", "E:\\",
        ]:
            if not base:
                continue
            for pattern in [
                "Python3*\\python.exe",
                "Python\\python.exe",
                "Programs\\Python\\Python3*\\python.exe",
            ]:
                candidates += glob.glob(os.path.join(base, pattern))

        candidates.sort(reverse=True)
        for path in candidates:
            if is_real_python(path):
                return path

        return None

    def _fish_detect_folder(self, silent=False):
        folder, _ = self._fish_find_folder()
        if folder:
            short = os.path.basename(folder)
            self.fish_folder_var.set(f"✓  Found:  {short}")
            if hasattr(self, "_fish_folder_lbl"):
                self._fish_folder_lbl.configure(fg=GREEN)
        else:
            self.fish_folder_var.set("✗  Not found — rename folder to 'fishscope' and place it here")
            if hasattr(self, "_fish_folder_lbl"):
                self._fish_folder_lbl.configure(fg=ACC3)
            if not silent:
                messagebox.showwarning("Folder Not Found",
                    "Could not find a FishScope folder.\n\n"
                    "Place the FishScope folder next to this file and rename it to:  fishscope")

    def _fish_install_launch(self):
        if hasattr(self, "_fish_proc") and self._fish_proc and self._fish_proc.poll() is None:
            messagebox.showinfo("Already Running", "FishScope is already running.")
            return
        threading.Thread(target=self._fish_install_thread, daemon=True).start()

    def _fish_install_thread(self):
        import subprocess as sp

        # ── Locate fishscope folder ──────────────────────────────────────
        folder, main_py = self._fish_find_folder()
        if not folder:
            self._fish_st("✗  Error: 'fishscope' folder not found. See Setup Instructions.")
            return
        if not main_py or not os.path.exists(main_py):
            self._fish_st("✗  Error: fishscope/main.py not found inside folder.")
            return

        req_txt = os.path.join(folder, "requirements.txt")

        # ── Find Python ──────────────────────────────────────────────────
        python_exe = self._fish_find_python()
        if not python_exe:
            self._fish_st("✗  No real Python found. Install Python from python.org and tick 'Add to PATH'.")
            return
        self._fish_st(f"⏳  Found Python: {python_exe}")

        # ── Install dependencies one by one ─────────────────────────────
        # numpy must come first with a pre-built wheel (no C compiler on user machines)
        # keyboard and pywin32 sometimes need --user flag to install properly
        DEPS_ORDERED = [
            "numpy<2",          # must be first, needs --only-binary
            "PyQt6",
            "Pillow",
            "keyboard",
            "autoit",           # required by pyautogui/pynput on Windows
            "pyautogui",
            "requests",
            "pytesseract",
            "opencv-python<5",
            "pywin32",
            "fuzzywuzzy",
            "python-Levenshtein",
            "screeninfo",
            "pynput",
            "packaging",
        ]
        failed = []
        total = len(DEPS_ORDERED)
        for i, dep in enumerate(DEPS_ORDERED):
            self._fish_st(f"⏳  [{i+1}/{total}] Installing {dep}...")
            try:
                extra = ["--only-binary=:all:"] if dep.startswith("numpy") else []
                r = sp.run(
                    [python_exe, "-m", "pip", "install", dep, "-q"] + extra,
                    capture_output=True, text=True, timeout=120
                )
                if r.returncode != 0:
                    # retry with --user flag
                    r2 = sp.run(
                        [python_exe, "-m", "pip", "install", dep, "-q", "--user"] + extra,
                        capture_output=True, text=True, timeout=120
                    )
                    if r2.returncode != 0:
                        failed.append(dep)
            except Exception as e:
                failed.append(f"{dep}({e})")

        if failed:
            self._fish_st(f"⚠  Some packages failed: {', '.join(failed)}")
        else:
            self._fish_st("✓  All dependencies installed.")

        # ── Verify key imports work ──────────────────────────────────────
        self._fish_st("⏳  Verifying install...")
        check = sp.run([python_exe, "-c", "import autoit, keyboard, PyQt6, cv2, PIL"],
                       capture_output=True, text=True, timeout=15)
        if check.returncode != 0:
            err = check.stderr.strip()
            missing = err.splitlines()[-1] if err.splitlines() else "unknown"
            self._fish_st(f"✗  {missing}")
            self.root.after(0, lambda e=err, p=python_exe: messagebox.showerror(
                "Dependency Error",
                "Could not import required modules after install.\n\n"
                "Error:\n" + e + "\n\n"
                "Python used:\n" + p + "\n\n"
                "Try running this manually as Administrator in cmd:\n" +
                p + " -m pip install autoit keyboard PyQt6 numpy opencv-python "
                    "pillow pyautogui pywin32 fuzzywuzzy screeninfo pynput"
            ))
            return

        # ── Launch FishScope ─────────────────────────────────────────────
        self._fish_st("✓  Launching FishScope...")
        try:
            self._fish_proc = sp.Popen(
                [python_exe, main_py],
                cwd=folder,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
            self._fish_st(f"● Running  (PID {self._fish_proc.pid})")
            threading.Thread(target=self._fish_watch_output,
                             args=(self._fish_proc,), daemon=True).start()
            self.root.after(1000, self._fish_poll)
        except Exception as e:
            self._fish_st(f"✗  Launch failed: {e}")

    def _fish_watch_output(self, proc):
        """Read stderr/stdout from FishScope and surface any crash errors."""
        import subprocess as sp
        try:
            _, stderr = proc.communicate()  # blocks until process exits
            ret = proc.returncode
            if ret != 0:
                err = (stderr or b"").decode("utf-8", errors="ignore").strip()
                # Show last meaningful line of the traceback
                lines = [l for l in err.splitlines() if l.strip()]
                summary = lines[-1] if lines else f"exit code {ret}"
                self._fish_st(f"✗  Crashed: {summary}")
                # Also pop a full error dialog so nothing is hidden
                self.root.after(0, lambda e=err: messagebox.showerror(
                    "FishScope Error",
                    f"FishScope exited with an error:\n\n{e[-1200:] or '(no output)'}"
                ))
        except Exception:
            pass

    def _fish_poll(self):
        if not hasattr(self, "_fish_proc") or self._fish_proc is None:
            return
        ret = self._fish_proc.poll()
        if ret is None:
            self.root.after(2000, self._fish_poll)
        else:
            self._fish_st(f"■  Stopped (exit code {ret})")
            self._fish_proc = None

    def _fish_kill(self):
        if not hasattr(self, "_fish_proc") or self._fish_proc is None:
            self._fish_st("● Idle")
            return
        try:
            self._fish_proc.terminate()
            self._fish_proc = None
            self._fish_st("■  Stopped.")
        except Exception as e:
            messagebox.showerror("Stop Failed", str(e))

    # ── STATS ─────────────────────────────────────────────────────────────
    def _build_stats_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("STATS", root)
        root.configure(padx=18, pady=16)
        hdr = tk.Frame(root, bg=BG1); hdr.pack(fill="x")
        tk.Label(hdr, text="Biome Stats", bg=BG1, fg=TXT,
                 font=("Segoe UI",11,"bold")).pack(side="left")
        tk.Label(hdr, text="  persistent across sessions", bg=BG1, fg=TXT3, font=FONT_LABEL).pack(side="left", pady=2)
        btn(hdr, "Reset", self._reset_biome_stats, BG3).pack(side="right")
        tk.Frame(root, bg=BDR, height=1).pack(fill="x", pady=(6,12))
        self._stats_frame = tk.Frame(root, bg=BG1)
        self._stats_frame.pack(fill="both", expand=True)
        self._stats_empty_lbl = tk.Label(self._stats_frame, text="No biomes detected yet.",
                                          bg=BG1, fg=TXT3, font=FONT_LABEL)
        self._stats_empty_lbl.pack(anchor="w")
        self.root.after(100, self._refresh_biome_stats)

    # ── LEADERBOARD ───────────────────────────────────────────────────────
    def _build_leaderboard_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("LEADERBOARD", root)
        root.configure(padx=18, pady=16)

        page_header(root, "Leaderboard", "grind time — updates when you close the macro")

        hdr = tk.Frame(root, bg=BG2)
        hdr.pack(fill="x")
        for text, width, anchor in [("#", 4, "w"), ("Player", 22, "w"), ("Macro Time", 14, "w")]:
            tk.Label(hdr, text=text, bg=BG2, fg=TXT3, font=FONT_LABEL,
                     width=width, anchor=anchor).pack(side="left", padx=(10,0), pady=6)
        tk.Frame(root, bg=BDR, height=1).pack(fill="x")

        lf = tk.Frame(root, bg=BG1); lf.pack(fill="both", expand=True)
        self._lb_canvas = tk.Canvas(lf, bg=BG1, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(lf, orient="vertical", command=self._lb_canvas.yview,
                          bg=BG1, troughcolor=BG1, width=8)
        self._lb_inner = tk.Frame(self._lb_canvas, bg=BG1)
        self._lb_inner.bind("<Configure>",
            lambda e: self._lb_canvas.configure(scrollregion=self._lb_canvas.bbox("all")))
        self._lb_canvas.create_window((0,0), window=self._lb_inner, anchor="nw")
        self._lb_canvas.configure(yscrollcommand=sb.set)
        self._lb_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._lb_canvas.bind("<MouseWheel>",
            lambda e: self._lb_canvas.yview_scroll(-1*(e.delta//120), "units"))

        bf = tk.Frame(root, bg=BG1); bf.pack(fill="x", pady=(6,0))
        self._lb_status_var = tk.StringVar(value="")
        tk.Label(bf, textvariable=self._lb_status_var, bg=BG1, fg=TXT3, font=FONT_LABEL).pack(side="left")
        btn(bf, "Refresh", self._lb_refresh, BG3).pack(side="right")

        threading.Thread(target=self._lb_load, daemon=True).start()

    def _lb_load(self):
        self.root.after(0, lambda: self._lb_status_var.set("Loading..."))
        data = lb_fetch()
        self.root.after(0, lambda: self._lb_render(data))

    def _lb_refresh(self):
        threading.Thread(target=self._lb_load, daemon=True).start()

    def _lb_render(self, data):
        for w in self._lb_inner.winfo_children(): w.destroy()
        if not data:
            tk.Label(self._lb_inner, text="No data yet. Run the macro to appear here!",
                     bg=BG1, fg=TXT3, font=FONT_LABEL).pack(anchor="w", pady=10, padx=12)
            self._lb_status_var.set("Empty leaderboard")
            return
        sorted_data = sorted(data.items(), key=lambda x: -x[1])
        medal = {0:"1.", 1:"2.", 2:"3."}
        my_name = self._player_name_var.get()
        for i, (username, seconds) in enumerate(sorted_data):
            is_me = username == my_name
            bg = "#151528" if is_me else (BG2 if i%2==0 else BG1)
            row = tk.Frame(self._lb_inner, bg=bg)
            row.pack(fill="x")
            rank = medal.get(i, f"  {i+1}.")
            fg = GOLD if i < 3 else (ACC if is_me else TXT)
            tk.Label(row, text=rank, bg=bg, fg=fg, font=FONT_LABEL, width=4, anchor="w").pack(side="left", padx=(10,0), pady=5)
            tk.Label(row, text=username, bg=bg, fg=fg, font=FONT_LABEL, width=22, anchor="w").pack(side="left", padx=(10,0))
            tk.Label(row, text=fmt_time(seconds), bg=bg, fg=TXT2,
                     font=FONT_MONO, width=14, anchor="w").pack(side="left", padx=(10,0))
            if is_me:
                tk.Label(row, text="← you", bg=bg, fg=ACC, font=FONT_LABEL).pack(side="left")
        self._lb_status_var.set(f"{len(sorted_data)} players  •  updated just now")

    def _build_credits_tab(self):
        root = tk.Frame(self.content_area, bg=BG1); self._reg("CREDITS", root)

        # Center everything
        inner = tk.Frame(root, bg=BG1)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        if self._icon128:
            tk.Label(inner, image=self._icon128, bg=BG1).pack(pady=(0,12))

        tk.Label(inner, text="MULTIFMACRO", bg=BG1, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack()
        tk.Label(inner, text=VERSION, bg=BG1, fg=ACC,
                 font=("Segoe UI",9)).pack(pady=(2,0))

        tk.Frame(inner, bg=BDR, height=1).pack(fill="x", padx=40, pady=14)

        tk.Label(inner, text="Created by  pws32z", bg=BG1, fg=TXT2,
                 font=("Segoe UI",9,"bold")).pack()
        tk.Label(inner, text="discord.gg/qGBB8T6xsw", bg=BG1, fg=TXT3,
                 font=FONT_LABEL).pack(pady=(2,8))
        btn(inner, "  Join Discord  ", lambda: webbrowser.open("https://discord.gg/qGBB8T6xsw"),
            color="#5865F2").pack()

        tk.Frame(inner, bg=BDR, height=1).pack(fill="x", padx=40, pady=14)

        tk.Label(inner, text="FISHSCOPE MACRO", bg=BG1, fg=TXT2,
                 font=("Segoe UI",9,"bold")).pack()
        tk.Label(inner, text="by  cresqnt-sys  ·  github.com/cresqnt-sys", bg=BG1, fg=TXT3,
                 font=FONT_LABEL).pack(pady=(2,8))
        btn(inner, "  FishScope GitHub  ",
            lambda: webbrowser.open("https://github.com/cresqnt-sys"),
            color=BG3).pack()

    # ── Save config ───────────────────────────────────────────────────────
    def _save_config(self):
        try:
            if hasattr(self, "wh_url"):
                self.cfg["Webhook"] = {"webhook_url":self.wh_url.get().strip(),
                                        "private_server":self.ps_url.get().strip(),
                                        "discord_user_id":self.disc_id.get().strip()}
            if hasattr(self, "roblox_username"):
                if not self.cfg.has_section("Player"): self.cfg["Player"] = {}
                self.cfg["Player"]["roblox_username"] = self.roblox_username.get().strip()
            if hasattr(self, "aura_enabled"):
                self.cfg["Aura"] = {"enabled":"1" if self.aura_enabled.get() else "0",
                                     "ping_on_aura":"1" if self.aura_ping.get() else "0"}
            if hasattr(self, "_aura_vars"):
                if not self.cfg.has_section("AuraFilter"):
                    self.cfg["AuraFilter"] = {}
                for name,(var,_) in self._aura_vars.items():
                    self.cfg["AuraFilter"][_cfg_key(name)] = "1" if var.get() else "0"
            if hasattr(self, "merch_log"):
                self.cfg["Merchant"] = {"log_detection":"1" if self.merch_log.get() else "0",
                                         "ping_mari":"1" if self.merch_ping_mari.get() else "0",
                                         "ping_jester":"1" if self.merch_ping_jester.get() else "0"}
            if hasattr(self, "ak_enabled"):
                self.cfg["AntiKick"] = {"enabled":"1" if self.ak_enabled.get() else "0",
                                         "interval_sec":self.ak_interval.get().strip()}
            if hasattr(self, "_ping_biome_vars"):
                self.cfg["BiomePing"] = {
                    _cfg_key(b): "1" if v.get() else "0"
                    for b,v in self._ping_biome_vars.items()
                }
            self.cfg["BiomeCounts"] = {
                _cfg_key(b): str(c) for b,c in self.biome_counts.items()
            }
            save_config(self.cfg)
            orig = self.status_var.get()
            self.status_var.set("● SAVED")
            self.root.after(1500, lambda: self.status_var.set(orig))
        except Exception as e:
            import traceback
            messagebox.showerror("Save Error", f"Failed to save config:\n{traceback.format_exc()}")

    # ── Timers ────────────────────────────────────────────────────────────
    def _ak_tick(self):
        if not self.started: return
        try: secs = int(self.ak_interval.get())
        except: secs = 600
        if self.ak_enabled.get():
            threading.Thread(target=do_anti_kick, daemon=True).start()
            self.ak_status_var.set(f"✓ Space pressed — next in {secs}s")
        self._ak_job = self.root.after(secs*1000, self._ak_tick)

    def _ak_start(self):
        """Schedule first anti-kick after the full interval (don't press on start)."""
        try: secs = int(self.ak_interval.get())
        except: secs = 600
        self.ak_status_var.set(f"⏳ Anti-kick armed — first press in {secs}s")
        self._ak_job = self.root.after(secs*1000, self._ak_tick)

    # ── Macro controls ────────────────────────────────────────────────────
    def _start(self):
        if self.started: return
        self._save_config()
        url = self.wh_url.get().strip()
        if not url or not url.startswith("https://"):
            messagebox.showerror("Error","Invalid or missing Webhook URL.\nMust start with https://"); return
        if not _get_log_dir():
            messagebox.showerror("Error","Roblox log folder not found. Open Roblox first."); return
        self.started = True; self.paused = False
        self._session_start = time.time()  # when this run began
        self.last_biome = get_latest_hovertext() or ""
        self.last_aura  = get_latest_equipped_aura() or ""
        self.last_merchant_ts = time.time()
        self.status_var.set("● RUNNING")
        self._start_btn.configure(bg="#1a3d2a")
        self.root.title("MultiFMacro  — RUNNING")
        threading.Thread(target=send_webhook,args=(url,make_embed("Macro started!")),daemon=True).start()
        self._poll()
        self._ak_start()
        self._timer_tick()


    def _pause(self):
        if not self.started: return
        self.paused = not self.paused
        if self.paused:
            self.status_var.set("● PAUSED")
            self._pause_btn.configure(bg=ACC); self.root.title("MultiFMacro  — PAUSED")
        else:
            self.status_var.set("● RUNNING")
            self._pause_btn.configure(bg=BG3); self.root.title("MultiFMacro  — RUNNING")

    def _stop(self):
        for job in [self._poll_job,self._ak_job]:
            if job:
                try: self.root.after_cancel(job)
                except: pass
        self._poll_job = self._ak_job = None
        if self._timer_job:
            try: self.root.after_cancel(self._timer_job)
            except: pass
        self._timer_job = None
        # Accumulate elapsed time so next START continues from here
        if self._session_start > 0:
            self._session_accum += time.time() - self._session_start
            self._session_start = 0.0
        url = self.wh_url.get().strip()
        if self.started and url:
            threading.Thread(target=send_webhook,args=(url,make_embed("Macro stopped.")),daemon=True).start()
        self.started = False; self.paused = False
        self._save_config()
        self.status_var.set("● IDLE"); self._start_btn.configure(bg=ACC)
        self._pause_btn.configure(bg=BG3)
        self.ak_status_var.set("Idle")
        self.biome_var.set("NORMAL")
        self.root.title(f"MultiFMacro  {VERSION}")

    def _test_hook(self):
        self._save_config()
        url = self.wh_url.get().strip()
        if not url: messagebox.showerror("Error","No webhook URL."); return
        def do():
            try:
                resp = requests.post(url, json=make_embed("Test webhook ✓", color=0x3ddc84), timeout=10)
                resp.raise_for_status()
                self.root.after(0, lambda: messagebox.showinfo("Test","Sent! Check your Discord channel."))
            except requests.exceptions.HTTPError as e:
                err = f"HTTP {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
                self.root.after(0, lambda m=err: messagebox.showerror("Webhook Error", f"Failed:\n{m}"))
            except Exception as e:
                self.root.after(0, lambda m=str(e): messagebox.showerror("Webhook Error", f"Failed:\n{m}"))
        threading.Thread(target=do, daemon=True).start()


    # ── Player info loader ───────────────────────────────────────────────
    def _load_player_info(self):
        """Load saved Roblox username + avatar from config on startup."""
        username = self.cfg.get("Player", "roblox_username", fallback="").strip()
        if not username:
            return
        self.root.after(0, lambda u=username: self._player_name_var.set(u))
        self.root.after(0, lambda: self._player_status_var.set("● Active"))
        user_id = get_roblox_user_id(username)
        if user_id:
            try:
                from PIL import ImageTk
                img = fetch_avatar_image(user_id, size=28)
                if img:
                    photo = ImageTk.PhotoImage(img)
                    self._avatar_photo = photo
                    self.root.after(0, lambda p=photo: self._avatar_label.configure(image=p))
            except Exception as e:
                print(f"[Avatar] {e}")

    # ── Session timer ────────────────────────────────────────────────────
    def _timer_tick(self):
        if not self.started: return
        elapsed = int(self._session_accum + (time.time() - self._session_start))
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.timer_var.set(f"{h:02d}:{m:02d}:{s:02d}")
        self._timer_job = self.root.after(1000, self._timer_tick)

    # ── Log poll — reads log every 500ms using SolsScope methods ──────────
    def _poll(self):
        if not self.started: return
        if not self.paused:
            try: self._check()
            except Exception as e:
                import traceback
                print(f"[Poll error] {traceback.format_exc()}")
        self._poll_job = self.root.after(500, self._poll)

    def _check(self):
        url = self.wh_url.get().strip()

        # ── Biome — SolsScope get_latest_hovertext() ──────────────────
        biome = get_latest_hovertext()
        if biome and biome != self.last_biome:
            prev = self.last_biome; self.last_biome = biome
            self.root.after(0, lambda b=biome: self.biome_var.set(b))
            if url:
                if biome == "NORMAL":
                    if prev and prev != "NORMAL":
                        s = self.cfg.get("Biomes",_cfg_key(prev),fallback="Message")
                        if s != "Nothing":
                            threading.Thread(target=send_webhook,
                                args=(url,make_biome_embed(prev,False,self.ps_url.get().strip(),
                                                           self.disc_id.get().strip(),s)),daemon=True).start()
                else:
                    s = self.cfg.get("Biomes",_cfg_key(biome),fallback="Message")
                    if s != "Nothing":
                        threading.Thread(target=send_webhook,
                            args=(url,make_biome_embed(biome,True,self.ps_url.get().strip(),
                                                       self.disc_id.get().strip(),s,
                                                       self._get_ping_biomes())),daemon=True).start()
            # Track count for every non-NORMAL biome start
            if biome != "NORMAL":
                self.biome_counts[biome] = self.biome_counts.get(biome, 0) + 1
                self.root.after(0, self._refresh_biome_stats)
                # Persist immediately so counts survive restarts
                self.cfg["BiomeCounts"] = {_cfg_key(b): str(c) for b,c in self.biome_counts.items()}
                threading.Thread(target=save_config, args=(self.cfg,), daemon=True).start()

        # ── Aura — SolsScope get_latest_equipped_aura() ───────────────
        if self.aura_enabled.get():
            aura = get_latest_equipped_aura()
            print(f"[Aura poll] detected={aura!r}  last={self.last_aura!r}")
            if aura and aura != self.last_aura:
                self.last_aura = aura
                self.root.after(0, lambda a=aura: self.aura_status_var.set(f"✨  {a}"))
                # Case-insensitive lookup in _aura_vars
                aura_lower = aura.lower()
                entry = next((v for k,v in self._aura_vars.items() if k.lower() == aura_lower), None)
                checked = entry[0].get() if entry else False
                rarity_num = _get_aura_rarity_number(aura)
                is_100m_plus = rarity_num >= 100_000_000
                print(f"[Aura fire] name={aura!r} checked={checked} rarity={rarity_num} is_100m+={is_100m_plus} url={bool(url)}")
                # Always send webhook; ping if checked OR rarity is 100m+
                should_ping = self.aura_ping.get() and (checked or is_100m_plus)
                if url:
                    threading.Thread(target=send_webhook,
                        args=(url, make_aura_embed(aura, self.disc_id.get().strip(),
                                                   should_ping)), daemon=True).start()
                else:
                    print("[Aura fire] SKIPPED — url is empty!")

        # ── Merchant — SolsScope get_latest_merchant_info() ───────────
        if self.merch_log.get():
            result = get_latest_merchant(self.last_merchant_ts)
            if result:
                name, ts = result
                self.last_merchant_ts = ts
                self.root.after(0, lambda m=name: self.merch_status_var.set(f"{m} detected!"))
                if url:
                    ping = ((name=="Mari"   and self.merch_ping_mari.get()) or
                            (name=="Jester" and self.merch_ping_jester.get()))
                    payload = make_merchant_embed(name, self.ps_url.get().strip())
                    if ping and self.disc_id.get().strip():
                        payload["content"] = f"<@{self.disc_id.get().strip()}>"
                    threading.Thread(target=send_webhook,args=(url,payload),daemon=True).start()

    def _on_close(self):
        for job in [self._poll_job, self._ak_job, self._timer_job]:
            if job:
                try: self.root.after_cancel(job)
                except: pass
        # Accumulate any remaining time
        if self._session_start > 0:
            self._session_accum += time.time() - self._session_start
            self._session_start = 0.0
        # Upload to leaderboard on close
        uname = (self.roblox_username.get().strip() if hasattr(self,"roblox_username") else "") or \
                (self._player_name_var.get() if hasattr(self,"_player_name_var") else "")
        new_secs = self._session_accum - getattr(self, "_last_lb_upload", 0.0)
        if uname and new_secs > 5:
            t = threading.Thread(target=lb_update, args=(uname, new_secs), daemon=True)
            t.start()
            t.join(timeout=4)
        url = self.wh_url.get().strip()
        if self.started and url:
            t = threading.Thread(target=send_webhook,
                args=(url, make_embed("Macro stopped.")), daemon=True)
            t.start()
            t.join(timeout=2)
        self.started = False
        try:
            self._save_config()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        # Also destroy the anchor root so the process fully exits
        try:
            self.root.master.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    import traceback

    # ── Taskbar anchor ────────────────────────────────────────────────────
    # overrideredirect Toplevels are invisible to the Windows taskbar.
    # Fix: keep a transparent off-screen Tk() root permanently alive so
    # Windows gives it a taskbar button.  The real UI is a Toplevel child.
    anchor = tk.Tk()
    anchor.title(f"MultiFMacro  {VERSION}")
    anchor.geometry("1x1+-32000+-32000")
    anchor.resizable(False, False)
    anchor.configure(bg="#000000")
    try:
        _set_window_icon(anchor)
        _ico = _get_photo(_ICON_64_B64, anchor)
        anchor.iconphoto(True, _ico)
    except Exception:
        pass
    # NEVER withdraw — that removes the taskbar slot.  Alpha=0 hides it visually.
    anchor.attributes("-alpha", 0.0)
    anchor.update()

    # Real frameless window
    root = tk.Toplevel(anchor)
    root.title(f"MultiFMacro  {VERSION}")

    # Track whether the user intentionally minimized
    _minimized = [False]
    _ignore_focus_until = [0.0]

    def _minimize():
        _minimized[0] = True
        _ignore_focus_until[0] = time.time() + 0.8  # ignore FocusIn for 800ms
        root.withdraw()

    def _restore():
        _minimized[0] = False
        root.deiconify()
        root.lift()
        root.focus_force()

    # Taskbar button click → anchor gets focus/map event → restore only if minimized
    def _anchor_focus(e=None):
        try:
            if time.time() < _ignore_focus_until[0]:
                return  # spurious FocusIn right after withdraw — ignore it
            if _minimized[0]:
                _restore()
            else:
                root.lift()
                root.focus_force()
        except Exception:
            pass

    anchor.bind("<FocusIn>", _anchor_focus)
    anchor.bind("<Map>",     _anchor_focus)

    def _tk_error(exc, val, tb):
        msg = "".join(traceback.format_exception(exc, val, tb))
        print(msg)
        try:
            messagebox.showerror("Unexpected Error", msg[-1000:])
        except Exception:
            pass
    root.report_callback_exception = _tk_error

    app = MultiFMacroApp(root)

    # Wire minimize button to our controlled minimize (not raw withdraw)
    app._minimize_fn = _minimize

    # ── Rounded corners via Windows 11 DWM API ───────────────────────────
    def _apply_rounded_corners(hwnd):
        try:
            import ctypes
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            pref = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(pref), ctypes.sizeof(pref)
            )
        except Exception:
            pass

    def _setup_window_style():
        try:
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, f"MultiFMacro  {VERSION}")
            if hwnd:
                _apply_rounded_corners(hwnd)
        except Exception:
            pass

    root.after(200, _setup_window_style)
    anchor.mainloop()

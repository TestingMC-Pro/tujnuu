import math
import traceback
import tkinter as tk
from tkinter import ttk

posArrow = 8.68011400560981
posArrowOffset = 0.00000007953368448855258
posArrowFine = 0.10544106641170162
negArrow = 8.7410329553163
negArrowFine = 0.10136464745734321
negArrowOffset = 0.00000008400136539190007
posTnT = 8.67362335175755 * 0.9
negTnT = 8.733855372210195 * 0.9
posFine = 0.010112727575963596 * 0.9
negFine = 0.010335220217364634 * 0.9
sideOffset = 0.796378035410971 * 0.9 - 0.49

trimArrow = [
    0,
    0.8741975000350434,
    1.7474285006966748,
    2.619571409382498,
    3.4904892604361533,
    4.360027759624948,
    5.228013079297519,
    6.094249372958224,
    6.958515974326133,
    7.8205642419025185
]
trimTnT = [
    0,
    0.8734785455679479 * 0.9,
    1.7460027262632432 * 0.9,
    2.6174521195454687 * 0.9,
    3.4876909994406082 * 0.9,
    4.356566374898484 * 0.9,
    5.223905775957048 * 0.9,
    6.089514756059614 * 0.9,
    6.953174075261127 * 0.9,
    7.814636525118937 * 0.9
]
trimFineTnT = [
    0,
    0.0010329740280212048 * 0.9,
    0.002071539746945771 * 0.9,
    0.003116319961532217 * 0.9,
    0.004167994321588394 * 0.9,
    0.00522730051831248 * 0.9,
    0.006295033922140227 * 0.9,
    0.00737204495600737 * 0.9,
    0.00845923325015693 * 0.9,
    0.009557537293892677 * 0.9
]
trimFineArrow = [
    0,
    0.01012996658256387,
    0.02032642404043858,
    0.030597266276200213,
    0.04095125892158624,
    0.05139811598717341,
    0.06194857676660194,
    0.0726144802414717,
    0.08340883302250142,
    0.0943458652197993
]


def intC(x):
    if abs(x - int(x)) > 0.999999:
        z = int(x) + int(math.copysign(1, x))
    else:
        z = int(x)
    return z


intC1 = lambda x: intC(x * 10) / 10


def getCount(diff, type):
    if type != 'arrowFine':
        if type == 'arrow':
            coarse = posArrow
            trim = trimArrow
        elif type == 'tnt':
            coarse = posTnT
            trim = trimTnT
        else:
            coarse = posFine
            trim = trimFineTnT
        x = diff - intC(diff / coarse) * coarse
        motion = min(trim, key=lambda v: abs(v - x))
        count = trim.index(motion) / 10
        return intC(diff / coarse) + count
    else:
        coarse = posArrow
        trim = trimArrow
        coarseFine = posArrowFine
        trimFine = trimFineArrow

        x = diff - intC(diff / coarse) * coarse
        motion = max(v for v in trim if v <= x)
        count = trim.index(motion) / 10
        z = diff - (intC(diff / coarse) * coarse + motion) - intC((x - motion) / coarseFine) * coarseFine
        motionFine = min(trimFine, key=lambda v: abs(v - z))
        countFine = trimFine.index(motionFine) / 10
        return intC(diff / coarse) + count + (intC((x - motion) / coarseFine) + countFine) / 100


def getVelocity(count, type):
    if type != 'arrowFine':
        countTrim = count - intC(count)
        if type == 'arrow':
            coarse = posArrow
            trim = trimArrow
        elif type == 'tnt':
            coarse = posTnT
            trim = trimTnT
        else:
            coarse = posFine
            trim = trimFineTnT
        coarsePart = intC(count)
        trimIdx = round(10 * countTrim)
        motion = trim[trimIdx]
        return coarsePart * coarse + motion
    else:
        coarse = posArrow
        trim = trimArrow
        coarseFine = posArrowFine
        trimFine = trimFineArrow

        coarsePart = intC(count)
        countTrim = count - intC(count)
        trimIdx = intC(10 * countTrim)
        motion = trim[trimIdx]

        coarsePartFine = intC((count - coarsePart - trimIdx / 10) * 100)
        countTrimFine = count - coarsePart - trimIdx / 10 - coarsePartFine / 100
        trimFineIdx = intC(countTrimFine * 1000)
        motionFine = trimFine[trimFineIdx]

        return coarsePart * coarse + motion + coarsePartFine * coarseFine + motionFine


def motionAddSearch(pVArrow, sVArrow, pVArrowAddIdeal):
    if math.copysign(pVArrow, sVArrow) == pVArrow:
        if pVArrowAddIdeal >= 0:
            pAccel = posArrow
            pAccelFine = posArrowFine
            sAccel = posArrow
            sAccelFine = posArrowFine
            a = lambda: getVelocity(pVArrowAddIdealCount, 'arrowFine')
            b = lambda: getVelocity(getCount(sVArrow / pVArrow * pVArrowAdd, 'arrowFine'), 'arrowFine')
            c = lambda: getCount(sVArrowAdd, 'arrowFine')
            d = lambda: getVelocity(pVArrowAddCountBest, 'arrowFine')
            e = lambda: getVelocity(sVArrowAddCountBest, 'arrowFine')
        else:
            pAccel = negArrow
            pAccelFine = negArrowFine
            sAccel = negArrow
            sAccelFine = negArrowFine
            a  = lambda: intC1(pVArrowAddIdealCount) * pAccel + (pVArrowAddIdealCount - intC1(pVArrowAddIdealCount)) * 100 * pAccelFine
            b1 = lambda: sVArrow / pVArrow * pVArrowAdd
            b2 = lambda: intC1(b1() / sAccel) + (b1() - intC1(b1() / sAccel) * sAccel) / sAccelFine / 100
            b  = lambda: intC1(b2()) * sAccel + (b2() - intC1(b2())) * 100 * sAccelFine
            c  = lambda: intC1(sVArrowAdd / sAccel) + intC1((sVArrowAdd - intC1(sVArrowAdd / sAccel) * sAccel) / sAccelFine) / 100
            d  = lambda: intC1(pVArrowAddCountBest) * pAccel + (pVArrowAddCountBest - intC1(pVArrowAddCountBest)) * 100 * pAccelFine
            e  = lambda: intC1(sVArrowAddCountBest) * sAccel + (sVArrowAddCountBest - intC1(sVArrowAddCountBest)) * 100 * sAccelFine
    else:
        if pVArrowAddIdeal >= 0:
            pAccel = posArrow
            pAccelFine = posArrowFine
            sAccel = negArrow
            sAccelFine = negArrowFine
            a  = lambda: getVelocity(pVArrowAddIdealCount, 'arrowFine')
            b1 = lambda: sVArrow / pVArrow * pVArrowAdd
            b2 = lambda: intC1(b1() / sAccel) + (b1() - intC1(b1() / sAccel) * sAccel) / sAccelFine / 100
            b  = lambda: intC1(b2()) * sAccel + (b2() - intC1(b2())) * 100 * sAccelFine
            c  = lambda: intC1(sVArrowAdd / sAccel) + intC1((sVArrowAdd - intC1(sVArrowAdd / sAccel) * sAccel) / sAccelFine) / 100
            d  = lambda: getVelocity(pVArrowAddCountBest, 'arrowFine')
            e  = lambda: intC1(sVArrowAddCountBest) * sAccel + (sVArrowAddCountBest - intC1(sVArrowAddCountBest)) * 100 * sAccelFine
        else:
            pAccel = negArrow
            pAccelFine = negArrowFine
            sAccel = posArrow
            sAccelFine = posArrowFine
            a = lambda: intC1(pVArrowAddIdealCount) * pAccel + (pVArrowAddIdealCount - intC1(pVArrowAddIdealCount)) * 100 * pAccelFine
            b = lambda: getVelocity(getCount(sVArrow / pVArrow * pVArrowAdd, 'arrowFine'), 'arrowFine')
            c = lambda: getCount(sVArrowAdd, 'arrowFine')
            d = lambda: intC1(pVArrowAddCountBest) * pAccel + (pVArrowAddCountBest - intC1(pVArrowAddCountBest)) * 100 * pAccelFine
            e = lambda: getVelocity(sVArrowAddCountBest, 'arrowFine')
    ratioDiff = float('inf')
    pVArrowAddCountBest = 0
    sVArrowAddCountBest = 0
    pVArrowAdd = 0
    sVArrowAdd = 0
    pVArrowAddIdealCount = round(pVArrowAddIdeal / pAccel, 3)
    while abs(pVArrowAddIdealCount) > 0.001:
        pVArrowAdd = a()
        sVArrowAdd = b()
        if abs(sVArrow / pVArrow - sVArrowAdd / pVArrowAdd) < ratioDiff:
            ratioDiff = abs(sVArrow / pVArrow - sVArrowAdd / pVArrowAdd)
            pVArrowAddCountBest = pVArrowAddIdealCount
            sVArrowAddCountBest = c()
        if ratioDiff <= 0.000001:
            break
        pVArrowAddIdealCount = pVArrowAddIdealCount - math.copysign(0.001, pVArrowAddIdealCount)
        pVArrowAdd = d()
        sVArrowAdd = e()
    return pVArrowAddCountBest, sVArrowAddCountBest, pVArrowAdd, sVArrowAdd, ratioDiff


class QuitRequested(Exception):
    pass


NUKE_LAYER = 15


def run_calculation(debug, nukeLayer, diffX, diffZ, cannonX=None, cannonZ=None,
                    targetX=None, targetZ=None):
    if not debug:
        diffX = targetX - cannonX
        diffZ = targetZ - cannonZ

    if nukeLayer == 0:
        raise QuitRequested('dumbass, u cant shoot an empty payload')
    if diffX == 0 and diffZ == 0:
        raise QuitRequested('are u trying to strike yo ass or sum')

    if diffX > 0 and diffZ > 0:
        mainCountX = getCount(diffX, 'tnt')
        mainCountZ = getCount(diffZ, 'tnt')
        xVArrow = getVelocity(mainCountX, 'arrow') + abs(mainCountZ) * posArrowOffset
        zVArrow = getVelocity(mainCountZ, 'arrow') + abs(mainCountX) * posArrowOffset
        xVBaseTnT = getVelocity(mainCountX, 'tnt')
        zVBaseTnT = getVelocity(mainCountZ, 'tnt')
    elif diffX <= 0 and diffZ <= 0:
        mainCountX = round((diffX / negTnT), 1)
        mainCountZ = round((diffZ / negTnT), 1)
        xVArrow = mainCountX * negArrow + abs(mainCountZ) * negArrowOffset
        zVArrow = mainCountZ * negArrow + abs(mainCountX) * negArrowOffset
        xVBaseTnT = mainCountX * negTnT
        zVBaseTnT = mainCountZ * negTnT
    elif diffX > 0:
        if abs(diffX) >= abs(diffZ):
            mainCountX = getCount(diffX, 'tnt')
            xVArrowIdeal = getVelocity(mainCountX, 'arrow')
            zVArrowIdeal = diffZ / diffX * xVArrowIdeal
            mainCountZ = round(zVArrowIdeal / negArrow, 1)
        else:
            mainCountZ = round((diffZ / negTnT), 1)
            zVArrowIdeal = mainCountZ * negArrow
            xVArrowIdeal = diffX / diffZ * zVArrowIdeal
            mainCountX = getCount(xVArrowIdeal, 'arrow')
        xVArrow = getVelocity(mainCountX, 'arrow') + abs(mainCountZ) * negArrowOffset
        zVArrow = mainCountZ * negArrow + abs(mainCountX) * posArrowOffset
        xVBaseTnT = getVelocity(mainCountX, 'tnt')
        zVBaseTnT = mainCountZ * negTnT
    else:
        if abs(diffX) >= abs(diffZ):
            mainCountX = round((diffX / negTnT), 1)
            xVArrowIdeal = mainCountX * negArrow
            zVArrowIdeal = diffZ / diffX * xVArrowIdeal
            mainCountZ = getCount(zVArrowIdeal, 'arrow')
        else:
            mainCountZ = getCount(diffZ, 'tnt')
            zVArrowIdeal = getVelocity(mainCountZ, 'arrow')
            xVArrowIdeal = diffX / diffZ * zVArrowIdeal
            mainCountX = round(xVArrowIdeal / negArrow, 1)
        xVArrow = mainCountX * negArrow + abs(mainCountZ) * posArrowOffset
        zVArrow = getVelocity(mainCountZ, 'arrow') + abs(mainCountX) * negArrowOffset
        xVBaseTnT = mainCountX * negTnT
        zVBaseTnT = getVelocity(mainCountZ, 'tnt')

    results = {}
    results['mainCountX'] = mainCountX
    results['mainCountZ'] = mainCountZ
    if debug:
        results['xVBaseTnT'] = xVBaseTnT / 0.9
        results['xVArrow'] = xVArrow
        results['zVBaseTnT'] = zVBaseTnT / 0.9
        results['zVArrow'] = zVArrow

    totalSpace = sideOffset * 2 / 11
    if abs(diffX) > abs(diffZ):
        bounceCount = math.ceil(math.log(sideOffset / abs(xVArrow / 2)) / math.log(0.099))
        xVArrowReduced = abs(xVArrow * 0.099 ** bounceCount)
        zVArrowReduced = abs(zVArrow * 0.099 ** bounceCount)
        relativeDirection = math.copysign(1, sideOffset * 2 - (xVArrowReduced + totalSpace))
        xVArrowAdd = totalSpace * (1 / 0.099) ** bounceCount / nukeLayer * abs(xVArrow) / xVArrow * relativeDirection
        vAddList = motionAddSearch(xVArrow, zVArrow, xVArrowAdd)
        xVArrowAddCount = vAddList[0]
        zVArrowAddCount = vAddList[1]
        xVArrowAdd = vAddList[2]
        zVArrowAdd = vAddList[3]

        fineX = (xVArrow + xVArrowAdd * nukeLayer / 2) * (-0.099) ** bounceCount - (
                    abs(xVArrow) / xVArrow) * sideOffset * (-1) ** bounceCount
        fineZ = (zVArrow + zVArrowAdd * nukeLayer / 2) * (-0.099) ** bounceCount - (
                    abs(xVArrow) / xVArrow) * sideOffset * (-1) ** bounceCount * (zVArrow / xVArrow)

    else:
        bounceCount = math.ceil(math.log(sideOffset / abs(zVArrow / 2)) / math.log(0.099))
        xVArrowReduced = abs(xVArrow * 0.099 ** bounceCount)
        zVArrowReduced = abs(zVArrow * 0.099 ** bounceCount)
        relativeDirection = math.copysign(1, sideOffset * 2 - (zVArrowReduced + totalSpace))
        zVArrowAdd = totalSpace * (1 / 0.099) ** bounceCount / nukeLayer * abs(zVArrow) / zVArrow * relativeDirection
        vAddList = motionAddSearch(zVArrow, xVArrow, zVArrowAdd)
        zVArrowAddCount = vAddList[0]
        xVArrowAddCount = vAddList[1]
        zVArrowAdd = vAddList[2]
        xVArrowAdd = vAddList[3]

        fineX = (xVArrow + xVArrowAdd * nukeLayer / 2) * (-0.099) ** bounceCount - (
                    abs(zVArrow) / zVArrow) * sideOffset * (-1) ** bounceCount * (xVArrow / zVArrow) + 0.00607894052332
        fineZ = (zVArrow + zVArrowAdd * nukeLayer / 2) * (-0.099) ** bounceCount - (
                    abs(zVArrow) / zVArrow) * sideOffset * (-1) ** bounceCount

    if fineX > 0:
        fineXCount = getCount(fineX, 'fine')
        fineXReal = getVelocity(fineXCount,'fine')
    else:
        fineXCount = round(fineX / negFine, 1)
        fineXReal = fineXCount * negFine
    if fineZ > 0:
        fineZCount = getCount(fineZ, 'fine')
        fineZReal = getVelocity(fineZCount,'fine')
    else:
        fineZCount = round(fineZ / negFine, 1)
        fineZReal = fineZCount * negFine

    results['fineXCount'] = fineXCount
    results['fineZCount'] = fineZCount
    results['xVArrowAddCount'] = xVArrowAddCount
    results['zVArrowAddCount'] = zVArrowAddCount
    results['bounceCount'] = bounceCount
    if debug:
        results['relativeDirection'] = relativeDirection
        results['fineX'] = fineXReal
        results['fineZ'] = fineZReal
        results['xVArrowAdd'] = round(xVArrowAdd, 13)
        results['zVArrowAdd'] = round(zVArrowAdd, 13)
        results['xVArrowReduced'] = round(xVArrowReduced, 13)
        results['zVArrowReduced'] = round(zVArrowReduced, 13)
        results['xVArrowAddReduced'] = xVArrowAdd * (-0.099) ** bounceCount
        results['zVArrowAddReduced'] = zVArrowAdd * (-0.099) ** bounceCount
        results['sideGapX'] = vAddList[4]
        results['sideGapZ'] = sideOffset * 2 - (zVArrowReduced + totalSpace)

    if abs(xVArrow) < abs(zVArrow):
        sideTnTDirection = 'Z'
        vectorCorrectionDirection = 'X'
        vectorCorrectionMotion = (xVArrow * zVBaseTnT / zVArrow) - xVBaseTnT
    else:
        sideTnTDirection = 'X'
        vectorCorrectionDirection = 'Z'
        vectorCorrectionMotion = (zVArrow * xVBaseTnT / xVArrow) - zVBaseTnT

    if vectorCorrectionMotion > 0:
        vectorCorrectionCoarseCount = intC(vectorCorrectionMotion / posTnT) + trimTnT.index(max(
            v for v in trimTnT if v <= vectorCorrectionMotion - intC(vectorCorrectionMotion / posTnT) * posTnT)) / 10
        vectorCorrectionFineCount = getCount(vectorCorrectionMotion - getVelocity(
            vectorCorrectionCoarseCount, 'tnt'),'fine')
    else:
        vectorCorrectionCoarseCount = math.ceil(vectorCorrectionMotion / negTnT * 10) / 10
        vectorCorrectionFineCount = round((vectorCorrectionMotion - vectorCorrectionCoarseCount * negTnT) / negFine, 1)

    results['sideTnTDirection'] = sideTnTDirection
    results['vectorCorrectionDirection'] = vectorCorrectionDirection
    results['vectorCorrectionCoarseCount'] = vectorCorrectionCoarseCount
    results['vectorCorrectionFineCount'] = vectorCorrectionFineCount
    if debug:
        results['vectorCorrectionMotion'] = vectorCorrectionMotion / 0.9

    directionFlip = 'ON' if vectorCorrectionDirection == 'Z' else 'OFF'
    if directionFlip == 'ON':
        fuseFlip = 'ON' if mainCountX > 0 else 'OFF'
    else:
        fuseFlip = 'ON' if mainCountZ > 0 else 'OFF'

    results['directionFlip'] = directionFlip
    results['fuseFlip'] = fuseFlip

    return results


class ResultRow(ttk.Frame):
    def __init__(self, parent, label):
        super().__init__(parent)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label, style='RowLabel.TLabel').grid(
            row=0, column=0, sticky='w', padx=(2, 8), pady=3)
        self.value_var = tk.StringVar(value='—')
        ttk.Label(self, textvariable=self.value_var, style='RowValue.TLabel').grid(
            row=0, column=1, sticky='e', padx=(0, 2), pady=3)

    def set(self, value):
        if isinstance(value, float):
            self.value_var.set(f'{value:,.6f}'.rstrip('0').rstrip('.') if '.' in f'{value:,.6f}' else f'{value:,.6f}')
        else:
            self.value_var.set(str(value))

    def clear(self):
        self.value_var.set('—')


class Section(ttk.LabelFrame):
    """A titled card containing a set of ResultRows."""
    def __init__(self, parent, title):
        super().__init__(parent, text=title, style='Card.TLabelframe')
        self.rows = {}

    def add_row(self, key, label):
        row = ResultRow(self, label)
        row.pack(fill='x', padx=6, pady=1)
        self.rows[key] = row
        return row

    def set(self, key, value):
        if key in self.rows:
            self.rows[key].set(value)

    def clear_all(self):
        for row in self.rows.values():
            row.clear()


class CannonGUI(tk.Tk):
    ACCENT = '#3a6ea5'
    BG = '#f4f6f9'
    CARD_BG = '#ffffff'

    def __init__(self):
        super().__init__()
        self.title('what is this diddy blud doing on the calculator')
        self.geometry('620x780')
        self.minsize(560, 600)
        self.configure(bg=self.BG)

        self._setup_style()

        self.debug_var = tk.StringVar(value='n')

        outer = ttk.Frame(self, style='App.TFrame')
        outer.pack(fill='both', expand=True)

        header = ttk.Frame(outer, style='Header.TFrame')
        header.pack(fill='x')
        ttk.Label(header, text='OAC calculator',
                  style='Title.TLabel').pack(anchor='w', padx=16, pady=(14, 2))
        ttk.Label(header, text='Calc for OAC',
                  style='Subtitle.TLabel').pack(anchor='w', padx=16, pady=(0, 12))

        body = ttk.Frame(outer, style='App.TFrame')
        body.pack(fill='both', expand=True, padx=14, pady=10)

        input_area = ttk.Frame(body, style='App.TFrame')
        input_area.pack(fill='x', pady=(0, 10))

        self.input_canvas = tk.Canvas(input_area, bg=self.BG, highlightthickness=0, height=260)
        input_vsb = ttk.Scrollbar(input_area, orient='vertical', command=self.input_canvas.yview)
        self.input_canvas.configure(yscrollcommand=input_vsb.set)
        input_vsb.pack(side='right', fill='y')
        self.input_canvas.pack(side='left', fill='both', expand=True)

        self.input_container = ttk.Frame(self.input_canvas, style='App.TFrame')
        self.input_window = self.input_canvas.create_window((0, 0), window=self.input_container, anchor='nw')
        self.input_container.bind(
            '<Configure>',
            lambda e: self.input_canvas.configure(scrollregion=self.input_canvas.bbox('all'))
        )
        self.input_canvas.bind(
            '<Configure>',
            lambda e: self.input_canvas.itemconfig(self.input_window, width=e.width)
        )

        def _on_input_mousewheel(event):
            delta = event.delta
            if delta:
                self.input_canvas.yview_scroll(int(-1 * (delta / 120)), 'units')
            elif event.num == 4:
                self.input_canvas.yview_scroll(-1, 'units')
            elif event.num == 5:
                self.input_canvas.yview_scroll(1, 'units')

        def _bind_input_wheel(event):
            self.input_canvas.bind_all('<MouseWheel>', _on_input_mousewheel)
            self.input_canvas.bind_all('<Button-4>', _on_input_mousewheel)
            self.input_canvas.bind_all('<Button-5>', _on_input_mousewheel)

        def _unbind_input_wheel(event):
            self.input_canvas.unbind_all('<MouseWheel>')
            self.input_canvas.unbind_all('<Button-4>')
            self.input_canvas.unbind_all('<Button-5>')

        self.input_canvas.bind('<Enter>', _bind_input_wheel)
        self.input_canvas.bind('<Leave>', _unbind_input_wheel)

        mode_card = ttk.LabelFrame(self.input_container, text='Mode', style='Card.TLabelframe')
        mode_card.pack(fill='x', pady=(0, 10))
        ttk.Radiobutton(
            mode_card, text='Debug  (raw diff X/Z · nuke layer fixed at 15)',
            variable=self.debug_var, value='y', command=self.on_mode_change
        ).pack(anchor='w', padx=8, pady=(4, 2))
        ttk.Radiobutton(
            mode_card, text='Normal  (cannon position + target position)',
            variable=self.debug_var, value='n', command=self.on_mode_change
        ).pack(anchor='w', padx=8, pady=(2, 6))

        self.entries = {}

        self.debug_frame = ttk.LabelFrame(self.input_container, text='Debug inputs', style='Card.TLabelframe')
        self.diffX_var = tk.StringVar()
        self.diffZ_var = tk.StringVar()
        self._labeled_entry(self.debug_frame, 'diff X', self.diffX_var, 'diffX')
        self._labeled_entry(self.debug_frame, 'diff Z', self.diffZ_var, 'diffZ')

        self.normal_frame = ttk.LabelFrame(self.input_container, text='Normal inputs', style='Card.TLabelframe')
        self.cannonX_var = tk.StringVar()
        self.cannonZ_var = tk.StringVar()
        self.targetX_var = tk.StringVar()
        self.targetZ_var = tk.StringVar()
        self._labeled_entry(self.normal_frame, 'cannon X', self.cannonX_var, 'cannonX')
        self._labeled_entry(self.normal_frame, 'cannon Z', self.cannonZ_var, 'cannonZ')
        self._labeled_entry(self.normal_frame, 'target X', self.targetX_var, 'targetX')
        self._labeled_entry(self.normal_frame, 'target Z', self.targetZ_var, 'targetZ')

        for var in (self.diffX_var, self.diffZ_var,
                    self.cannonX_var, self.cannonZ_var, self.targetX_var, self.targetZ_var):
            var.trace_add('write', lambda *args: self.live_validate())

        btn_row = ttk.Frame(body, style='App.TFrame')
        btn_row.pack(fill='x', pady=(4, 4))
        self.calc_button = ttk.Button(btn_row, text='Calculate', style='Accent.TButton',
                                       command=self.on_calculate)
        self.calc_button.pack(side='left')
        self.status_var = tk.StringVar(value='')
        ttk.Label(btn_row, textvariable=self.status_var, style='Error.TLabel').pack(
            side='left', padx=12)

        self.warning_var = tk.StringVar(value='')
        self.warning_label = ttk.Label(body, textvariable=self.warning_var,
                                        style='Warning.TLabel', justify='left', wraplength=560)
        self.warning_label.pack(fill='x', pady=(0, 8))

        canvas_frame = ttk.Frame(body, style='App.TFrame')
        canvas_frame.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg=self.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.results_container = ttk.Frame(self.canvas, style='App.TFrame')
        self.results_window = self.canvas.create_window((0, 0), window=self.results_container, anchor='nw')
        self.results_container.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.itemconfig(self.results_window, width=e.width)
        )

        self.main_section = Section(self.results_container, 'Main Accel')
        self.main_section.pack(fill='x', pady=(0, 8))
        self.main_section.add_row('mainCountX', 'Main count X')
        self.main_section.add_row('mainCountZ', 'Main count Z')
        self.main_section.add_row('xVArrow', 'Arrow velocity X')
        self.main_section.add_row('zVArrow', 'Arrow velocity Z')
        self.main_section.add_row('xVBaseTnT', 'Base TNT velocity X')
        self.main_section.add_row('zVBaseTnT', 'Base TNT velocity Z')

        self.fine_section = Section(self.results_container, 'Fine Accel')
        self.fine_section.pack(fill='x', pady=(0, 8))
        self.fine_section.add_row('fineXCount', 'Fine X count')
        self.fine_section.add_row('fineZCount', 'Fine Z count')
        self.fine_section.add_row('xVArrowAddCount', 'Arrow-add count X')
        self.fine_section.add_row('zVArrowAddCount', 'Arrow-add count Z')
        self.fine_section.add_row('bounceCount', 'Bounce count')

        self.vector_section = Section(self.results_container, 'Side TNT / Vector Correction')
        self.vector_section.pack(fill='x', pady=(0, 8))
        self.vector_section.add_row('vectorCorrectionDirection', 'Correction direction')
        self.vector_section.add_row('vectorCorrectionCoarseCount', 'Correction coarse count')
        self.vector_section.add_row('vectorCorrectionFineCount', 'Correction fine count')
        self.vector_section.add_row('vectorCorrectionMotion', 'Correction motion (raw)')
        self.vector_section.add_row('directionFlip', 'Direction flip')
        self.vector_section.add_row('fuseFlip', 'Fuse flip')

        self.debug_section = Section(self.results_container, 'Debug Details')
        self.debug_section.add_row('relativeDirection', 'Relative direction')
        self.debug_section.add_row('fineX', 'Fine X (raw)')
        self.debug_section.add_row('fineZ', 'Fine Z (raw)')
        self.debug_section.add_row('xVArrowAdd', 'Arrow-add velocity X (raw)')
        self.debug_section.add_row('zVArrowAdd', 'Arrow-add velocity Z (raw)')
        self.debug_section.add_row('xVArrowReduced', 'Arrow velocity X reduced')
        self.debug_section.add_row('zVArrowReduced', 'Arrow velocity Z reduced')
        self.debug_section.add_row('xVArrowAddReduced', 'Arrow-add X reduced')
        self.debug_section.add_row('zVArrowAddReduced', 'Arrow-add Z reduced')
        self.debug_section.add_row('sideGapX', 'Side gap X')
        self.debug_section.add_row('sideGapZ', 'Side gap Z')

        self.on_mode_change()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure('App.TFrame', background=self.BG)
        style.configure('Header.TFrame', background=self.ACCENT)
        style.configure('Title.TLabel', background=self.ACCENT, foreground='white',
                         font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', background=self.ACCENT, foreground='#dbe6f2',
                         font=('Segoe UI', 9))
        style.configure('Card.TLabelframe', background=self.CARD_BG, borderwidth=1,
                         relief='solid')
        style.configure('Card.TLabelframe.Label', background=self.CARD_BG,
                         foreground=self.ACCENT, font=('Segoe UI', 10, 'bold'))
        style.configure('RowLabel.TLabel', background=self.CARD_BG,
                         font=('Segoe UI', 9), foreground='#333333')
        style.configure('RowValue.TLabel', background=self.CARD_BG,
                         font=('Consolas', 10, 'bold'), foreground='#1a1a1a')
        style.configure('Error.TLabel', background=self.BG, foreground='#b3261e',
                         font=('Segoe UI', 9, 'bold'))
        style.configure('Warning.TLabel', background=self.BG, foreground='#b3691e',
                         font=('Segoe UI', 9, 'bold'))
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TFrame', background=self.CARD_BG)
        style.configure('TEntry', padding=4)
        style.configure('Normal.TEntry', padding=4)
        style.configure('Error.TEntry', padding=4, fieldbackground='#fbdcdc',
                         bordercolor='#b3261e', lightcolor='#b3261e', darkcolor='#b3261e')
        style.map('Error.TEntry', fieldbackground=[('!disabled', '#fbdcdc')])

    def _labeled_entry(self, parent, label, var, key):
        row = ttk.Frame(parent, style='TFrame')
        row.pack(fill='x', padx=8, pady=3)
        ttk.Label(row, text=label, width=16, anchor='w', style='RowLabel.TLabel').pack(side='left')
        entry = ttk.Entry(row, textvariable=var, style='Normal.TEntry')
        entry.pack(side='left', fill='x', expand=True)
        self.entries[key] = entry
        return entry

    def on_mode_change(self):
        debug = self.debug_var.get() == 'y'
        if debug:
            self.normal_frame.pack_forget()
            self.debug_frame.pack(fill='x', pady=(0, 10))
            self.debug_section.pack(fill='x', pady=(0, 8))
        else:
            self.debug_frame.pack_forget()
            self.normal_frame.pack(fill='x', pady=(0, 10))
            self.debug_section.pack_forget()
        self.live_validate()

    def _mark(self, key, bad):
        entry = self.entries.get(key)
        if entry is not None:
            entry.configure(style='Error.TEntry' if bad else 'Normal.TEntry')

    def live_validate(self):
        debug = self.debug_var.get() == 'y'

        all_keys = ['diffX', 'diffZ', 'cannonX', 'cannonZ', 'targetX', 'targetZ']
        for key in all_keys:
            self._mark(key, False)

        errors = []
        warnings = []

        if debug:
            diffX = diffZ = None
            try:
                diffX = float(self.diffX_var.get())
            except ValueError:
                self._mark('diffX', True)
                errors.append('diff X must be a number.')
            try:
                diffZ = float(self.diffZ_var.get())
            except ValueError:
                self._mark('diffZ', True)
                errors.append('diff Z must be a number.')

            if diffX is not None and diffZ is not None and diffX == 0 and diffZ == 0:
                self._mark('diffX', True)
                self._mark('diffZ', True)
                errors.append('diff X and diff Z cannot both be 0.')

        else:
            coord_vals = {}
            for key, var in (('cannonX', self.cannonX_var), ('cannonZ', self.cannonZ_var),
                              ('targetX', self.targetX_var), ('targetZ', self.targetZ_var)):
                try:
                    coord_vals[key] = float(var.get())
                except ValueError:
                    self._mark(key, True)
                    errors.append(f'{key} must be a number.')

            if len(coord_vals) == 4:
                cannonX = coord_vals['cannonX']
                cannonZ = coord_vals['cannonZ']
                targetX = coord_vals['targetX']
                targetZ = coord_vals['targetZ']

                non_integer_keys = [k for k in ('cannonX', 'cannonZ', 'targetX', 'targetZ')
                                     if not coord_vals[k].is_integer()]
                if non_integer_keys:
                    for k in non_integer_keys:
                        self._mark(k, True)
                    warnings.append('All coordinates should be whole numbers.')

                bad_axes = []
                if cannonX % 16 != 0:
                    self._mark('cannonX', True)
                    bad_axes.append('X')
                if cannonZ % 16 != 0:
                    self._mark('cannonZ', True)
                    bad_axes.append('Z')
                if bad_axes:
                    errors.append(f'Cannon origin {" and ".join(bad_axes)} must be divisible by 16.')

                distance = math.hypot(targetX - (cannonX + 8), targetZ - (cannonZ + 8))
                if distance < 100:
                    self._mark('cannonX', True)
                    self._mark('cannonZ', True)
                    self._mark('targetX', True)
                    self._mark('targetZ', True)
                    errors.append(f'Target is only {distance:.1f} blocks from the cannon (must be at least 100).')

        self.status_var.set('  '.join(errors))
        self.warning_var.set('\n'.join(warnings))

        if errors or warnings:
            self.calc_button.state(['disabled'])
        else:
            self.calc_button.state(['!disabled'])

    def on_calculate(self):
        debug = self.debug_var.get() == 'y'

        if debug:
            diffX = float(self.diffX_var.get())
            diffZ = float(self.diffZ_var.get())
            kwargs = dict(debug=True, nukeLayer=NUKE_LAYER, diffX=diffX, diffZ=diffZ)
        else:
            cannonX = float(self.cannonX_var.get()) + 8
            cannonZ = float(self.cannonZ_var.get()) + 8
            targetX = float(self.targetX_var.get())
            targetZ = float(self.targetZ_var.get())
            kwargs = dict(debug=False, nukeLayer=NUKE_LAYER, diffX=None, diffZ=None,
                           cannonX=cannonX, cannonZ=cannonZ, targetX=targetX, targetZ=targetZ)

        for section in (self.main_section, self.fine_section, self.vector_section, self.debug_section):
            section.clear_all()

        try:
            results = run_calculation(**kwargs)
        except QuitRequested as e:
            self.status_var.set(str(e))
            return
        except Exception as e:
            self.status_var.set(f'Error: {e}')
            print('--- OAC calculator: error during calculation ---')
            traceback.print_exc()
            return

        for section in (self.main_section, self.fine_section, self.vector_section, self.debug_section):
            for key in section.rows:
                if key in results:
                    section.set(key, results[key])


if __name__ == '__main__':
    app = CannonGUI()
    app.mainloop()
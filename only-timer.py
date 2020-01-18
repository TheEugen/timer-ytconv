import time
from threading import Timer
from threading import Thread
import winsound
import subprocess
import os
import sys

try:
    import PySimpleGUI as sg
    if sg.version < '4.14.1':
        print("\nFound unsupported version, upgrading PySimpleGUI\n")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'PySimpleGUI'])
        print("\nFinished upgrade, restarting program\n")
        subprocess.check_call([sys.executable, __file__])
        sys.exit()
except ModuleNotFoundError:
    print("\nCould not find module, installing: PySimpleGUI\n")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PySimpleGUI'])
    import PySimpleGUI as sg

sg.change_look_and_feel('Topanga')

try:
    from pygame import mixer
except ModuleNotFoundError:
    print("\nCould not find module, installing: pygame\n")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
    from pygame import mixer

try:
    import psutil
except ModuleNotFoundError:
    print("\nCould not find module, installing: psutil\n")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    import psutil


class Status():
    def __init__(self):
        self.soundstop = False
        self.timerrunning = False

    def setSoundStop(self, b):
        self.soundstop = b

    def getSoundStop(self):
        return self.soundstop

    def setTimerRunning(self, b):
        self.timerrunning = b

    def getTimerRunning(self):
        return self.timerrunning



def timerDone(window, status, usersound):
    status.setSoundStop(False)
    status.setTimerRunning(False)

    window['lefttext'].Update("Beendet um: " + time.strftime('%X'))
    window['righttext'].Update("")

    window.Normal()

    if usersound.endswith(('.mp3','.wav','.ogg')):
        mixer.music.play()
        while True:
            if status.getSoundStop() == True:
                mixer.music.stop()
                break
    else:
        while status.getSoundStop() == False:
            winsound.Beep(600,500)

def startTimer(window, status, usertime):
    status.setTimerRunning(True)

    saved_sound = EntryExists()
    if saved_sound != None:
        usersound = saved_sound.replace('#','')
    else:
        usersound = ''

    timer = Timer(usertime*60, timerDone, args = [window, status, usersound])
    timer.start()
    start_time = int(round(time.time() * 100))
    finish_time = start_time + usertime * 60 * 100
    window['lefttext'].Update("Gestartet um: " + time.strftime('%X'))

    disableButton(('Los','1m','2m','5m','10m','15m','30m','browser'), True, window)
    disableButton('Stopp', False, window)
    window.Minimize()

    if mixer.get_init() == None:
        mixer.init()
    if len(usersound) > 0 and usersound.endswith(('.mp3','.wav','.ogg')):
        mixer.music.load(usersound)

    return start_time, finish_time, timer

def disableButton(button, boolean, window):
    i = 0
    if type(boolean) == tuple:
        for bool in boolean:
            window[button[i]].Update(disabled = bool)
            i += 1
    else:
        if type(button) == tuple:
            for btn in button:
                window[btn].Update(disabled = boolean)
        else:
            window[button].Update(disabled = boolean)

def EntryExists():
    with open(__file__, 'r') as f:
        for line in f:
            continue
        line = line.replace('\n','')
        if line.endswith(('.mp3','.wav','.ogg')):
            return line
        return None

def makeEntry(window, usersound):
    with open(__file__, 'r') as f:
        code = code_bak = f.read()

    with open(__file__, 'a') as f:
        try:
            f.write('#' + usersound + '\n')
            window['righttext'].Update('')
        except:
            f.write(code_bak)
            window['righttext'].Update('Fehler aufgetreten')

def resetEntrys(window):
    with open(__file__, 'r') as f:
        code = code_bak = f.read()

    with open(__file__, 'w') as f:
        try:
            edited_code = ''
            code = code.strip().splitlines()

            for line in code:
                if not line.endswith(('.mp3','.wav','.ogg')):
                    edited_code += line + '\n'

            f.write(edited_code)
            window['righttext'].Update('Alle Einträge entfernt')
        except:
            f.write(code_bak)
            window['righttext'].Update('Fehler aufgetreten')

def removeLastEntry(window):
    with open(__file__, 'r') as f:
        code = code_bak = f.read()

    with open(__file__, 'w') as f:
        try:
            edited_code = ''
            code = code.strip().splitlines()

            if code[len(code) - 1].endswith(('.mp3','.wav','.ogg')):
                code.remove(code[len(code) - 1])

            for line in code:
                edited_code += line + '\n'

            f.write(edited_code)
            window['righttext'].Update("Letzten Eintrag entfernt")
        except:
            f.write(code_bak)
            window['righttext'].Update("Fehler aufgetreten")

def main():
    status = Status()

    #menu_def = [['File', ['Open', 'Save', 'Exit'  ]],
                #['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                #['Help', 'About...'], ]

    layout = [  #[sg.Menu(menu_def, )],
                [sg.Text('Dauer einstellen (in Minuten):', key = 'lefttext', justification = 'left'),
                 sg.Text('', size = (20, 1), key = 'righttext', justification = 'center')],
                [sg.InputText(size = (13, 1), key = 'userinput', focus = True, pad = ((0, 13),(0, 0))), sg.Button('1m'), sg.Button('5m'),
                 sg.Button('15m'), sg.Button('Last', pad = ((10, 0),(0, 0))),
                 sg.Input(enable_events = True, visible = False, key = 'usersound'),
                 sg.FileBrowse('Sound', target = 'usersound', key = 'browser')],
			    [sg.Button('Los'), sg.Button('Stopp', disabled = True, pad = ((14, 0),(0, 0))),
                 sg.Button('2m', pad = ((13, 5),(0, 0))), sg.Button('10m'), sg.Button('30m'),
                 sg.Button('Reset', pad = ((10, 0),(0, 0))), sg.Button('Exit')] ]

    window = sg.Window('Timer', layout, default_button_element_size=(4, 1), auto_size_buttons=False)

    while (True):
        event, values = window.Read(timeout=30)
        cpu_percent = psutil.cpu_percent()
        if event in (None, 'Exit'):
            if not status.getSoundStop():
                status.setSoundStop(True)
            if status.getTimerRunning():
                timer.cancel()
                status.setTimerRunning(False)
            break
        elif event in ('Los'):
            try:
                start_time, finish_time, timer = startTimer(window, status, float(values['userinput']))
            except ValueError:
                window['lefttext'].Update("Ungültige Eingabe")
                window['righttext'].Update("")
        elif event in ('1m'):
            start_time, finish_time, timer = startTimer(window, status, 1)
        elif event in ('2m'):
            start_time, finish_time, timer = startTimer(window, status, 2)
        elif event in ('5m'):
            start_time, finish_time, timer = startTimer(window, status, 5)
        elif event in ('10m'):
            start_time, finish_time, timer = startTimer(window, status, 10)
        elif event in ('15m'):
            start_time, finish_time, timer = startTimer(window, status, 15)
        elif event in ('30m'):
            start_time, finish_time, timer = startTimer(window, status, 30)
        elif event in ('Stopp'):
            status.setSoundStop(True)
            if status.getTimerRunning():
                timer.cancel()
                status.setTimerRunning(False)
            window['lefttext'].Update("Dauer einstellen (in Minuten):")
            window['righttext'].Update("Gestoppt um: " + time.strftime('%X'))
            disableButton(('Los','1m','2m','5m','10m','15m','30m','browser'), False, window)
            disableButton('Stopp', True, window)
        elif event in ('Last'):
            removeLastEntry(window)
        elif event in ('Reset'):
            resetEntrys(window)
        elif event in ('usersound'):
            if len(values['usersound']) > 0:
                if not values['usersound'].endswith(('.mp3','.wav','.ogg')):
                    window.Element('righttext').Update("Ungültiges Dateiformat")
                else:
                    makeEntry(window, values['usersound'])

        if status.getTimerRunning():
            remaining_time = round(finish_time - int(round(time.time() * 100)))
            window.Element('righttext').Update('{:02d}:{:02d}.{:02d}'.format((remaining_time // 100) // 60,
                                                                      (remaining_time // 100) % 60,
                                                                      remaining_time % 100))

    if mixer.get_init() != None:
        mixer.quit()
    window.close()

main()

# -*- coding:utf-8 -*-

import PySimpleGUI as sg

import subprocess
import os


def update():
  try:
    os.getcwd()

    p = subprocess.Popen('''
    cd ../../..
    for f in `ls ./`
    do
      if [ -d "${f}" ]
      then
          echo -e "\n${f}"
          cd ${f}
    
          git fetch -aptP
          echo "update result:"
          git pull --rebase
    
          cd ..
        fi
    done
    ''', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=False)
    output = p.stdout.read()
    # p.terminate()
    code = 0
    print('execute success!')
  except subprocess.CalledProcessError as e:
    code = e.returncode
    output = e.output
    print('execute error!')
    exit()
  return code, output


if __name__ == '__main__':
  layout = [
    [sg.Button(key='-GO-', button_text='一键更新', font='Helvetica 14',
               size=(14, 1),
               auto_size_button=True)],
  ]

  # Create the window
  window = sg.Window('Git Update', layout)

  while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
      break
    elif event in ('-GO-'):
      window['-GO-'].update(disabled=True, text="正在更新...")
      window.refresh()
      code, output = update()
      # print(code, output)
      if code == 1:
        window['-GO-'].update(disabled=False, text="更新完成 :)",
                              button_color=('white', 'green'))
      else:
        window['-GO-'].update(disabled=False, text="更新失败 :(",
                              button_color=('white', 'red'))
    # print(event, values)
  window.close()

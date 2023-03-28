import PySimpleGUI as sg
import subprocess
import webbrowser

sg.theme('LightBlue')

start = 'https://'
branch = '-grey-go.t2.moego.pet'

# 打开窗口并返回一个视图对象
def open_window():
  # 设计窗口布局
  layout = [
    [sg.Text('Branch Name:'), sg.InputText(key='name')],
    [sg.Text('Password:'), sg.InputText(password_char='*', key='password')],
    [sg.Text('连接集群'),
     sg.Button('运行', size=(8, 1), key='main_run')],
    [sg.Text('moego-service-business'),
     sg.Button('运行', size=(8, 1), key='run_business')],
    [sg.Text('moego-service-customer'),
     sg.Button('运行', size=(8, 1), key='run_customer')],
    [sg.Text('moego-service-grooming'),
     sg.Button('运行', size=(8, 1), key='run_grooming')],
    [sg.Text('灰度网关:'),
     sg.Button('https://grey.t2.moego.pet',
               button_color=(sg.theme_background_color(), 'blue'),
               font=('Arial', 10), key='_LINK_', border_width=0)],
    [sg.Text('当前分支:'),
     sg.Button('https://go.t2.moego.pet',
               button_color=(sg.theme_background_color(), 'blue'),
               font=('Arial', 10), key='_BRANCH_', border_width=0)],
    [sg.Button('Close')],
  ]

  # 创建窗口
  window = sg.Window('Local Test', layout)

  return window


# 运行主程序
def main():
  # 打开窗口
  window = open_window()

  while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Close':
      break

    # if event == 'name':
    #   name_branch = start + str.strip(values['name']) + branch
    #   window['_BRANCH_'].update(text=name_branch)

    if event == 'main_run':
      name_branch = start + str.strip(values['name']) + branch
      window['_BRANCH_'].update(text=name_branch)
      p = subprocess.Popen(
          'echo ' + str.strip(values['password']) + ' | sudo -S ktctl connect -n ns-testing --withLabel "sidecar.istio.io/inject=true"',
          shell=True)
      window['main_run'].update('运行中')
      window.refresh()
    elif event == '运行中':
      p.kill()
      window['main_run'].update('运行')

    if event == 'run_business':
      p = subprocess.Popen(
          'ktctl preview moego-business-groom-debug-' + str.strip(values['name']) + ' --expose 9203:9203 -n ns-testing --withLabel "sidecar.istio.io/inject=true"',
          shell=True)
      window['run_business'].update('运行中')
    elif event == '运行中':
      p.kill()
      window['run_business'].update('运行')

    if event == 'run_customer':
      p = subprocess.Popen(
          'ktctl preview moego-customer-groom-debug-' + str.strip(values['name']) + ' --expose 9201:9201 -n ns-testing --withLabel "sidecar.istio.io/inject=true"',
          shell=True)
      window['run_customer'].update('运行中')
    elif event == '运行中':
      p.kill()
      window['run_customer'].update('运行')

    if event == 'run_grooming':
      p = subprocess.Popen(
          'ktctl preview moego-service-groom-debug-' + str.strip(values['name']) + ' --expose 9206:9206 -n ns-testing --withLabel "sidecar.istio.io/inject=true"',
          shell=True)
      window['run_grooming'].update('运行中')
    elif event == '运行中':
      p.kill()
      window['run_grooming'].update('运行')

    if event == '_BRANCH_':
      if str.strip(values['name']) == "":
        webbrowser.open("https://go.t2.moego.pet")
      else:
        webbrowser.open(start + str.strip(values['name']) + branch)

    if event == '_LINK_':
      webbrowser.open('https://grey.t2.moego.pet/')

  # 关闭窗口
  window.close()


if __name__ == '__main__':
  main()
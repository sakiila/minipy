import xlrd
import xlwt
from pathlib import Path, PurePath

# 文件
prepared_file = 'D:/Books/学习列表.xls'
# 拆分文件保存路径
dst_path = 'D:/Books'

data = xlrd.open_workbook(prepared_file)
table = data.sheets()[0]
# 取得表头
result_header = table.row_values(rowx=0, start_colx=0, end_colx=None)

# 定义写入文件的函数
def write_to_file(filename, cnt):
    '''
    filename : 写入的文件名
    cnt      : 写入的内容
    '''
    workbook = xlwt.Workbook(encoding='utf-8')
    xlsheet = workbook.add_sheet("技术点")

    row = 0
    for line in cnt:
        col = 0
        for cell in line:
            xlsheet.write(row, col, cell)
            col += 1
        row += 1

    workbook.save(PurePath(prepared_file).with_name(filename).with_suffix('.xls'))

# 取得总数
total_number = table.nrows
# 取得每一行,并用第二个单元格作为新的文件名
for line in range(1, total_number):
    content = table.row_values(rowx=line, start_colx=0, end_colx=None)
    # 将表头和内容重新组成一个新的文件
    new_content = []
    # 增加表头到要写入的内容中
    new_content.append(result_header)
    # 增加内容到要写入的内容中
    new_content.append(content)
    # 调用自定义函数write_to_file()写入新的文件
    write_to_file(filename = content[1], cnt = new_content)











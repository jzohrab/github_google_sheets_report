import pygsheets
gc = pygsheets.authorize()
sh = gc.open('my new ssheet')
wks = sh.sheet1
wks = sh.worksheet_by_title('raw_data')
wks.update_cells(crange='A2', values=[[1,2],[3,4],[5,6]])   # can sort the array in python before output
tel = {'jack': 4098, 'sape': 4139}
tel2 = {'sape': 2222, 'jack': 1111}
wks.update_cells(crange='A1', values=[['aeou','aoeubb']])
# wks.update_cells(crange='A1', values=[tel.keys()])
# wks.update_cells(crange='A1', values=[tel2.keys()])
# wks.update_cells(crange='A2', values=[tel.values(), tel2.values()])

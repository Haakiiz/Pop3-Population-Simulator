class Book():
    def __init__(self, navn, sidetall, sjanger):
        self.navn = navn
        self.sidetall = sidetall
        self.sjanger = sjanger

    def navnet_mitt(self):
        print(f'Boka heter {self.navn}, er {self.sidetall} sider lang og sjangeren er {self.sjanger}')


fivtyshades = Book(navn='FiftyShadesOfGray', sidetall=200, sjanger='kåt lektyre')
JamesCook = Book(navn='JamesCook', sidetall=250, sjanger='båt ting')




print(fivtyshades.navnet_mitt())
print(JamesCook.navnet_mitt())




# class Book():
#     def __init__(self, navn, sidetall, sjanger):
#         self.navn = navn
#         self.sidetall = sidetall
#         self.sjanger = sjanger
#
#     def navnet_mitt(self):
#         print(f'Boka heter {self.navn}, er {self.sidetall} sider lang og sjangeren er {self.sjanger}')
#
#
# fiftyshades = Book(navn='FiftyShadesOfGray', sidetall=200, sjanger='kåt lektyre')
#
# fiftyshades.navnet_mitt()
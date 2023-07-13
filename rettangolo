import pickle
class Rettangolo:
    def __init__(self, base, altezza):
        self.base = base
        self.altezza = altezza

    def __str__(self):
        return f"Base = {self.base},  Altezza = {self.altezza}\n"

    def ridimensiona(self, newbase, newaltezza):
        self.base = newbase
        self.altezza = newaltezza
        print("Ho aggiornato il rettangolo.\n")

    def perimetro(self):
        return (self.base + self.altezza)*2

    def area(self):
        return (self.base * self.altezza)

scelta = 0
cont = 0

rettangolo1 = Rettangolo(20, 10)
rettangolo2 = Rettangolo(10, 5)
rettangoli = []
perimetri = 0
aree = 0

rettangoli.append(rettangolo1)
rettangoli.append(rettangolo2)

rettangolo1.ridimensiona(15, 10)


while scelta != "5":
    scelta = input("\nCosa vuoi fare?\n"
                   "Premere\n"
                   "1 per stampare la somma dei perimetri\n"
                   "2 per stampare la somma delle aree\n"
                   "3 per per salvare la lista su un file\n"
                   "4 per leggere la lista su un file\n"
                   "5 per uscire dal programma: ")

    if scelta == "1":
        for el in rettangoli:
            perimetri += Rettangolo.perimetro(el)
        print(f"\nLa somma dei perimetri è: {perimetri}")

    elif scelta == "2":
        for el in rettangoli:
            aree += Rettangolo.area(el)
        print(f"\nLa somma delle aree è: {aree}")

    elif scelta == "3":
        elenco = open("rettangoli.pkl", "wb")
        pickle.dump(rettangoli, elenco)
        elenco.close()
        print("\nSalvataggio effettuato.")


    elif scelta == "4":
        elenco = open("rettangoli.pkl", "rb")
        unpickler = pickle.Unpickler(elenco)
        rettangoli = unpickler.load()
        print("\nEcco l'elenco dei rettangoli:\n")
        for riga in rettangoli:
            cont += 1
            print(f"Rettangolo {cont}: ")
            print(riga)
        elenco.close()

    elif scelta == "5":
        exit()

    else:
        print("Scelta non valida.")

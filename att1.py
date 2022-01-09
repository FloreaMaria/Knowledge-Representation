import time
from math import sqrt
import numpy as np
import copy
import os
import sys

sys.setrecursionlimit(1000000)


def is_escape(x, y, mat):
    """
    :param x: coordonata x
    :param y: coordonata y
    :param mat: matricea nodului curent
    :return: daca este iesire pentru soricel
    """
    if 0 < x < len(mat) and 0 < y < len(mat):
        return mat[x][y] == "E"


def is_hide(x, y, mat):
    """
     :param x: coordonata x
     :param y: coordonata y
     :param mat: matricea nodului curent
     :return: daca este ascunzatoare pentru soricel
     """
    if 0 < x < len(mat) and 0 < y < len(mat):
        return mat[x][y] == "@"


def is_empty(x, y, mat):
    """
     :param x: coordonata x
     :param y: coordonata y
     :param mat: matricea nodului curent
     :return: daca este pozitie libera in matrice
     """
    if 0 < x < len(mat) and 0 < y < len(mat):
        return mat[x][y] == "."


def is_ok_for_cat(x, y, mat):
    """
    :param x: coordonata x
    :param y: coordonata y
    :param mat: matricea nodului curent
    :return: daca este pozitie valabila pentru pisica
    """
    if 0 < x < len(mat) and 0 < y < len(mat):
        return mat[x][y] == "." or mat[x][y].startswith("s")


def is_ok_for_mouse(x, y, mat):
    """
       :param x: coordonata x
       :param y: coordonata y
       :param mat: matricea nodului curent
       :return: daca este pozitie valabila pentru soarece
       """
    if 0 <= x < len(mat) and 0 <= y < len(mat):
        return mat[x][y] == "." or mat[x][y] == "@" or mat[x][y] == "E"


def cartesian_product(*arrays):
    """
    :param arrays: vectori pentru pozitii soarece
    :return: produs cartezian intre vectori
    """
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)


def get_number_of_trapped_mice(mat):
    """
    :param mat: matricea nodului curent
    :return: numar de soareci care nu pot iesi oricum de la inceput
    """
    trapped = 0
    for i in range(1, len(mat) - 1):
        for j in range(1, len(mat[i]) - 1):
            if mat[i][j].startswith("s"):
                if (not is_ok_for_mouse(i - 1, j, mat)) and (not is_ok_for_mouse(i + 1, j, mat)) and (
                        not is_ok_for_mouse(i, j - 1, mat)) and (not is_ok_for_mouse(i, j + 1, mat)):
                    trapped += 1
    return trapped


def format_matrix_output(mat):
    """
    :param mat: matricea nodului curent
    :return: formatul cerut cu spatiere
    """
    matrice = ""
    for i in range(1, len(mat) - 1):
        line = ""
        for j in range(1, len(mat[i]) - 1):
            if mat[i][j].startswith("s") or mat[i][j].startswith("p") or mat[i][j].startswith("S"):
                id = int(mat[i][j][1:])
                if id < 10:
                    line += mat[i][j] + "  "
                else:
                    line += mat[i][j] + " "
            else:
                line += mat[i][j] + "   "
        matrice += line + "\n"
    return matrice


def check_input(mat):
    for i in range(1, len(mat) - 1):
        for j in range(1, len(mat[i]) - 1):
            if not mat[i][j].startswith("s") and not mat[i][j].startswith("p") and not mat[i][j].startswith("S") and \
                    mat[i][j] != "." and mat[i][j] != "@" and mat[i][j] != "#" and mat[i][j] != "E":
                return 0
    return 1


class NodParcurgere:
    graf = None  # static

    def __init__(self, id, info, parinte, cost, h):
        self.id = id  # este indicele din vectorul de noduri
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # costul de la radacina la nodul curent
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self.info]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte.info)
            nod = nod.parinte
        return l

    def afisDrum(self, file, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()

        for i, nod in enumerate(l):
            file.write(str(i) + ")\n")
            file.write(format_matrix_output(nod["matrice"]) + "\n")
            file.write("\n")
            for line in nod["lista_comm"]:
                file.write(str(line) + "\n")
            file.write("\n")

        if afisCost:
            file.write("Cost: " + str(self.g) + "\n")

        if afisLung:
            file.write(("Lungime: " + str(len(l)) + "\n"))

        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info["matrice"])
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):

        matrice = []
        f = open(nume_fisier, "r")
        try:
            k = int(f.readline())
        except:
            e = sys.exc_info()[0]
            k = -1
            print("<p>Error: %s</p>" % e)

        for line in f.readlines():
            line1 = " ".join(line.split())
            line1 = line1.split(" ")
            matrice.append(line1)

        comm_list = []
        line2 = []
        for i in range(len(matrice[0])):
            line2.append("1")

        matrice.insert(0, line2)
        matrice.insert(len(matrice), line2)

        for line in matrice:
            line.insert(0, "1")
            line.insert(len(line), "1")

        lista_soareci = []
        lista_pisici = []
        lista_E = []
        nr_soareci = 0
        nr_pisici = 0

        for i in range(1, len(matrice) - 1):
            for j in range(1, len(matrice[i]) - 1):
                if matrice[i][j].startswith("s"):
                    lista_soareci.append((int(matrice[i][j][1:]), (i, j)))
                    nr_soareci += 1
                elif matrice[i][j].startswith("p"):
                    nr_pisici += 1
                    lista_pisici.append((int(matrice[i][j][1:]), (i, j)))
                elif matrice[i][j] == "E":
                    lista_E.append((matrice[i][j], (i, j)))

        lista_soareci.sort(key=lambda x: x[0])
        lista_pisici.sort(key=lambda x: x[0])
        inf = {
            "matrice": matrice,
            "soareci": nr_soareci,
            "pisici": nr_pisici,
            "lista_soareci": lista_soareci,
            "lista_pisici": lista_pisici,
            "lista_E": lista_E,
            "lista_comm": comm_list,
            "soareci_salvati": 0
        }

        self.start = NodParcurgere(0, inf, None, 0, 0)
        self.k = k

    def testeaza_scop(self, nodCurent):
        return nodCurent.info["soareci_salvati"] >= self.k

    # va genera succesorii sub forma de noduri in arborele de parcurgere
    def generare_succesori(self, nodCurent, tip_euristica):

        mat1 = nodCurent.info["matrice"]
        if check_input(mat1) == 0:
            print("FORMATUL MATRICEI ESTE GRESIT")
            return
        if self.k == -1:
            print("K nu s-a citit")
            return
        nr_soareci = nodCurent.info["soareci"]
        nr_pisici = nodCurent.info["pisici"]
        lista_soareci = nodCurent.info["lista_soareci"]
        lista_pisici = nodCurent.info["lista_pisici"]
        cost = nodCurent.g

        lista_succ = []
        t = []

        lista_soareci.sort(key=lambda x: x[0])
        lista_pisici.sort(key=lambda x: x[0])

        if nr_soareci > 0:
            for i in range(nr_soareci):
                t.append(np.arange(4))

            c_product = cartesian_product(*t)
            for idx, line in enumerate(c_product):
                mat = []
                mat = copy.deepcopy(mat1)
                lista_soareci_noua = []
                lista_pisici_noua = []
                soareci_salvati = copy.deepcopy(nodCurent.info["soareci_salvati"])
                lista_new_comm = []
                new_cost = cost
                has_escaped = False
                was_catch = False

                for i in range(len(lista_soareci)):
                    # 0 = sus
                    if line[i] == 0:
                        if is_escape(lista_soareci[i][1][0] - 1, lista_soareci[i][1][1], mat):
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a salvat."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            has_escaped = True
                            soareci_salvati += 1

                        elif is_hide(lista_soareci[i][1][0] - 1, lista_soareci[i][1][1], mat):
                            mat[lista_soareci[i][1][0] - 1][lista_soareci[i][1][1]] = "S" + mat[lista_soareci[i][1][0]][
                                                                                                lista_soareci[i][1][1]][
                                                                                            1:]

                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a ascuns."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0] - 1, lista_soareci[i][1][1])))
                            new_cost += 1

                        elif is_empty(lista_soareci[i][1][0] - 1, lista_soareci[i][1][1], mat):
                            mat[lista_soareci[i][1][0] - 1][lista_soareci[i][1][1]] = mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " s-a mutat o pozitie in sus."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0] - 1, lista_soareci[i][1][1])))
                            new_cost += 1
                        else:
                            lista_soareci_noua.append(lista_soareci[i])
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " nu s-a mutat."
                            lista_new_comm.append(coment)

                    # 1 - dreapta
                    if line[i] == 1:
                        if is_escape(lista_soareci[i][1][0], lista_soareci[i][1][1] + 1, mat):
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a salvat."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            has_escaped = True
                            soareci_salvati += 1

                        elif is_hide(lista_soareci[i][1][0], lista_soareci[i][1][1] + 1, mat):
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1] + 1] = "S" + mat[lista_soareci[i][1][0]][
                                                                                                lista_soareci[i][1][1]][
                                                                                            1:]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a ascuns."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0], lista_soareci[i][1][1] + 1)))
                            new_cost += 1

                        elif is_empty(lista_soareci[i][1][0], lista_soareci[i][1][1] + 1, mat):
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1] + 1] = mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " s-a mutat o pozitie spre dreapta."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0], lista_soareci[i][1][1] + 1)))
                            new_cost += 1

                        else:
                            lista_soareci_noua.append(lista_soareci[i])
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " nu s-a mutat."
                            lista_new_comm.append(coment)

                    # 2 - jos
                    if line[i] == 2:

                        if is_escape(lista_soareci[i][1][0] + 1, lista_soareci[i][1][1], mat):
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a salvat."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            has_escaped = True
                            soareci_salvati += 1

                        elif is_hide(lista_soareci[i][1][0] + 1, lista_soareci[i][1][1], mat):
                            mat[lista_soareci[i][1][0] + 1][lista_soareci[i][1][1]] = "S" + mat[lista_soareci[i][1][0]][
                                                                                                lista_soareci[i][1][1]][
                                                                                            1:]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a ascuns."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0] + 1, lista_soareci[i][1][1])))
                            new_cost += 1

                        elif is_empty(lista_soareci[i][1][0] + 1, lista_soareci[i][1][1], mat):
                            mat[lista_soareci[i][1][0] + 1][lista_soareci[i][1][1]] = mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " a coborat o pozitie."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0] + 1, lista_soareci[i][1][1])))
                            new_cost += 1

                        else:
                            lista_soareci_noua.append(lista_soareci[i])
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " nu s-a mutat."
                            lista_new_comm.append(coment)

                    # 3 - stanga
                    if line[i] == 3:
                        if is_escape(lista_soareci[i][1][0], lista_soareci[i][1][1] - 1, mat):
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a salvat."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            has_escaped = True
                            soareci_salvati += 1

                        elif is_hide(lista_soareci[i][1][0], lista_soareci[i][1][1] - 1, mat):
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1] - 1] = "S" + mat[lista_soareci[i][1][0]][
                                                                                                lista_soareci[i][1][1]][
                                                                                            1:]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] + " s-a ascuns."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0], lista_soareci[i][1][1] - 1)))
                            new_cost += 1

                        elif is_empty(lista_soareci[i][1][0], lista_soareci[i][1][1] - 1, mat):
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1] - 1] = mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]]
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " s-a mutat o pozitie spre stanga."
                            lista_new_comm.append(coment)
                            mat[lista_soareci[i][1][0]][lista_soareci[i][1][1]] = "."
                            lista_soareci_noua.append(
                                (lista_soareci[i][0], (lista_soareci[i][1][0], lista_soareci[i][1][1] - 1)))
                            new_cost += 1

                        else:
                            lista_soareci_noua.append(lista_soareci[i])
                            coment = "Soarecele " + mat[lista_soareci[i][1][0]][
                                lista_soareci[i][1][1]] + " nu s-a mutat."
                            lista_new_comm.append(coment)

                for y, p in enumerate(lista_pisici):
                    dist_mini = 10000000

                    x1 = p[1][0]  # coordonate pisica
                    y1 = p[1][1]

                    xs, ys = 0, 0  # coordonatele celui mai apropiat soricel
                    index = 0
                    for k, m in enumerate(lista_soareci_noua):
                        x2 = m[1][0]
                        y2 = m[1][1]
                        dist = sqrt(abs((pow((y2 - y1), 2) + pow((x2 - x1), 2))))

                        if dist < dist_mini:
                            dist_mini = dist
                            xs = x2
                            ys = y2
                            index = k

                    if xs > x1:
                        if ys > y1:
                            if is_ok_for_cat(x1 + 1, y1 + 1, mat):

                                if x1 + 1 == xs and y1 + 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in diagonala dreapta jos."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1 + 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 += 1
                                y1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)


                            elif is_ok_for_cat(x1 + 1, y1, mat):
                                if x1 + 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in jos."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 + 1, mat):
                                if x1 == xs and y1 + 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre dreapta."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 + 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)

                        elif ys < y1:
                            if is_ok_for_cat(x1 + 1, y1 - 1, mat):
                                if x1 + 1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in diagonala stanga jos."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 += 1
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 - 1, mat):
                                if x1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre stanga."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1 + 1, y1, mat):
                                if x1 + 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in jos."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)

                        elif ys == y1:
                            if is_ok_for_cat(x1 + 1, y1, mat):
                                if x1 + 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in jos."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 + 1, mat):
                                if x1 == xs and y1 + 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre dreapta."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 + 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 - 1, mat):
                                if x1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre stanga."
                                    lista_new_comm.append(coment)

                                mat[x1 + 1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."

                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)

                    elif xs < x1:
                        if ys < y1:
                            if is_ok_for_cat(x1 - 1, y1 - 1, mat):
                                if x1 - 1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in diagonala stanga sus."
                                    lista_new_comm.append(coment)

                                mat[x1 - 1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 -= 1
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)


                            elif is_ok_for_cat(x1 - 1, y1, mat):
                                if x1 - 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in sus."
                                    lista_new_comm.append(coment)

                                mat[x1 - 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 - 1, mat):
                                if x1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre stanga."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)


                        elif ys > y1:
                            if is_ok_for_cat(x1 - 1, y1 + 1, mat):
                                if x1 - 1 == xs and y1 + 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in diagonala dreapta sus."
                                    lista_new_comm.append(coment)

                                mat[x1 - 1][y1 + 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 -= 1
                                y1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1 - 1, y1, mat):
                                if x1 - 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in sus."
                                    lista_new_comm.append(coment)

                                mat[x1 - 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)

                            elif is_ok_for_cat(x1, y1 + 1, mat):
                                if x1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre dreapta."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)


                        else:
                            if is_ok_for_cat(x1 - 1, y1, mat):
                                if x1 - 1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie in sus."
                                    lista_new_comm.append(coment)

                                mat[x1 - 1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                x1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)

                    else:
                        if ys < y1:
                            if is_ok_for_cat(x1, y1 - 1, mat):
                                if x1 == xs and y1 - 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre stanga."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 - 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 -= 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)


                        elif ys > y1:
                            if is_ok_for_cat(x1, y1 + 1, mat):
                                if x1 == xs and y1 + 1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " s-a mutat o pozitie spre dreapta."
                                    lista_new_comm.append(coment)

                                mat[x1][y1 + 1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                y1 += 1
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)
                        else:
                            if is_ok_for_cat(x1, y1, mat):
                                if x1 == xs and y1 == ys:
                                    lista_soareci_noua.remove(lista_soareci_noua[index])
                                    was_catch = True
                                    coment = "Pisica " + mat[x1][y1] + " a mancat soarecele " + mat[xs][ys] + "."
                                    lista_new_comm.append(coment)
                                else:
                                    coment = "Pisica " + mat[x1][y1] + " nu s-a mutat.."
                                    lista_new_comm.append(coment)

                                mat[x1][y1] = mat[x1][y1]
                                mat[x1][y1] = "."
                                p_new = (p[0], (x1, y1))
                                lista_pisici_noua.append(p_new)
                            else:
                                coment = "Pisica " + mat[x1][y1] + " nu s-a mutat."
                                lista_new_comm.append(coment)

                if was_catch and has_escaped == False:
                    new_cost = nr_soareci * nr_pisici
                # elif was_catch and has_escaped:
                #     new_cost = nr_soareci*nr_pisici

                elif has_escaped:
                    new_cost = cost + 1

                inf = {"matrice": mat,
                       "soareci": len(lista_soareci_noua),
                       "pisici": len(lista_pisici_noua),
                       "lista_soareci": lista_soareci_noua,
                       "lista_pisici": lista_pisici_noua,
                       "lista_E": nodCurent.info["lista_E"],
                       "lista_comm": lista_new_comm,
                       "soareci_salvati": soareci_salvati}

                nod_nou = NodParcurgere(idx, inf, nodCurent, new_cost, self.calculeaza_h(inf, tip_euristica))
                lista_succ.append(nod_nou)

        return lista_succ

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)

    def calculeaza_h(self, infoNod, tip_euristica):
        if tip_euristica == "euristica_banala":
            return self.euristica_banala(infoNod, tip_euristica)
        elif tip_euristica == "euristica_admisibila_1":
            return self.euristica_admisibila_1(infoNod, tip_euristica)
        elif tip_euristica == "euristica_admisibila_2":
            return self.euristica_admisibila_2(infoNod, tip_euristica)
        elif tip_euristica == "euristica_inadmisibila":
            return self.euristica_inadmisibila(infoNod, tip_euristica)
        else:
            raise Exception("Aceasta euristica nu este definita")

    def euristica_banala(self, infoNod, tip_euristica):
        return 0 if self.start.info["soareci"] - infoNod["soareci"] >= self.k else 1

    def euristica_admisibila_1(self, infoNod, tip_euristica):

        euristici = []
        lista_soricei = self.start.info["lista_soareci"]
        lista_E = infoNod["lista_E"]

        for s in lista_soricei:

            xs = s[1][0]
            ys = s[1][1]

            for e in lista_E:
                xe = e[1][0]
                ye = e[1][1]
                if xe == xs and ye == ye:
                    continue
                else:
                    dist = sqrt(abs((pow((ys - ye), 2) + pow((xs - xe), 2))))
                    euristici.append(dist)

        euristici.sort()
        return euristici[self.k - 1]

    def euristica_admisibila_2(self, infoNod, tip_euristica):

        euristici = []
        lista_soricei = self.start.info["lista_soareci"]
        lista_E = infoNod["lista_E"]

        for s in lista_soricei:

            xs = s[1][0]
            ys = s[1][1]

            for e in lista_E:
                xe = e[1][0]
                ye = e[1][1]
                if xs == xe and ys == ye:
                    continue
                else:
                    dist = abs(ys - ye) + abs(xs - xe)
                    euristici.append(dist)

        euristici.sort()
        return euristici[self.k - 1]

    def euristica_inadmisibila(self, infoNod, tip_euristica):
        return 800000 - self.euristica_admisibila_1(infoNod, tip_euristica)

    # def euristica_inadmisibila(self, infoNod, tip_euristica):
    #     euristici = []
    #     lista_soricei = infoNod["lista_soareci"]
    #     lista_E = infoNod["lista_E"]
    #
    #     if len(lista_soricei) > 0:
    #         for s in lista_soricei:
    #
    #             xs = s[1][0]
    #             ys = s[1][1]
    #
    #             for e in lista_E:
    #                 xe = e[1][0]
    #                 ye = e[1][1]
    #                 if xs == xe and ys == ye:
    #                     continue
    #                 else:
    #                     dist = abs(ys - ye) + abs(xs - xe)
    #                     euristici.append(dist)
    #
    #         euristici.sort(reverse=True)
    #         return max(euristici)
    #     return 100000


def a_star(gr, nrSolutiiCautate, tip_euristica, time_out, fisier_output):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [gr.start]
    nr_noduri_calculate = 1
    file = open(fisier_output, "w")

    # optimizare
    if c[0].info["soareci"] < gr.k:
        file.write("Nu avem destui soricei din start")
        return
    if c[0].info["soareci"] - get_number_of_trapped_mice(c[0].info["matrice"]) < gr.k:
        file.write("Desi sunt destui soricei, unii nu vor putea scapa niciodata")
        return
    t0 = time.time()

    while len(c) > 0:
        # print("Coada actuala: " + str(c))
        # input()

        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return

        nodCurent = c.pop(0)
        if gr.testeaza_scop(nodCurent):
            file.write("Solutie: \n")
            nodCurent.afisDrum(file, afisCost=True, afisLung=True)
            t3 = time.time()

            timp_gasire_solutie = round(1000 * (t3 - t0))
            file.write("Timp gasire solutie: " + str(timp_gasire_solutie) + "\n")
            file.write("Numar maxim noduri in memorie : " + str(len(c)) + "\n")
            file.write("Numar noduri generate : " + str(nr_noduri_calculate) + "\n")
            file.write("\n----------------\n")

            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.generare_succesori(nodCurent, tip_euristica)

        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return

        nr_noduri_calculate += len(lSuccesori)

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def a_star_optimizat(gr, tip_euristica, time_out, fisier_output):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [gr.start]
    file = open(fisier_output, "w")
    # optimizare
    if l_open[0].info["soareci"] < gr.k:
        file.write("Nu avem destui soricei din start")
        return
    if l_open[0].info["soareci"] - get_number_of_trapped_mice(l_open[0].info["matrice"]) < gr.k:
        file.write("Desi sunt destui soricei, unii nu vor putea scapa niciodata")
        return

    # l_open contine nodurile candidate pentru expandare
    # l_closed contine nodurile expandate
    l_closed = []
    nr_noduri_generate = 1

    t0 = time.time()

    while len(l_open) > 0:
        # print("Coada actuala: " + str(l_open))
        # input()
        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return

        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)
        if gr.testeaza_scop(nodCurent):
            file.write("Solutie: \n")
            nodCurent.afisDrum(file, afisCost=True, afisLung=True)
            t3 = time.time()

            timp_gasire_solutie = round(1000 * (t3 - t0))
            file.write("Timp gasire solutie: " + str(timp_gasire_solutie) + "\n")
            file.write("Numar maxim noduri in memorie : " + str(len(l_open)) + "\n")
            file.write("Numar noduri generate : " + str(nr_noduri_generate) + "\n")
            file.write("\n----------------\n")
            return

        lSuccesori = gr.generare_succesori(nodCurent, tip_euristica)
        nr_noduri_generate += len(lSuccesori)

        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return

        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)


def uniform_cost(gr, nrSolutiiCautate, tip_euristica, time_out, fisier_output):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [gr.start]

    continua = True  # variabila pe care o setez la false cand consider ca s-au afisat suficiente solutii
    nr_noduri_calculate = 1
    file = open(fisier_output, "w")
    # optimizare
    if c[0].info["soareci"] < gr.k:
        file.write("Nu avem destui soricei din start")
        return
    if c[0].info["soareci"] - get_number_of_trapped_mice(c[0].info["matrice"]) < gr.k:
        file.write("Desi sunt destui soricei, unii nu vor putea scapa niciodata")
        return

    t0 = time.time()
    while (len(c) > 0 and continua):
        # print("Coada actuala: " + str(c))
        # input()
        nodCurent = c.pop(0)
        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return
        if gr.testeaza_scop(nodCurent):
            file.write("Solutie: \n")
            nodCurent.afisDrum(file, afisCost=True, afisLung=True)
            t3 = time.time()

            timp_gasire_solutie = round(1000 * (t3 - t0))
            file.write("Timp gasire solutie: " + str(timp_gasire_solutie) + "\n")
            file.write("Numar maxim noduri in memorie : " + str(len(c)) + "\n")
            file.write("Numar noduri generate : " + str(nr_noduri_calculate) + "\n")
            file.write("\n----------------\n")

            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                continua = False

        lSuccesori = gr.generare_succesori(nodCurent, tip_euristica)

        nr_noduri_calculate += len(lSuccesori)

        if time.time() - t0 > time_out:
            file.write("S-a depasit time out-ul\n")
            return

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta e ca ordonez dupa g
                if c[i].g >= s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, tip_euristica, file, t0, time_out, nr_noduri,
                      noduri_in_memorie):
    # file.write("A ajuns la: " + str(nodCurent))
    nr_noduri += 1
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f

    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:

        file.write("Solutie: \n")
        nodCurent.afisDrum(file, afisCost=True, afisLung=True)

        t3 = time.time()
        timp_gasire_solutie = round(1000 * (t3 - t0))
        file.write("Timp gasire solutie: " + str(timp_gasire_solutie) + "\n")
        file.write("Numar maxim noduri in memorie : " + str(noduri_in_memorie) + "\n")
        file.write("Numar noduri generate : " + str(nr_noduri) + "\n")
        file.write("\n----------------\n")

        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return 0, "gata"

    lSuccesori = gr.generare_succesori(nodCurent, tip_euristica)
    noduri_in_memorie += len(lSuccesori)
    nr_noduri += len(lSuccesori)

    if time.time() - t0 > time_out:
        file.write("S-a depasit time out-ul\n")
        return 0, "timeout"

    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, tip_euristica, file, t0, time_out,
                                                  nr_noduri, noduri_in_memorie)
        nr_noduri += 1
        if rez == "gata":
            return 0, "gata"
        if rez == "timeout":
            return 0, "timeout"
        # file.write("Compara "+ str(rez)+ " cu " + str(minim))
        if rez < minim:
            minim = rez
            # file.write("Noul minim: " + str(minim))
    return nrSolutiiCautate, minim


def ida_star(gr, nrSolutiiCautate, tip_euristica, time_out, fisier_output):
    nodStart = gr.start
    limita = nodStart.f
    file = open(fisier_output, "w")
    nr_noduri = 1
    noduri_in_memorie = 0

    # optimizare
    if nodStart.info["soareci"] < gr.k:
        file.write("Nu avem destui soricei din start")
        return
    if nodStart.info["soareci"] - get_number_of_trapped_mice(nodStart.info["matrice"]) < gr.k:
        file.write("Desi sunt destui soricei, unii nu vor putea scapa niciodata")
        return

    t0 = time.time()
    while True:
        # file.write("Limita de pornire: "+ str(limita))
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, tip_euristica, file, t0,
                                                  time_out, nr_noduri, noduri_in_memorie)
        if rez == "gata":
            break
        if rez == float('inf'):
            # file.write("Nu exista solutii!")
            break
        if rez == "timeout":
            return
        limita = rez
        # file.write(">>> Limita noua: " + str(limita))


def citire():
    print("Introdu numele folderului cu fisierele de input")
    input_directory = input()

    print("Introdu numarul de solutii de calculat")
    nr_sol = int(input())

    print("Introdu valoare pentru timeout in secunde")
    time_out = int(input())

    euristici = ["euristica_banala", "euristica_admisibila_1", "euristica_admisibila_2", "euristica_inadmisibila"]

    output_directory = "C:/Users/Maria/PycharmProjects/temaKR/output_directory"

    # in = C:/Users/Maria/PycharmProjects/temaKR/input_directory

    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".txt"):
            gr = Graph(input_directory + "/" + filename)
            output = output_directory + "/"
            if filename == "input_bun.txt":
                output += "output_bun"
            elif filename == "input_fara_solutii.txt":
                output += "output_fara_solutii"
            elif filename == "input_timeout.txt":
                output += "output_timeout"
            else:

                output += "alt_output.txt"

            for e in euristici:
                m = copy.deepcopy(e)

                # filename_ufc = output + "_" + m + "_ufc.txt"
                # uniform_cost(gr, nr_sol, e, time_out, filename_ufc)

                # filename_a_star = output + "_" + m + "_a_star.txt"
                # a_star(gr, nr_sol, e, time_out, filename_a_star)
                #

                filename_a_star_optimizat = output + "_" + m + "_a_star_optimizat.txt"
                a_star_optimizat(gr, e, time_out, filename_a_star_optimizat)
                #
                # filename_ida_star = output + "_" + m + "_ida_star11.txt"
                # ida_star(gr, nr_sol, e, time_out, filename_ida_star)


citire()

# 0 - st
# 1 - dr
# 2 - jos
# 3 - sus

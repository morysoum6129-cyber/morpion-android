from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
import random

JAUNE = (1, 0.85, 0, 1)
NOIR = (0.08, 0.08, 0.08, 1)
BLEU_CIEL = (0.4, 0.75, 1, 1)
FOND_SOMBRE = (0.05, 0.05, 0.05, 1)
VERT = (0.3, 0.8, 0.3, 1)
BLANC_VICTOIRE = (1, 1, 1, 1)

COMBINAISONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


class EcranFond(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*FOND_SOMBRE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class BoutonStyle(Button):
    def __init__(self, couleur=JAUNE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = NOIR if couleur == JAUNE else (1, 1, 1, 1)
        self.bold = True
        self.couleur_fond = couleur
        with self.canvas.before:
            self.color_instr = Color(*self.couleur_fond)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[12])
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def changer_couleur(self, couleur):
        self.couleur_fond = couleur
        self.color_instr.rgba = couleur


class MenuScreen(EcranFond):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        layout.add_widget(Label(text="Morpion", font_size='32sp', bold=True,
                                 color=JAUNE, size_hint=(1, 0.3)))

        btn_2j = BoutonStyle(text="2 joueurs", couleur=JAUNE, font_size='20sp')
        btn_2j.bind(on_press=lambda b: self.demarrer_2joueurs())
        layout.add_widget(btn_2j)

        btn_ia = BoutonStyle(text="Contre l'ordinateur", couleur=BLEU_CIEL, font_size='20sp')
        btn_ia.bind(on_press=lambda b: setattr(self.manager, 'current', 'difficulte'))
        layout.add_widget(btn_ia)

        self.add_widget(layout)

    def demarrer_2joueurs(self):
        jeu = self.manager.get_screen('jeu')
        jeu.demarrer("2joueurs", None, reset_scores=True)
        self.manager.current = 'jeu'


class DifficulteScreen(EcranFond):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        layout.add_widget(Label(text="Difficulté", font_size='26sp', bold=True,
                                 color=JAUNE, size_hint=(1, 0.25)))

        btn_facile = BoutonStyle(text="Facile", couleur=JAUNE, font_size='18sp')
        btn_facile.bind(on_press=lambda b: self.demarrer("facile"))
        layout.add_widget(btn_facile)

        btn_difficile = BoutonStyle(text="Difficile (imbattable)", couleur=BLEU_CIEL, font_size='18sp')
        btn_difficile.bind(on_press=lambda b: self.demarrer("difficile"))
        layout.add_widget(btn_difficile)

        btn_retour = BoutonStyle(text="Retour", couleur=JAUNE, font_size='16sp', size_hint=(1, 0.2))
        btn_retour.bind(on_press=lambda b: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_retour)

        self.add_widget(layout)

    def demarrer(self, difficulte):
        jeu = self.manager.get_screen('jeu')
        jeu.demarrer("ordinateur", difficulte, reset_scores=True)
        self.manager.current = 'jeu'


class JeuScreen(EcranFond):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "2joueurs"
        self.difficulte = None
        self.joueur_actuel = "X"
        self.plateau = [""] * 9
        self.partie_finie = False
        self.scores = {"X": 0, "O": 0, "Nul": 0}

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.label_tour = Label(text="Tour du joueur : X", font_size='22sp',
                                 bold=True, color=JAUNE, size_hint=(1, 0.1))
        self.layout.add_widget(self.label_tour)

        self.label_score = Label(text="", font_size='16sp',
                                  color=BLEU_CIEL, size_hint=(1, 0.08))
        self.layout.add_widget(self.label_score)

        self.grille = GridLayout(cols=3, spacing=8, size_hint=(1, 0.56))
        self.cases = []
        for i in range(9):
            btn = BoutonStyle(text="", couleur=JAUNE, font_size='40sp')
            btn.bind(on_press=lambda b, i=i: self.jouer(i))
            self.cases.append(btn)
            self.grille.add_widget(btn)
        self.layout.add_widget(self.grille)

        ligne_boutons = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.13))
        self.btn_rejouer = BoutonStyle(text="Rejouer", couleur=BLEU_CIEL, font_size='16sp')
        self.btn_rejouer.bind(on_press=lambda b: self.demarrer(self.mode, self.difficulte, reset_scores=False))
        ligne_boutons.add_widget(self.btn_rejouer)

        self.btn_menu = BoutonStyle(text="Menu", couleur=JAUNE, font_size='16sp')
        self.btn_menu.bind(on_press=lambda b: setattr(self.manager, 'current', 'menu'))
        ligne_boutons.add_widget(self.btn_menu)
        self.layout.add_widget(ligne_boutons)

        self.add_widget(self.layout)

    def demarrer(self, mode, difficulte, reset_scores=True):
        self.mode = mode
        self.difficulte = difficulte
        self.joueur_actuel = "X"
        self.plateau = [""] * 9
        self.partie_finie = False
        if reset_scores:
            self.scores = {"X": 0, "O": 0, "Nul": 0}
        self.label_tour.text = "Tour du joueur : X"
        self.mettre_a_jour_score()
        for case in self.cases:
            case.text = ""
            case.changer_couleur(JAUNE)

    def mettre_a_jour_score(self):
        nom_o = "Ordinateur" if self.mode == "ordinateur" else "O"
        self.label_score.text = (
            f"Score - X: {self.scores['X']}  |  "
            f"{nom_o}: {self.scores['O']}  |  Nul: {self.scores['Nul']}"
        )

    def jouer(self, i):
        if self.partie_finie or self.plateau[i] != "":
            return
        if self.mode == "ordinateur" and self.joueur_actuel == "O":
            return

        self.poser(i, self.joueur_actuel)

        if not self.partie_finie and self.mode == "ordinateur" and self.joueur_actuel == "O":
            Clock.schedule_once(lambda dt: self.tour_ia(), 0.4)

    def poser(self, i, joueur):
        self.plateau[i] = joueur
        self.cases[i].text = joueur
        self.cases[i].changer_couleur(VERT if joueur == "X" else BLEU_CIEL)

        combo_gagnante = self.trouver_combo_gagnante()
        if combo_gagnante:
            gagnant = self.plateau[combo_gagnante[0]]
            self.scores[gagnant] += 1
            texte = f"Le joueur {gagnant} a gagné !"
            if self.mode == "ordinateur" and gagnant == "O":
                texte = "L'ordinateur a gagné !"
            self.label_tour.text = texte
            self.partie_finie = True
            for idx in combo_gagnante:
                self.cases[idx].changer_couleur(BLANC_VICTOIRE)
            self.mettre_a_jour_score()
        elif "" not in self.plateau:
            self.scores["Nul"] += 1
            self.label_tour.text = "Match nul !"
            self.partie_finie = True
            self.mettre_a_jour_score()
        else:
            self.joueur_actuel = "O" if self.joueur_actuel == "X" else "X"
            self.label_tour.text = f"Tour du joueur : {self.joueur_actuel}"

    def tour_ia(self):
        if self.partie_finie:
            return
        if self.difficulte == "facile":
            coup = self.coup_aleatoire_intelligent()
        else:
            coup = self.meilleur_coup_minimax()
        if coup is not None:
            self.poser(coup, "O")

    def coup_aleatoire_intelligent(self):
        cases_libres = [i for i in range(9) if self.plateau[i] == ""]
        for i in cases_libres:
            self.plateau[i] = "O"
            if self.verifier_victoire() == "O":
                self.plateau[i] = ""
                return i
            self.plateau[i] = ""
        if random.random() < 0.5:
            for i in cases_libres:
                self.plateau[i] = "X"
                if self.verifier_victoire() == "X":
                    self.plateau[i] = ""
                    return i
                self.plateau[i] = ""
        return random.choice(cases_libres) if cases_libres else None

    def meilleur_coup_minimax(self):
        meilleur_score = -float('inf')
        meilleur_coup = None
        for i in range(9):
            if self.plateau[i] == "":
                self.plateau[i] = "O"
                score = self.minimax(0, False)
                self.plateau[i] = ""
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_coup = i
        return meilleur_coup

    def minimax(self, profondeur, tour_ia):
        resultat = self.verifier_victoire()
        if resultat == "O":
            return 10 - profondeur
        elif resultat == "X":
            return profondeur - 10
        elif "" not in self.plateau:
            return 0

        if tour_ia:
            meilleur = -float('inf')
            for i in range(9):
                if self.plateau[i] == "":
                    self.plateau[i] = "O"
                    meilleur = max(meilleur, self.minimax(profondeur + 1, False))
                    self.plateau[i] = ""
            return meilleur
        else:
            pire = float('inf')
            for i in range(9):
                if self.plateau[i] == "":
                    self.plateau[i] = "X"
                    pire = min(pire, self.minimax(profondeur + 1, True))
                    self.plateau[i] = ""
            return pire

    def verifier_victoire(self):
        for a, b, c in COMBINAISONS:
            if self.plateau[a] != "" and self.plateau[a] == self.plateau[b] == self.plateau[c]:
                return self.plateau[a]
        return None

    def trouver_combo_gagnante(self):
        for a, b, c in COMBINAISONS:
            if self.plateau[a] != "" and self.plateau[a] == self.plateau[b] == self.plateau[c]:
                return (a, b, c)
        return None


class MorpionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DifficulteScreen(name='difficulte'))
        sm.add_widget(JeuScreen(name='jeu'))
        return sm


if __name__ == '__main__':
    MorpionApp().run()

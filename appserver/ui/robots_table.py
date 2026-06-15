from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from server.registry import registry


# tableau des robots, rafraichi periodiquement depuis le registre
class RobotsTable(QTableWidget):
    HEADERS = ["Rang", "RID", "Score", "Pas", "Etat"]

    def __init__(self):
        super().__init__()
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def refresh(self):
        robots = registry.all()
        robots.sort(key=lambda r: r["score"], reverse=True)  # classement par score
        self.setRowCount(len(robots))
        for row, robot in enumerate(robots):
            required = robot["nb_steps_required"] if robot["nb_steps_required"] is not None else "?"
            steps = f"{robot['nb_steps_done']}/{required}"
            dot = "●" if robot["active"] else "○"  # plein = connecte, vide = parti
            state = f"{dot} {robot['state']}"
            self.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.setItem(row, 1, QTableWidgetItem(robot["rid"]))
            self.setItem(row, 2, QTableWidgetItem(str(robot["score"])))
            self.setItem(row, 3, QTableWidgetItem(steps))
            self.setItem(row, 4, QTableWidgetItem(state))

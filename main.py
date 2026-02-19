from toric_simulator import ToricSimulator
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt, QElapsedTimer

from qt import MyWindow

class GameController:
    def __init__(self, window):
        self.window = window
        self.keys = set()
        self.speed = 5

        self.timer = QElapsedTimer()
        self.timer.start()

        self.last_time = self.timer.elapsed()  # ms

        #toric
        self.L = 5
        self.error_rate = 0.01
        self.error_steps = 5 #this is done to avoid rounding errors
        self.toric = ToricSimulator(self.L)
        self.toric.add_error(self.error_rate*self.error_steps)
        self.toric.get_syndromes()
        self.window.set_toric(self.toric)

        #controlling simulation
        self.should_run = False
        self.should_peel = False

        #button control
        self.is_pressed = False

    def key_press(self, key):
        self.keys.add(key)

    def key_release(self, key):
        self.keys.discard(key)

    def update(self):
        current_time = self.timer.elapsed()
        delta_ms = current_time - self.last_time
        self.last_time = current_time

        delta_time = delta_ms / 1000.0  # seconds

        updated = False
        self.should_run = False
        self.should_peel = False
        if not self.is_pressed:
            if Qt.Key.Key_W in self.keys:
                self.is_pressed = True
                updated = True
                self.L += 1
            if Qt.Key.Key_S in self.keys:
                self.is_pressed = True
                if (self.L > 3):
                    updated = True
                    self.L -= 1
            
            if Qt.Key.Key_A in self.keys:
                updated = True
                self.error_steps += 1
                self.is_pressed = True
            if Qt.Key.Key_D in self.keys:
                self.is_pressed = True
                if (self.error_steps >= 1):
                    updated = True
                    self.error_steps -= 1
            
            if Qt.Key.Key_T in self.keys:
                self.is_pressed = True
                self.should_run = True
            
            if Qt.Key.Key_F in self.keys:
                self.is_pressed = True
                self.should_peel = True
            
        else:
            keys = [Qt.Key.Key_W, Qt.Key.Key_S, Qt.Key.Key_T, Qt.Key.Key_F, Qt.Key.Key_A, Qt.Key.Key_D]
            self.is_pressed = False
            for x in keys:
                if x in self.keys:
                    self.is_pressed = True

        
        if (updated):
            self.toric = ToricSimulator(self.L)
            self.toric.add_error(self.error_rate * self.error_steps)
            self.toric.get_syndromes()
            self.window.set_toric(self.toric)

        #print(self.should_run)
        if self.should_run and self.toric.has_odd():
            self.toric.iterate()
        
        if self.should_peel and not self.toric.has_odd():
            self.toric.peel()

        
        self.window.set_toric(self.toric)

        self.window.update()

def main():
    app = QApplication(sys.argv)

    window = MyWindow()
    window.setWindowTitle("ToricSimulator")
    window.setGeometry(100, 100, 960, 540)
    window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    window.show()

    controller = GameController(window)

    # Inject input handlers
    window.keyPressEvent = lambda e: controller.key_press(e.key())
    window.keyReleaseEvent = lambda e: controller.key_release(e.key())

    # Main loop
    timer = QTimer()
    timer.timeout.connect(controller.update)
    timer.start(16)  # ~60 FPS

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
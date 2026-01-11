import tkinter as tk
from tkinter import ttk

SERVO_COUNT = 4

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Arturio - Control Panel")
        self.root.geometry("520x260")

        self.connected = False

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        self.status_var = tk.StringVar(value="Nincs csatlakozva")
        ttk.Label(top, textvariable=self.status_var).pack(side="left")

        ttk.Button(top, text="Connect", command=self.connect).pack(side="right", padx=6)
        ttk.Button(top, text="Disconnect", command=self.disconnect).pack(side="right")

        body = ttk.Frame(root, padding=10)
        body.pack(fill="both", expand=True)

        self.angle_vars = []

        for i in range(SERVO_COUNT):
            row = ttk.Frame(body)
            row.pack(fill="x", pady=6)

            ttk.Label(row, text=f"Servo {i}", width=10).pack(side="left")

            var = tk.IntVar(value=90)
            self.angle_vars.append(var)

            value_label = ttk.Label(row, text="90", width=4)
            value_label.pack(side="right")

            slider = ttk.Scale(row, from_=0, to=180, orient="horizontal")
            slider.pack(side="left", fill="x", expand=True, padx=10)

            # callback: közvetlenül a labelt frissítjük, nincs lista index
            def make_cb(servo_idx: int, v: tk.IntVar, lbl: ttk.Label):
                def cb(val: str):
                    angle = int(float(val))
                    v.set(angle)
                    lbl.config(text=str(angle))

                    if self.connected:
                        print(f"[DEMO] would send: S{servo_idx}:{angle}")
                return cb

            slider.configure(command=make_cb(i, var, value_label))
            slider.set(90)

        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Send all", command=self.send_all).pack(side="right")

    def connect(self):
        self.connected = True
        self.status_var.set("CSATLAKOZVA (demo)")

    def disconnect(self):
        self.connected = False
        self.status_var.set("Nincs csatlakozva")

    def send_all(self):
        if not self.connected:
            print("[DEMO] not connected")
            return
        for i, var in enumerate(self.angle_vars):
            angle = var.get()
            print(f"[DEMO] would send: S{i}:{angle}")

def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
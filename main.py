import tkinter as tk
from tkinter import ttk, messagebox

import serial
import serial.tools.list_ports

SERVO_COUNT = 6
BAUD = 115200

def list_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Arturito - Control Panel")
        self.root.geometry("720x360")

        self.ser: serial.Serial | None = None


        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Port:").pack(side="left")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top, textvariable=self.port_var, width=28, values=list_ports())
        self.port_combo.pack(side="left", padx=6)

        ttk.Button(top, text="Refresh", command=self.refresh_ports).pack(side="left", padx=6)
        ttk.Button(top, text="Connect", command=self.connect).pack(side="right", padx=6)
        ttk.Button(top, text="Disconnect", command=self.disconnect).pack(side="right", padx=6)

        self.status_var = tk.StringVar(value="Nincs csatlakozva")
        ttk.Label(root, textvariable=self.status_var, padding=(10,0)).pack(fill="x")


        body = ttk.Frame(root, padding=10)
        body.pack(fill="both", expand=True)

        self.angle_vars: list[tk.IntVar] = []

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

                    #ez itt realtime küldés ha csatlakozva vagyunk
                    self.send_command(servo_idx, angle)
                return cb

            slider.configure(command=make_cb(i, var, value_label))
            slider.set(90)

        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Send all", command=self.send_all).pack(side="right")


    ## serial helpers
    @property
    def connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def refresh_ports(self) -> None:
        ports = list_ports()
        self.port_combo["values"] = ports
        if ports and (self.port_var.get() not in ports):
            self.port_var.set(ports[0])

    def connect(self):
        ports = list_ports()
        if not ports:
            messagebox.showerror("Hiba", "Nem találtam soros portot. Be van dugva az Arduino?")
            return

        port = self.port_var.get() or ports[0]
        self.port_var.set(port)

        try:
            self.ser = serial.Serial(port, BAUD, timeout=0.1)
            self.status_var.set(f"Csatlakozva: {port} @ {BAUD}")
        except Exception as e:
            self.ser = None
            messagebox.showerror("Hiba", f"Nem sikerült csatlakozni:\n{e}")
            return

        # Arduino gyakran resetel connectkor → kezdjük el olvasni a READY/OK sorokat
        self.root.after(200, self.poll_serial)

    def disconnect(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.status_var.set("Nincs csatlakozva")

    def send_command(self, servo_idx: int, angle: int):
        if not self.connected:
            return
        angle = max(0, min(180, int(angle)))
        msg = f"S{servo_idx}:{angle}\n".encode("utf-8")
        try:
            self.ser.write(msg)
        except Exception as e:
            self.status_var.set(f"Küldési hiba: {e}")

    def send_all(self):
        if not self.connected:
            self.status_var.set("Nem vagy csatlakozva")
            return
        for i, var in enumerate(self.angle_vars):
            self.send_command(i, var.get())

    def poll_serial(self):
        """Időnként olvasunk az Arduinóról, és kiírjuk a státuszba."""
        if not self.connected:
            return

        try:
            # olvassunk be minden teljes sort, ami érkezett
            while self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    # pl: READY vagy OK S2 120
                    self.status_var.set(line)
        except Exception as e:
            self.status_var.set(f"Olvasási hiba: {e}")

        self.root.after(100, self.poll_serial)


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
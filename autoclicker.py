import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import threading
import pyautogui
import keyboard
import time
import json
import os

SCENARIO_FILE = 'scenarios.json'

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Auto Clicker")
        window_width = 450
        window_height = 550
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.running = False
        self.thread = None
        self.recording = False
        self.recorded_scenario = []
        self.scenarios = {}
        self.widgets = []
        # Persistent filter variables
        self.type_filter_smart = tk.BooleanVar(value=True)
        self.type_filter_simple = tk.BooleanVar(value=True)
        # Register hotkey
        keyboard.add_hotkey('F8', self.stop_clicking)
        # Only check if scenarios exist, don't load them yet
        scenarios_exist = False
        if os.path.exists(SCENARIO_FILE):
            try:
                with open(SCENARIO_FILE, 'r') as f:
                    loaded = json.load(f)
                    if loaded:
                        scenarios_exist = True
            except Exception:
                pass
        if not scenarios_exist:
            self.show_welcome_screen()
        else:
            self.show_main_interface(load_scenarios=True)

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings dialog (to be implemented)")

    def clear_widgets(self):
        for w in self.widgets:
            w.destroy()
        self.widgets = []

    def show_welcome_screen(self):
        self.clear_widgets()
        title = tk.Label(self.master, text="Scenarios", font=("Arial", 24, "bold"))
        title.pack(pady=(40, 10))
        self.widgets.append(title)

        canvas = tk.Canvas(self.master, width=200, height=150, bg=self.master.cget('bg'), highlightthickness=0)
        canvas.create_rectangle(50, 80, 150, 140, fill="#f5f5f5", outline="#bbb", width=2)
        canvas.create_polygon(50, 80, 100, 40, 150, 80, 100, 120, fill="#fff", outline="#bbb", width=2)
        canvas.pack(pady=10)
        self.widgets.append(canvas)

        subtitle = tk.Label(self.master, text="Create your first scenario and\nstart automatizing tasks on your PC", font=("Arial", 14), justify="center")
        subtitle.pack(pady=20)
        self.widgets.append(subtitle)

        create_btn = tk.Button(self.master, text="Create a scenario", font=("Arial", 14, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", padx=20, pady=10, command=self.create_first_scenario)
        create_btn.pack(pady=30, ipadx=10, ipady=5)
        self.widgets.append(create_btn)

    def show_new_scenario_interface(self):
        self.clear_widgets()
        # Top bar
        topbar = tk.Frame(self.master)
        topbar.pack(fill=tk.X, pady=(5, 0))
        close_btn = tk.Button(topbar, text="✕", font=("Arial", 16), bd=0, command=self.show_main_interface, cursor="hand2")
        close_btn.pack(side=tk.LEFT, padx=10)
        title = tk.Label(topbar, text="New scenario", font=("Arial", 18, "bold"))
        title.pack(side=tk.LEFT, padx=10)
        save_btn = tk.Button(topbar, text="💾", font=("Arial", 16), bd=0, command=self.save_new_scenario, cursor="hand2")
        save_btn.pack(side=tk.RIGHT, padx=10)
        self.widgets.extend([topbar, close_btn, title, save_btn])

        # Scenario name
        name_label = tk.Label(self.master, text="Scenario name", font=("Arial", 12))
        name_label.pack(pady=(30, 0))
        name_entry = tk.Entry(self.master, font=("Arial", 14))
        name_entry.insert(0, "Default name")
        name_entry.pack(pady=(0, 20), ipadx=10, ipady=5)
        self.new_scenario_name_entry = name_entry
        self.widgets.extend([name_label, name_entry])

        # Scenario type selection
        type_frame = tk.Frame(self.master, bg="#f3f7fa", bd=1, relief=tk.FLAT)
        type_frame.pack(pady=10, padx=20, fill=tk.X)
        type_label = tk.Label(type_frame, text="Scenario type", font=("Arial", 12, "bold"), bg="#f3f7fa")
        type_label.pack(anchor="w", padx=10, pady=(10, 0))
        btn_frame = tk.Frame(type_frame, bg="#f3f7fa")
        btn_frame.pack(pady=10, padx=10, fill=tk.X)
        self.scenario_type_var = tk.StringVar(value="Simple")
        self.simple_btn = tk.Button(btn_frame, text=self.get_scenario_btn_text("Simple"), font=("Arial", 12), width=12, padx=10, pady=10, relief=tk.RAISED, command=lambda: self.select_scenario_type("Simple"))
        self.smart_btn = tk.Button(btn_frame, text=self.get_scenario_btn_text("Smart"), font=("Arial", 12), width=12, padx=10, pady=10, relief=tk.RAISED, command=lambda: self.select_scenario_type("Smart"))
        self.simple_btn.pack(side=tk.LEFT, padx=10)
        self.smart_btn.pack(side=tk.LEFT, padx=10)
        desc_label = tk.Label(type_frame, text="The regular auto clicker experience.\nSimply place clicks and swipes on the screen.", font=("Arial", 10), bg="#f3f7fa")
        desc_label.pack(pady=(0, 10))
        self.widgets.extend([type_frame, type_label, btn_frame, self.simple_btn, self.smart_btn, desc_label])

    def get_scenario_btn_text(self, typ):
        if typ == "Simple":
            icon = "✖️➔"  # You can use a better icon if you want
        else:
            icon = "🖼️"
        selected = self.scenario_type_var.get() == typ
        check = " ✔️" if selected else ""
        return f"{icon}  {typ}{check}"

    def select_scenario_type(self, typ):
        self.scenario_type_var.set(typ)
        self.simple_btn.config(text=self.get_scenario_btn_text("Simple"))
        self.smart_btn.config(text=self.get_scenario_btn_text("Smart"))

    def create_first_scenario(self):
        self.clear_widgets()
        self.show_new_scenario_interface()

    def save_new_scenario(self):
        name = self.new_scenario_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Scenario name cannot be empty.")
            return
        typ = self.scenario_type_var.get()
        self.scenarios[name] = {'steps': [], 'description': '', 'type': typ}
        self.save_scenarios()
        self.show_main_interface()

    def show_main_interface(self, load_scenarios=True):
        self.clear_widgets()
        # Top bar
        topbar = tk.Frame(self.master)
        topbar.pack(fill=tk.X, pady=(5, 0))
        title = tk.Label(topbar, text="Scenarios", font=("Arial", 22, "bold"))
        title.pack(side=tk.LEFT, padx=(20, 0))
        folder_btn = tk.Button(topbar, text="📁", font=("Arial", 16), bd=0, command=self.import_scenarios, cursor="hand2")
        folder_btn.pack(side=tk.RIGHT, padx=5)
        search_btn = tk.Button(topbar, text="🔍", font=("Arial", 16), bd=0, command=self.search_scenarios, cursor="hand2")
        search_btn.pack(side=tk.RIGHT, padx=5)
        settings_btn = tk.Button(topbar, text="⚙️", font=("Arial", 16), bd=0, command=self.open_settings, cursor="hand2")
        settings_btn.pack(side=tk.RIGHT, padx=5)
        self.widgets.extend([topbar, title, folder_btn, search_btn, settings_btn])

        # Filter/sort bar
        filter_frame = tk.Frame(self.master, bg="#eaf2fa")
        filter_frame.pack(pady=(10, 0), padx=10, fill=tk.X)
        self.filter_var = tk.StringVar(value="Name")
        name_btn = tk.Radiobutton(filter_frame, text="A Z Name", variable=self.filter_var, value="Name", font=("Arial", 12), indicatoron=0, width=10, padx=10, pady=8, bg="#eaf2fa", selectcolor="#d0e6fa")
        recent_btn = tk.Radiobutton(filter_frame, text="⏲ Recent", variable=self.filter_var, value="Recent", font=("Arial", 12), indicatoron=0, width=10, padx=10, pady=8, bg="#eaf2fa", selectcolor="#d0e6fa")
        fav_btn = tk.Radiobutton(filter_frame, text="☆ Favorite", variable=self.filter_var, value="Favorite", font=("Arial", 12), indicatoron=0, width=10, padx=10, pady=8, bg="#eaf2fa", selectcolor="#d0e6fa")
        name_btn.pack(side=tk.LEFT, padx=(5, 0))
        recent_btn.pack(side=tk.LEFT)
        fav_btn.pack(side=tk.LEFT)
        self.widgets.extend([filter_frame, name_btn, recent_btn, fav_btn])

        # Scenario type filter (Checkbuttons, persistent variables)
        type_filter_frame = tk.Frame(self.master, bg="#eaf2fa")
        type_filter_frame.pack(pady=(10, 0), padx=10, fill=tk.X)
        smart_btn = tk.Checkbutton(type_filter_frame, text="✔ Smart", variable=self.type_filter_smart, font=("Arial", 12), indicatoron=0, width=10, padx=10, pady=8, bg="#eaf2fa", selectcolor="#d0e6fa", command=lambda: self.show_main_interface(load_scenarios=False))
        simple_btn = tk.Checkbutton(type_filter_frame, text="✔ Simple", variable=self.type_filter_simple, font=("Arial", 12), indicatoron=0, width=10, padx=10, pady=8, bg="#eaf2fa", selectcolor="#d0e6fa", command=lambda: self.show_main_interface(load_scenarios=False))
        smart_btn.pack(side=tk.LEFT, padx=(5, 0))
        simple_btn.pack(side=tk.LEFT)
        self.widgets.extend([type_filter_frame, smart_btn, simple_btn])

        # Scenario cards
        if load_scenarios:
            self.load_scenarios()
        card_frame = tk.Frame(self.master, bg="#f3f7fa")
        card_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.widgets.append(card_frame)
        for name, data in self.scenarios.items():
            typ = data.get('type', 'Simple')
            show_smart = self.type_filter_smart.get()
            show_simple = self.type_filter_simple.get()
            if (typ == "Smart" and not show_smart) or (typ == "Simple" and not show_simple):
                continue
            icon = "✖️➔" if typ == "Simple" else "🖼️"
            card = tk.Frame(card_frame, bg="#e9f1f7", bd=1, relief=tk.RIDGE)
            card.pack(fill=tk.X, pady=8)
            icon_label = tk.Label(card, text=icon, font=("Arial", 16), bg="#e9f1f7")
            icon_label.pack(side=tk.LEFT, padx=10)
            name_label = tk.Label(card, text=name, font=("Arial", 14, "bold"), bg="#e9f1f7")
            name_label.pack(side=tk.LEFT, padx=10)
            del_btn = tk.Button(card, text="🗑️", font=("Arial", 12), bd=0, command=lambda n=name: self.delete_scenario_by_name(n), cursor="hand2", bg="#e9f1f7", activebackground="#e9f1f7")
            del_btn.pack(side=tk.RIGHT, padx=10)
            play_btn = tk.Button(card, text="▶️", font=("Arial", 14), bd=0, command=lambda n=name: self.play_scenario_by_name(n), cursor="hand2", bg="#e9f1f7", activebackground="#e9f1f7")
            play_btn.pack(side=tk.RIGHT, padx=10)
            self.widgets.extend([card, icon_label, name_label, del_btn, play_btn])

        # Floating + button
        plus_btn = tk.Button(self.master, text="+", font=("Arial", 24, "bold"), bg="#b3e0ff", fg="#222", bd=0, command=self.show_new_scenario_interface, cursor="hand2")
        plus_btn.place(relx=0.92, rely=0.92, anchor="center")
        self.widgets.append(plus_btn)

    def update_mouse_position(self):
        x, y = pyautogui.position()
        self.coord_label.config(text=f"Current Mouse Position: ({x}, {y})")
        self.master.after(100, self.update_mouse_position)

    def update_description_label(self):
        name = self.scenario_var.get()
        desc = self.scenarios.get(name, {}).get('description', '') if name in self.scenarios else ''
        self.desc_label.config(text=f"Description: {desc}")
        if name in self.scenarios:
            self.edit_desc_button.config(state=tk.NORMAL)
        else:
            self.edit_desc_button.config(state=tk.DISABLED)

    def click_loop(self, interval):
        while self.running:
            pyautogui.click()
            time.sleep(interval)

    def start_clicking(self):
        try:
            interval_ms = int(self.interval_entry.get())
            if interval_ms < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for interval.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        interval = interval_ms / 1000.0
        self.thread = threading.Thread(target=self.click_loop, args=(interval,), daemon=True)
        self.thread.start()

    def stop_clicking(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.recording:
            self.toggle_recording()

    # Scenario features
    def toggle_recording(self):
        if not self.recording:
            self.recorded_scenario = []
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.save_button.config(state=tk.DISABLED)
            self.master.after(100, self.record_step)
            messagebox.showinfo("Recording", "Scenario recording started. Move your mouse and click to record positions. Press 'Stop Recording' to finish.")
        else:
            self.recording = False
            self.record_button.config(text="Record Scenario")
            if self.recorded_scenario:
                self.save_button.config(state=tk.NORMAL)

    def record_step(self):
        if self.recording:
            if pyautogui.mouseDown():
                x, y = pyautogui.position()
                t = time.time()
                if not self.recorded_scenario or t - self.recorded_scenario[-1][2] > 0.05:
                    interval = int(self.interval_entry.get()) if self.interval_entry.get().isdigit() else 100
                    self.recorded_scenario.append((x, y, t, interval))
            self.master.after(50, self.record_step)

    def save_scenario(self):
        name = simpledialog.askstring("Save Scenario", "Enter a name for this scenario:")
        if name:
            # Store only (x, y, interval) for each step
            steps = [(x, y, interval) for (x, y, t, interval) in self.recorded_scenario]
            desc = simpledialog.askstring("Scenario Description", "Enter a description for this scenario (optional):") or ""
            self.scenarios[name] = {'steps': steps, 'description': desc}
            self.save_scenarios()
            self.show_main_interface()

    def on_scenario_select(self, value):
        self.scenario_var.set(value)
        self.update_description_label()

    def play_scenario(self):
        name = self.scenario_var.get()
        if not name or name not in self.scenarios:
            messagebox.showerror("Error", "No scenario selected.")
            return
        scenario = self.scenarios[name]['steps']
        threading.Thread(target=self.run_scenario, args=(scenario,), daemon=True).start()

    def run_scenario(self, scenario):
        for (x, y, interval) in scenario:
            pyautogui.moveTo(x, y)
            pyautogui.click()
            time.sleep(interval / 1000.0)

    def delete_scenario(self):
        name = self.scenario_var.get()
        if not name or name not in self.scenarios:
            messagebox.showerror("Error", "No scenario selected to delete.")
            return
        if messagebox.askyesno("Delete Scenario", f"Are you sure you want to delete scenario '{name}'?"):
            del self.scenarios[name]
            self.save_scenarios()
            self.show_main_interface()

    def edit_scenario(self):
        name = self.scenario_var.get()
        if not name or name not in self.scenarios:
            messagebox.showerror("Error", "No scenario selected to edit.")
            return
        new_name = simpledialog.askstring("Edit Scenario Name", "Enter a new name for this scenario:", initialvalue=name)
        if new_name and new_name != name:
            self.scenarios[new_name] = self.scenarios.pop(name)
            self.save_scenarios()
            self.show_main_interface()
            self.scenario_var.set(new_name)
            messagebox.showinfo("Renamed", f"Scenario renamed to '{new_name}'.")

    def edit_description(self):
        name = self.scenario_var.get()
        if not name or name not in self.scenarios:
            messagebox.showerror("Error", "No scenario selected to edit description.")
            return
        desc = self.scenarios[name].get('description', '')
        new_desc = simpledialog.askstring("Edit Description", "Enter a new description:", initialvalue=desc)
        if new_desc is not None:
            self.scenarios[name]['description'] = new_desc
            self.save_scenarios()
            self.update_description_label()
            messagebox.showinfo("Updated", "Scenario description updated.")

    def edit_scenario_steps(self):
        name = self.scenario_var.get()
        if not name or name not in self.scenarios:
            messagebox.showerror("Error", "No scenario selected to edit steps.")
            return
        steps = self.scenarios[name]['steps']
        editor = tk.Toplevel(self.master)
        editor.title(f"Edit Steps: {name}")
        editor.geometry("500x500")
        listbox = tk.Listbox(editor, width=60)
        listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        for i, (x, y, interval) in enumerate(steps):
            listbox.insert(tk.END, f"Step {i+1}: x={x}, y={y}, interval={interval}ms")

        def add_step():
            x = simpledialog.askinteger("Add Step", "X position:", parent=editor)
            y = simpledialog.askinteger("Add Step", "Y position:", parent=editor)
            interval = simpledialog.askinteger("Add Step", "Interval (ms):", parent=editor, initialvalue=100)
            if x is not None and y is not None and interval is not None:
                steps.append((x, y, interval))
                listbox.insert(tk.END, f"Step {len(steps)}: x={x}, y={y}, interval={interval}ms")

        def remove_step():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            del steps[idx]
            listbox.delete(idx)
            # Update listbox labels
            listbox.delete(0, tk.END)
            for i, (x, y, interval) in enumerate(steps):
                listbox.insert(tk.END, f"Step {i+1}: x={x}, y={y}, interval={interval}ms")

        def edit_step():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            x, y, interval = steps[idx]
            new_x = simpledialog.askinteger("Edit Step", "X position:", parent=editor, initialvalue=x)
            new_y = simpledialog.askinteger("Edit Step", "Y position:", parent=editor, initialvalue=y)
            new_interval = simpledialog.askinteger("Edit Step", "Interval (ms):", parent=editor, initialvalue=interval)
            if new_x is not None and new_y is not None and new_interval is not None:
                steps[idx] = (new_x, new_y, new_interval)
                listbox.delete(idx)
                listbox.insert(idx, f"Step {idx+1}: x={new_x}, y={new_y}, interval={new_interval}ms")

        def move_up():
            sel = listbox.curselection()
            if not sel or sel[0] == 0:
                return
            idx = sel[0]
            steps[idx-1], steps[idx] = steps[idx], steps[idx-1]
            listbox.delete(0, tk.END)
            for i, (x, y, interval) in enumerate(steps):
                listbox.insert(tk.END, f"Step {i+1}: x={x}, y={y}, interval={interval}ms")
            listbox.select_set(idx-1)

        def move_down():
            sel = listbox.curselection()
            if not sel or sel[0] == len(steps)-1:
                return
            idx = sel[0]
            steps[idx+1], steps[idx] = steps[idx], steps[idx+1]
            listbox.delete(0, tk.END)
            for i, (x, y, interval) in enumerate(steps):
                listbox.insert(tk.END, f"Step {i+1}: x={x}, y={y}, interval={interval}ms")
            listbox.select_set(idx+1)

        def save_and_close():
            self.scenarios[name]['steps'] = steps
            self.save_scenarios()
            editor.destroy()
            messagebox.showinfo("Saved", "Scenario steps updated.")

        btn_frame = tk.Frame(editor)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Step", command=add_step).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Step", command=remove_step).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Step", command=edit_step).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Move Up", command=move_up).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Move Down", command=move_down).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save & Close", command=save_and_close).pack(side=tk.LEFT, padx=5)

    def export_scenarios(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export Scenarios")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.scenarios, f)
                messagebox.showinfo("Exported", f"Scenarios exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def import_scenarios(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Import Scenarios")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded scenarios
                    for k, v in loaded.items():
                        if isinstance(v, dict) and 'steps' in v:
                            self.scenarios[str(k)] = {'steps': [tuple(step) for step in v['steps']], 'description': v.get('description', '')}
                        else:
                            # Backward compatibility: old format
                            self.scenarios[str(k)] = {'steps': [tuple(step) for step in v], 'description': ''}
                self.save_scenarios()
                self.show_main_interface()
                messagebox.showinfo("Imported", f"Scenarios imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")

    def save_scenarios(self):
        try:
            with open(SCENARIO_FILE, 'w') as f:
                json.dump(self.scenarios, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scenarios: {e}")

    def load_scenarios(self):
        if os.path.exists(SCENARIO_FILE):
            try:
                with open(SCENARIO_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Convert keys to str and values to dict with steps and description
                    for k, v in loaded.items():
                        if isinstance(v, dict) and 'steps' in v:
                            self.scenarios[str(k)] = {'steps': [tuple(step) for step in v['steps']], 'description': v.get('description', ''), 'type': v.get('type', 'Simple')}
                        else:
                            # Backward compatibility: old format
                            self.scenarios[str(k)] = {'steps': [tuple(step) for step in v], 'description': '', 'type': 'Simple'}
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load scenarios: {e}")
        # Do NOT call self.show_main_interface() here to avoid recursion

    def delete_scenario_by_name(self, name):
        if name in self.scenarios:
            if messagebox.askyesno("Delete Scenario", f"Are you sure you want to delete scenario '{name}'?"):
                del self.scenarios[name]
                self.save_scenarios()
                self.show_main_interface()

    def play_scenario_by_name(self, name):
        # Show a custom overlay permission popup styled like the mobile app
        popup = tk.Toplevel(self.master)
        popup.title("Overlay")
        popup.geometry("400x260")
        popup.transient(self.master)
        popup.grab_set()
        popup.resizable(False, False)
        # Center the popup
        popup.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 200
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 130
        popup.geometry(f"400x260+{x}+{y}")
        try:
            popup.wm_attributes("-type", "dialog")
        except:
            pass
        frame = tk.Frame(popup, bg="#f6fafd", bd=0, relief=tk.FLAT)
        frame.pack(fill=tk.BOTH, expand=True)
        title = tk.Label(frame, text="Overlay", font=("Arial", 18, "bold"), bg="#f6fafd")
        title.pack(pady=(20, 10))
        msg = tk.Label(frame, text="The overlay permission is required in order to show Klick'r interface over the applications you want to automate, allowing you to configure your scenario without stopping the other application.", font=("Arial", 11), bg="#f6fafd", wraplength=340, justify="center")
        msg.pack(pady=(0, 20))
        btn_frame = tk.Frame(frame, bg="#f6fafd")
        btn_frame.pack(pady=(0, 10))
        def close_popup():
            popup.destroy()
        def show_accessibility_popup():
            close_popup()
            self.show_accessibility_popup()
        req_btn = tk.Button(btn_frame, text="Request permission", font=("Arial", 12, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", padx=20, pady=6, command=show_accessibility_popup, relief=tk.FLAT, bd=0)
        req_btn.pack(side=tk.TOP, pady=(0, 10), ipadx=10, ipady=2, fill=tk.X)
        deny_btn = tk.Button(frame, text="Deny", font=("Arial", 12), bg="#f6fafd", fg="#1976d2", activebackground="#e3eaf6", activeforeground="#1976d2", padx=20, pady=6, command=close_popup, relief=tk.FLAT, bd=1, highlightbackground="#b0b0b0")
        deny_btn.pack(pady=(0, 10), ipadx=10, ipady=2, fill=tk.X)

    def show_accessibility_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Accessibility service")
        popup.geometry("400x340")
        popup.transient(self.master)
        popup.grab_set()
        popup.resizable(False, False)
        # Center the popup
        popup.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 200
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 170
        popup.geometry(f"400x340+{x}+{y}")
        try:
            popup.wm_attributes("-type", "dialog")
        except:
            pass
        frame = tk.Frame(popup, bg="#f6fafd", bd=0, relief=tk.FLAT)
        frame.pack(fill=tk.BOTH, expand=True)
        title = tk.Label(frame, text="Accessibility service", font=("Arial", 18, "bold"), bg="#f6fafd")
        title.pack(pady=(20, 10))
        msg = tk.Label(frame, text="The accessibility service permission allows Klick'r to perform gestures on your device screen. This permission is required in order to execute the clicks and swipes you will create in your automations scenarios.\n\nNo data is collected by Klick'r\n\nTo grant the Accessibility service permission, click on the button bellow.", font=("Arial", 11), bg="#f6fafd", wraplength=340, justify="center")
        msg.pack(pady=(0, 20))
        btn_frame = tk.Frame(frame, bg="#f6fafd")
        btn_frame.pack(pady=(0, 10), fill=tk.X)
        def close_popup():
            popup.destroy()
        def show_full_control_popup():
            close_popup()
            self.show_full_control_popup()
        req_btn = tk.Button(btn_frame, text="Request permission", font=("Arial", 12, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", padx=20, pady=8, command=show_full_control_popup, relief=tk.FLAT, bd=0)
        req_btn.pack(fill=tk.X, padx=40, pady=(0, 10))
        deny_btn = tk.Button(btn_frame, text="Deny", font=("Arial", 12), bg="#f6fafd", fg="#1976d2", activebackground="#e3eaf6", activeforeground="#1976d2", padx=20, pady=8, command=close_popup, relief=tk.FLAT, bd=1, highlightbackground="#b0b0b0")
        deny_btn.pack(fill=tk.X, padx=40)

    def show_full_control_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Full control")
        popup.geometry("400x420")
        popup.transient(self.master)
        popup.grab_set()
        popup.resizable(False, False)
        # Center the popup
        popup.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 200
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 210
        popup.geometry(f"400x420+{x}+{y}")
        try:
            popup.wm_attributes("-type", "dialog")
        except:
            pass
        frame = tk.Frame(popup, bg="#f6fafd", bd=0, relief=tk.FLAT)
        frame.pack(fill=tk.BOTH, expand=True)
        # Green icon (simulate with emoji)
        icon = tk.Label(frame, text="🟩", font=("Arial", 36), bg="#f6fafd")
        icon.pack(pady=(18, 0))
        title = tk.Label(frame, text="Allow Klick'r to have full control\nof your device?", font=("Arial", 15, "bold"), bg="#f6fafd", justify="center")
        title.pack(pady=(10, 10))
        desc = tk.Label(frame, text="Full control is appropriate for apps that help you with accessibility needs, but not for most apps.", font=("Arial", 11), bg="#f6fafd", wraplength=340, justify="center")
        desc.pack(pady=(0, 10))
        # Permission explanations
        perm1 = tk.Label(frame, text=" 441  View and control screen\nIt can read all content on the screen and display content over other apps.", font=("Arial", 11), bg="#f6fafd", anchor="w", justify="left")
        perm1.pack(pady=(0, 6), padx=30, anchor="w")
        perm2 = tk.Label(frame, text=" 91a  View and perform actions\nIt can track your interactions with an app or a hardware sensor, and interact with apps on your behalf.", font=("Arial", 11), bg="#f6fafd", anchor="w", justify="left")
        perm2.pack(pady=(0, 10), padx=30, anchor="w")
        # Button row
        btn_frame = tk.Frame(frame, bg="#f6fafd")
        btn_frame.pack(pady=(10, 10), fill=tk.X)
        def close_popup():
            popup.destroy()
        def show_overlay_bar():
            close_popup()
            self.show_floating_overlay_bar()
        allow_btn = tk.Button(btn_frame, text="ALLOW", font=("Arial", 12, "bold"), bg="#1abc6b", fg="white", activebackground="#159c54", activeforeground="white", padx=20, pady=8, command=show_overlay_bar, relief=tk.FLAT, bd=0)
        allow_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(20, 5))
        deny_btn = tk.Button(btn_frame, text="DENY", font=("Arial", 12, "bold"), bg="#f6fafd", fg="#1976d2", activebackground="#e3eaf6", activeforeground="#1976d2", padx=20, pady=8, command=close_popup, relief=tk.FLAT, bd=1, highlightbackground="#b0b0b0")
        deny_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        uninstall_btn = tk.Button(btn_frame, text="UNINSTALL…", font=("Arial", 12, "bold"), bg="#f6fafd", fg="#1976d2", activebackground="#e3eaf6", activeforeground="#1976d2", padx=20, pady=8, command=close_popup, relief=tk.FLAT, bd=1, highlightbackground="#b0b0b0")
        uninstall_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 20))

    def show_floating_overlay_bar(self, x=None, y=None):
        overlay = tk.Toplevel(self.master)
        overlay.title("Klick'r Overlay")
        overlay.geometry("60x320+{}+{}".format(
            x if x is not None else self.master.winfo_screenwidth()-80,
            y if y is not None else 80))
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.7)
        overlay.config(bg="#3a4655")
        # Make overlay draggable
        def start_move(event):
            overlay._drag_start_x = event.x
            overlay._drag_start_y = event.y
        def do_move(event):
            nx = overlay.winfo_x() + event.x - overlay._drag_start_x
            ny = overlay.winfo_y() + event.y - overlay._drag_start_y
            overlay.geometry(f"60x320+{nx}+{ny}")
        overlay.bind('<Button-1>', start_move)
        overlay.bind('<B1-Motion>', do_move)
        # Vertical bar with icons (visual only)
        btn_frame = tk.Frame(overlay, bg="#3a4655")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # Play
        play_btn = tk.Button(btn_frame, text="▶️", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        play_btn.pack(pady=(0, 18), fill=tk.X)
        # Close
        close_btn = tk.Button(btn_frame, text="✖️", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white", command=overlay.destroy)
        close_btn.pack(pady=(0, 18), fill=tk.X)
        # Scenario (3rd button)
        def show_alt_overlay():
            ox, oy = overlay.winfo_x(), overlay.winfo_y()
            overlay.destroy()
            self.show_alt_floating_overlay_bar(ox, oy)
        scenario_btn = tk.Button(btn_frame, text="🔀", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white", command=show_alt_overlay)
        scenario_btn.pack(pady=(0, 18), fill=tk.X)
        # Settings
        settings_btn = tk.Button(btn_frame, text="⚙️", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        settings_btn.pack(pady=(0, 18), fill=tk.X)
        # Move
        move_btn = tk.Button(btn_frame, text="⤢", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        move_btn.pack(pady=(0, 0), fill=tk.X)

    def show_alt_floating_overlay_bar(self, x, y):
        overlay = tk.Toplevel(self.master)
        overlay.title("Klick'r Overlay Alt")
        overlay.geometry(f"60x320+{x}+{y}")
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.7)
        overlay.config(bg="#3a4655")
        # Make overlay draggable
        def start_move(event):
            overlay._drag_start_x = event.x
            overlay._drag_start_y = event.y
        def do_move(event):
            nx = overlay.winfo_x() + event.x - overlay._drag_start_x
            ny = overlay.winfo_y() + event.y - overlay._drag_start_y
            overlay.geometry(f"60x320+{nx}+{ny}")
        overlay.bind('<Button-1>', start_move)
        overlay.bind('<B1-Motion>', do_move)
        btn_frame = tk.Frame(overlay, bg="#3a4655")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # ←
        left_btn = tk.Button(btn_frame, text="←", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        left_btn.pack(pady=(0, 18), fill=tk.X)
        # ⦿
        circle_btn = tk.Button(btn_frame, text="⦿", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        circle_btn.pack(pady=(0, 18), fill=tk.X)
        # ＋
        plus_btn = tk.Button(btn_frame, text="＋", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        plus_btn.pack(pady=(0, 18), fill=tk.X)
        # 👁️
        eye_btn = tk.Button(btn_frame, text="👁️", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        eye_btn.pack(pady=(0, 18), fill=tk.X)
        # ⬌
        move_btn = tk.Button(btn_frame, text="⬌", font=("Arial", 18), bg="#3a4655", fg="white", bd=0, relief=tk.FLAT, activebackground="#2e3742", activeforeground="white")
        move_btn.pack(pady=(0, 0), fill=tk.X)

    def search_scenarios(self):
        messagebox.showinfo("Search", "Search functionality to be implemented.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop() 
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import threading
import pyautogui
import keyboard
import time
import json
import os
import math

SCENARIO_FILE = 'scenarios.json'

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Scenarios")
        self.master.config(bg="#212121")
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
        self.master.config(bg="#101D18")

        topbar = tk.Frame(self.master, bg="#101D18")
        topbar.pack(fill=tk.X, pady=(5, 0), padx=(20, 5))

        title = tk.Label(topbar, text="Scenarios", font=("Arial", 22, "bold"), fg="white", bg="#101D18")
        title.pack(side=tk.LEFT)

        folder_btn = tk.Button(topbar, text="📁", font=("Arial", 16), bd=0, command=self.import_scenarios, cursor="hand2", bg="#101D18", fg="white", activebackground="#101D18", activeforeground="white")
        folder_btn.pack(side=tk.RIGHT)
        
        center_frame = tk.Frame(self.master, bg="#101D18")
        center_frame.pack(pady=20, expand=True)

        canvas = tk.Canvas(center_frame, width=120, height=120, bg="#101D18", highlightthickness=0)
        
        # Draw the box icon
        canvas.create_polygon(30, 70, 60, 85, 90, 70, 60, 55, fill="#f0f0f0", outline="grey")
        canvas.create_polygon(30, 70, 30, 90, 60, 105, 60, 85, fill="#e0e0e0", outline="grey")
        canvas.create_polygon(90, 70, 90, 90, 60, 105, 60, 85, fill="#d0d0d0", outline="grey")
        canvas.create_polygon(30, 70, 60, 55, 60, 35, 30, 50, fill="white", outline="grey")
        canvas.create_polygon(90, 70, 60, 55, 60, 35, 90, 50, fill="#f8f8f8", outline="grey")

        for i in range(7):
            angle = -15 + i * 25
            rad = angle * math.pi / 180
            x1 = 60 + 30 * math.cos(rad)
            y1 = 40 - 30 * math.sin(rad)
            x2 = 60 + 40 * math.cos(rad)
            y2 = 40 - 40 * math.sin(rad)
            canvas.create_line(x1, y1, x2, y2, fill="#4CAF50", width=2)
        
        canvas.pack(pady=20)

        subtitle = tk.Label(center_frame, text="Create your first scenario and start\nautomatizing tasks on your phone", font=("Arial", 14), justify="center", fg="white", bg="#101D18")
        subtitle.pack(pady=20)

        create_btn = tk.Button(self.master, text="Create a scenario", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white", padx=20, pady=10, command=self.create_first_scenario, relief=tk.FLAT, bd=0)
        create_btn.pack(pady=30, ipadx=10, ipady=5)

        self.widgets.extend([topbar, title, folder_btn, center_frame, canvas, subtitle, create_btn])


    def show_new_scenario_interface(self):
        # Modal dialog for new scenario (mobile style)
        dialog = tk.Toplevel(self.master)
        dialog.title("New scenario")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg="#18221B")
        # Center the dialog
        dialog.update_idletasks()
        w, h = 380, 220
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        # Rounded effect (simulate with padding and bg)
        container = tk.Frame(dialog, bg="#233024", bd=0)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.7)

        title = tk.Label(container, text="New scenario", font=("Arial", 16, "bold"), fg="white", bg="#233024")
        title.pack(pady=(18, 8))

        entry_frame = tk.Frame(container, bg="#233024")
        entry_frame.pack(pady=(0, 10), padx=18, fill=tk.X)
        name_entry = tk.Entry(entry_frame, font=("Arial", 13), bg="#18221B", fg="white", insertbackground="white", relief=tk.FLAT, highlightthickness=2, highlightcolor="#4CAF50")
        name_entry.pack(fill=tk.X, ipady=7)
        name_entry.insert(0, "")
        name_entry.focus_set()
        name_entry.config(justify="left")
        name_entry.bind("<Return>", lambda e: save())
        name_entry.bind("<Escape>", lambda e: cancel())
        name_entry.config(highlightbackground="#4CAF50")
        name_entry.placeholder = "Name"  # For reference, not shown in Tkinter
        self.new_scenario_name_entry = name_entry

        # Button row
        btn_frame = tk.Frame(container, bg="#233024")
        btn_frame.pack(pady=(10, 0), fill=tk.X)
        def cancel():
            dialog.destroy()
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Scenario name cannot be empty.", parent=dialog)
                return
            self.scenarios[name] = {'steps': [], 'description': '', 'type': 'Simple'}
            self.save_scenarios()
            dialog.destroy()
            self.show_main_interface()
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 12), bg="#233024", fg="#4CAF50", activebackground="#233024", activeforeground="#4CAF50", bd=0, relief=tk.FLAT, command=cancel)
        cancel_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8), ipadx=8, ipady=3)
        ok_btn = tk.Button(btn_frame, text="OK", font=("Arial", 12, "bold"), bg="#233024", fg="#4CAF50", activebackground="#233024", activeforeground="#4CAF50", bd=0, relief=tk.FLAT, command=save)
        ok_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0), ipadx=8, ipady=3)

        # For keyboard navigation
        dialog.bind("<Escape>", lambda e: cancel())
        dialog.bind("<Return>", lambda e: save())

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
        # No longer used with modal dialog, but keep for compatibility
        pass

    def show_main_interface(self, load_scenarios=True):
        if load_scenarios:
            self.load_scenarios()

        if not self.scenarios:
            self.show_welcome_screen()
            return

        self.clear_widgets()
        self.master.config(bg="#101D18")

        # Top bar
        topbar = tk.Frame(self.master, bg="#101D18")
        topbar.pack(fill=tk.X, pady=(5, 0))
        title = tk.Label(topbar, text="Scenarios", font=("Arial", 22, "bold"), fg="white", bg="#101D18")
        title.pack(side=tk.LEFT, padx=(20, 0))
        search_btn = tk.Button(topbar, text="🔍", font=("Arial", 16), bd=0, command=self.search_scenarios, cursor="hand2", bg="#101D18", fg="white", activebackground="#101D18")
        search_btn.pack(side=tk.RIGHT, padx=5)
        folder_btn = tk.Button(topbar, text="📁", font=("Arial", 16), bd=0, command=self.import_scenarios, cursor="hand2", bg="#101D18", fg="white", activebackground="#101D18")
        folder_btn.pack(side=tk.RIGHT, padx=5)
        self.widgets.extend([topbar, title, folder_btn, search_btn])

        # Scenario cards
        card_frame = tk.Frame(self.master, bg="#101D18")
        card_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.widgets.append(card_frame)
        for name, data in self.scenarios.items():
            typ = data.get('type', 'Simple')
            
            card = tk.Frame(card_frame, bg="#2C3E34", height=60)
            card.pack(fill=tk.X, pady=5, ipady=8)
            card.pack_propagate(False)

            name_label = tk.Label(card, text=name, font=("Arial", 14), bg="#2C3E34", fg="white")
            name_label.pack(side=tk.LEFT, padx=20)
            
            play_canvas = tk.Canvas(card, width=40, height=40, bg="#2C3E34", highlightthickness=0)
            play_canvas.create_oval(5, 5, 35, 35, fill="#4CAF50", outline="")
            play_canvas.create_polygon(17, 14, 17, 26, 28, 20, fill="white")
            play_canvas.pack(side=tk.RIGHT, padx=10)
            play_canvas.bind("<Button-1>", lambda e, n=name: self.play_scenario_by_name(n))

            del_btn = tk.Button(card, text="🗑️", font=("Arial", 12), bd=0, command=lambda n=name: self.delete_scenario_by_name(n), cursor="hand2", bg="#2C3E34", fg="white", activebackground="#2C3E34")
            del_btn.pack(side=tk.RIGHT, padx=10)
            
            self.widgets.extend([card, name_label, del_btn, play_canvas])

        # Floating + button
        plus_btn = tk.Button(self.master, text="+", font=("Arial", 24, "bold"), bg="#4CAF50", fg="white", bd=0, command=self.show_new_scenario_interface, cursor="hand2", activebackground="#45a049", relief=tk.FLAT)
        plus_btn.place(relx=0.9, rely=0.9, anchor="center", width=50, height=50)
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
        overlay.attributes("-alpha", 0.95)
        overlay.config(bg="#000000")  # Pure black
        self.overlay_window = overlay  # Store reference for raising
        btn_frame = tk.Frame(overlay, bg="#000000")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        play_btn = tk.Button(btn_frame, text="▶", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        play_btn.pack(pady=(18, 24), fill=tk.X)
        stop_btn = tk.Button(btn_frame, text="■", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        stop_btn.pack(pady=(0, 24), fill=tk.X)
        def open_settings_modal():
            self.show_settings_modal()
            # Re-raise overlay after modal is created
            if hasattr(self, 'overlay_window') and self.overlay_window.winfo_exists():
                self.overlay_window.attributes('-topmost', True)
                self.overlay_window.lift()
        settings_btn = tk.Button(btn_frame, text="⚙", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white", command=open_settings_modal)
        settings_btn.pack(pady=(0, 24), fill=tk.X)
        move_btn = tk.Button(btn_frame, text="⇲", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        move_btn.pack(pady=(0, 0), fill=tk.X)
        def start_move(event):
            overlay._drag_start_x = event.x
            overlay._drag_start_y = event.y
        def do_move(event):
            nx = overlay.winfo_x() + event.x - overlay._drag_start_x
            ny = overlay.winfo_y() + event.y - overlay._drag_start_y
            overlay.geometry(f"60x320+{nx}+{ny}")
        move_btn.bind('<Button-1>', start_move)
        move_btn.bind('<B1-Motion>', do_move)

    def show_settings_modal(self):
        modal = tk.Toplevel(self.master)
        modal.title("Scenario Settings")
        modal.transient(self.master)
        # modal.grab_set()  # Do NOT grab, so overlay remains interactive
        modal.resizable(False, False)
        modal.configure(bg="#18221B")
        w, h = 420, 420
        self.master.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")
        # Top bar
        topbar = tk.Frame(modal, bg="#232D23")
        topbar.pack(fill=tk.X, pady=(0, 0))
        close_btn = tk.Button(topbar, text="✕", font=("Arial", 18), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        close_btn.pack(side=tk.LEFT, padx=16, pady=8)
        title = tk.Label(topbar, text="Scenario", font=("Arial", 18, "bold"), fg="white", bg="#232D23")
        title.pack(side=tk.LEFT, padx=10, pady=8)
        save_btn = tk.Button(topbar, text="💾", font=("Arial", 16), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        save_btn.pack(side=tk.RIGHT, padx=16, pady=8)
        center_frame = tk.Frame(modal, bg="#18221B")
        center_frame.pack(expand=True)
        msg = tk.Label(center_frame, text="No events !", font=("Arial", 20, "bold"), fg="white", bg="#18221B")
        msg.pack(pady=(60, 10))
        desc = tk.Label(center_frame, text="An event contains a set of actions executed when a specific\ncondition is detected on the screen.\nYou need at least one event in your scenario to execute it.", font=("Arial", 12), fg="#B0B0B0", bg="#18221B", justify="center")
        desc.pack(pady=(0, 0))
        def on_add_event():
            self.show_event_modal()
        plus_btn = tk.Button(modal, text="+", font=("Arial", 22, "bold"), bg="#1abc6b", fg="white", activebackground="#159c54", activeforeground="white", bd=0, relief=tk.FLAT, command=on_add_event)
        plus_btn.place(relx=0.93, rely=0.93, anchor="se", width=56, height=56)
        plus_btn.config(highlightthickness=0, borderwidth=0)
        plus_btn.config(cursor="hand2")
        plus_btn.config(overrelief=tk.FLAT)
        plus_btn.config(relief=tk.FLAT)
        plus_btn.config(border=0)
        plus_btn.config(highlightbackground="#1abc6b")
        plus_btn.config(highlightcolor="#1abc6b")
        plus_btn.config(font=("Arial", 28, "bold"))
        plus_btn.config(pady=0, padx=0)
        plus_btn.config(justify="center")
        # Re-raise overlay to top after modal is created
        if hasattr(self, 'overlay_window') and self.overlay_window.winfo_exists():
            self.overlay_window.attributes('-topmost', True)
            self.overlay_window.lift()

    def show_event_modal(self):
        import tkinter.ttk as ttk
        from PIL import Image, ImageTk
        import pyautogui
        if not hasattr(self, '_event_conditions'):
            self._event_conditions = []  # In-memory list of conditions for this event
        modal = tk.Toplevel(self.master)
        modal.title("Event")
        modal.transient(self.master)
        modal.resizable(False, False)
        modal.configure(bg="#18221B")
        w, h = 420, 420
        self.master.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")
        # Top bar
        topbar = tk.Frame(modal, bg="#232D23")
        topbar.pack(fill=tk.X, pady=(0, 0))
        close_btn = tk.Button(topbar, text="✕", font=("Arial", 18), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        close_btn.pack(side=tk.LEFT, padx=16, pady=8)
        title = tk.Label(topbar, text="Event", font=("Arial", 18, "bold"), fg="white", bg="#232D23")
        title.pack(side=tk.LEFT, padx=10, pady=8)
        delete_btn = tk.Button(topbar, text="🗑️", font=("Arial", 16), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        delete_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        save_btn = tk.Button(topbar, text="💾", font=("Arial", 16), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        save_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        # Content area (swappable)
        content_frame = tk.Frame(modal, bg="#18221B")
        content_frame.pack(expand=True, fill=tk.BOTH)
        modal._event_content_frame = content_frame
        modal._event_active_tab = 'config'
        def show_config():
            for w in content_frame.winfo_children():
                w.destroy()
            name_frame = tk.Frame(content_frame, bg="#18221B")
            name_frame.pack(fill=tk.X, padx=24, pady=(32, 8))
            name_label = tk.Label(name_frame, text="Name", font=("Arial", 11), fg="#B0FFB0", bg="#18221B", anchor="w")
            name_label.pack(fill=tk.X, anchor="w")
            name_entry = tk.Entry(name_frame, font=("Arial", 15), bg="#232D23", fg="white", insertbackground="white", relief=tk.FLAT, highlightthickness=2, highlightcolor="#4CAF50")
            name_entry.pack(fill=tk.X, ipady=7)
            name_entry.insert(0, "Default event")
            cond_frame = tk.Frame(content_frame, bg="#18221B")
            cond_frame.pack(fill=tk.X, padx=24, pady=(8, 0))
            cond_label = tk.Label(cond_frame, text="Conditions", font=("Arial", 11), fg="#4CAF50", bg="#18221B", anchor="w")
            cond_label.pack(fill=tk.X, anchor="w")
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Green.TCombobox', fieldbackground='#232D23', background='#232D23', foreground='white', bordercolor='#4CAF50', lightcolor='#4CAF50', darkcolor='#4CAF50', arrowcolor='#4CAF50')
            cond_var = tk.StringVar(value="All")
            cond_combo = ttk.Combobox(cond_frame, textvariable=cond_var, values=["All", "One"], font=("Arial", 14), style='Green.TCombobox', state="readonly")
            cond_combo.pack(fill=tk.X, ipady=4)
        def show_conditions():
            for w in content_frame.winfo_children():
                w.destroy()
            # If there are conditions, show them as cards
            if self._event_conditions:
                card_frame = tk.Frame(content_frame, bg="#18221B")
                card_frame.pack(fill=tk.X, padx=16, pady=(16, 0))
                for idx, cond in enumerate(self._event_conditions):
                    card = tk.Frame(card_frame, bg="#232D23", bd=0, relief=tk.FLAT)
                    card.pack(fill=tk.X, pady=8)
                    # Thumbnail
                    img = Image.open(cond['image_path'])
                    img.thumbnail((120, 60))
                    tk_img = ImageTk.PhotoImage(img)
                    img_label = tk.Label(card, image=tk_img, bg="#232D23")
                    img_label.image = tk_img
                    img_label.place(x=0, y=0)
                    # Name
                    name_label = tk.Label(card, text=cond['name'], font=("Arial", 13, "bold"), fg="white", bg="#232D23")
                    name_label.place(x=8, y=4)
                    # Detection type icon
                    det_icon = "🗔" if cond['det_type'] == "Exact" else ("📱" if cond['det_type'] == "Screen" else "⬚")
                    det_label = tk.Label(card, text=det_icon, font=("Arial", 16), fg="#4CAF50", bg="#232D23")
                    det_label.place(x=8, y=32)
                    # Status (checkmark)
                    status_label = tk.Label(card, text="✔", font=("Arial", 16), fg="#4CAF50", bg="#232D23")
                    status_label.place(x=90, y=32)
                    # Percentage (dummy)
                    percent_label = tk.Label(card, text="4%", font=("Arial", 10), fg="#B0FFB0", bg="#232D23")
                    percent_label.place(x=90, y=50)
                    # Delete button
                    del_btn = tk.Button(card, text="🗑️", font=("Arial", 12), bd=0, command=lambda i=idx: delete_condition(i), cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
                    del_btn.place(x=140, y=10, width=32, height=32)
                    # Copy button
                    copy_btn = tk.Button(card, text="📋", font=("Arial", 12), bd=0, command=lambda i=idx: copy_condition(i), cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
                    copy_btn.place(x=180, y=10, width=32, height=32)
                    card.config(width=220, height=70)
                    card.pack_propagate(False)
            else:
                msg = tk.Label(content_frame, text="No conditions !", font=("Arial", 20, "bold"), fg="white", bg="#18221B")
                msg.pack(pady=(60, 10))
                desc = tk.Label(content_frame, text="A condition is a part of a screenshot that will be searched on each frames displayed by your phone screen.\nYou need at least one condition in your event.", font=("Arial", 12), fg="#B0B0B0", bg="#18221B", justify="center")
                desc.pack(pady=(0, 0))
            def on_add_condition():
                self.start_condition_capture(lambda cond: add_condition_and_refresh(cond, show_conditions))
            plus_btn = tk.Button(content_frame, text="+", font=("Arial", 22, "bold"), bg="#1abc6b", fg="white", activebackground="#159c54", activeforeground="white", bd=0, relief=tk.FLAT, command=on_add_condition)
            plus_btn.place(relx=0.93, rely=0.93, anchor="se", width=56, height=56)
            plus_btn.config(highlightthickness=0, borderwidth=0, cursor="hand2", overrelief=tk.FLAT, relief=tk.FLAT, border=0, highlightbackground="#1abc6b", highlightcolor="#1abc6b", font=("Arial", 28, "bold"), pady=0, padx=0, justify="center")
            def delete_condition(idx):
                del self._event_conditions[idx]
                show_conditions()
            def copy_condition(idx):
                import shutil
                import uuid
                cond = self._event_conditions[idx].copy()
                new_img_path = f"cropped_condition_{uuid.uuid4().hex}.png"
                shutil.copy(cond['image_path'], new_img_path)
                cond['image_path'] = new_img_path
                cond['name'] += " (copy)"
                self._event_conditions.append(cond)
                show_conditions()
            def add_condition_and_refresh(cond, refresh_func):
                self._event_conditions.append(cond)
                refresh_func()
        def show_actions():
            for w in content_frame.winfo_children():
                w.destroy()
            msg = tk.Label(content_frame, text="No actions !", font=("Arial", 20, "bold"), fg="white", bg="#18221B")
            msg.pack(pady=(60, 10))
            desc = tk.Label(content_frame, text="An action is an interaction (click, swipe...) with your phone triggered when the created conditions are fulfilled.\nYou need at least one action in your event.", font=("Arial", 12), fg="#B0B0B0", bg="#18221B", justify="center")
            desc.pack(pady=(0, 0))
            def on_add_action():
                pass  # Placeholder
            plus_btn = tk.Button(content_frame, text="+", font=("Arial", 22, "bold"), bg="#1abc6b", fg="white", activebackground="#159c54", activeforeground="white", bd=0, relief=tk.FLAT, command=on_add_action)
            plus_btn.place(relx=0.93, rely=0.93, anchor="se", width=56, height=56)
            plus_btn.config(highlightthickness=0, borderwidth=0, cursor="hand2", overrelief=tk.FLAT, relief=tk.FLAT, border=0, highlightbackground="#1abc6b", highlightcolor="#1abc6b", font=("Arial", 28, "bold"), pady=0, padx=0, justify="center")
        nav_bar = tk.Frame(modal, bg="#232D23")
        nav_bar.pack(side=tk.BOTTOM, fill=tk.X)
        def set_active(tab):
            modal._event_active_tab = tab
            for btn, t in [(nav_btn1, 'config'), (nav_btn2, 'conditions'), (nav_btn3, 'actions')]:
                if t == tab:
                    btn.config(bg="#232D23", fg="#4CAF50")
                else:
                    btn.config(bg="#232D23", fg="#B0FFB0")
            if tab == 'config':
                show_config()
            elif tab == 'conditions':
                show_conditions()
            elif tab == 'actions':
                show_actions()
        nav_btn1 = tk.Button(nav_bar, text="⚙\nConfig", font=("Arial", 12), bd=0, bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50", command=lambda: set_active('config'))
        nav_btn1.pack(side=tk.LEFT, expand=True, fill=tk.X)
        nav_btn2 = tk.Button(nav_bar, text="🖼️\nConditions", font=("Arial", 12), bd=0, bg="#232D23", fg="#B0FFB0", activebackground="#232D23", activeforeground="#4CAF50", command=lambda: set_active('conditions'))
        nav_btn2.pack(side=tk.LEFT, expand=True, fill=tk.X)
        nav_btn3 = tk.Button(nav_bar, text="🖱️\nActions", font=("Arial", 12), bd=0, bg="#232D23", fg="#B0FFB0", activebackground="#232D23", activeforeground="#4CAF50", command=lambda: set_active('actions'))
        nav_btn3.pack(side=tk.LEFT, expand=True, fill=tk.X)
        set_active('config')

    def start_condition_capture(self, on_save=None):
        import pyautogui
        from PIL import Image, ImageTk
        screenshot = pyautogui.screenshot()
        screenshot.save('full_screenshot.png')
        overlay = tk.Toplevel(self.master)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.config(bg='#000000')
        overlay.attributes('-alpha', 0.3)
        cam_btn = tk.Button(overlay, text='📷', font=("Arial", 28), bg='#ffffff', fg='#222', bd=0, relief=tk.FLAT, command=lambda: on_screenshot())
        cam_btn.place(relx=0.05, rely=0.5, anchor='w', width=60, height=60)
        cancel_btn = tk.Button(overlay, text='✖', font=("Arial", 28), bg='#ffffff', fg='#c00', bd=0, relief=tk.FLAT, command=overlay.destroy)
        cancel_btn.place(relx=0.05, rely=0.6, anchor='w', width=60, height=60)
        move_btn = tk.Button(overlay, text='⇲', font=("Arial", 28), bg='#ffffff', fg='#222', bd=0, relief=tk.FLAT)
        move_btn.place(relx=0.05, rely=0.7, anchor='w', width=60, height=60)
        def start_move(event):
            overlay._drag_start_x = event.x
            overlay._drag_start_y = event.y
        def do_move(event):
            nx = overlay.winfo_x() + event.x - overlay._drag_start_x
            ny = overlay.winfo_y() + event.y - overlay._drag_start_y
            overlay.geometry(f"{overlay.winfo_width()}x{overlay.winfo_height()}+{nx}+{ny}")
        move_btn.bind('<Button-1>', start_move)
        move_btn.bind('<B1-Motion>', do_move)
        def on_screenshot():
            overlay.destroy()
            self.show_crop_popup('full_screenshot.png', on_save)

    def show_crop_popup(self, image_path, on_save=None):
        from PIL import Image, ImageTk
        crop_win = tk.Toplevel(self.master)
        crop_win.title("Crop Screenshot")
        crop_win.transient(self.master)
        crop_win.resizable(True, True)
        img = Image.open(image_path)
        tk_img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(crop_win, width=img.width, height=img.height, cursor="cross")
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        crop_win.tk_img = tk_img
        rect = [None]
        start_x = [0]
        start_y = [0]
        def on_press(event):
            start_x[0] = event.x
            start_y[0] = event.y
            if rect[0]:
                canvas.delete(rect[0])
            rect[0] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="#4CAF50", width=2)
        def on_drag(event):
            if rect[0]:
                canvas.coords(rect[0], start_x[0], start_y[0], event.x, event.y)
        def on_release(event):
            if rect[0]:
                x1, y1, x2, y2 = canvas.coords(rect[0])
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                if x2 > x1 and y2 > y1:
                    cropped = img.crop((x1, y1, x2, y2))
                    import uuid
                    img_path = f'cropped_condition_{uuid.uuid4().hex}.png'
                    cropped.save(img_path)
                    crop_win.destroy()
                    self.show_condition_details_modal(img_path, on_save)
        canvas.bind('<ButtonPress-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)

    def show_condition_details_modal(self, cropped_img_path, on_save=None):
        import tkinter.ttk as ttk
        from PIL import Image, ImageTk
        modal = tk.Toplevel(self.master)
        modal.title("Condition")
        modal.transient(self.master)
        modal.resizable(False, False)
        modal.configure(bg="#18221B")
        w, h = 420, 540
        self.master.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (w // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")
        topbar = tk.Frame(modal, bg="#232D23")
        topbar.pack(fill=tk.X, pady=(0, 0))
        close_btn = tk.Button(topbar, text="✕", font=("Arial", 18), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        close_btn.pack(side=tk.LEFT, padx=16, pady=8)
        title = tk.Label(topbar, text="Condition", font=("Arial", 18, "bold"), fg="white", bg="#232D23")
        title.pack(side=tk.LEFT, padx=10, pady=8)
        delete_btn = tk.Button(topbar, text="🗑️", font=("Arial", 16), bd=0, command=modal.destroy, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        delete_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        def save_and_close():
            cond = {
                'name': name_entry.get(),
                'image_path': cropped_img_path,
                'det_type': det_type_var.get(),
                'status': 'Present',
            }
            if on_save:
                on_save(cond)
            modal.destroy()
        save_btn = tk.Button(topbar, text="💾", font=("Arial", 16), bd=0, command=save_and_close, cursor="hand2", bg="#232D23", fg="#4CAF50", activebackground="#232D23", activeforeground="#4CAF50")
        save_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        name_frame = tk.Frame(modal, bg="#18221B")
        name_frame.pack(fill=tk.X, padx=24, pady=(16, 8))
        name_label = tk.Label(name_frame, text="Name", font=("Arial", 11), fg="#B0FFB0", bg="#18221B", anchor="w")
        name_label.pack(fill=tk.X, anchor="w")
        name_entry = tk.Entry(name_frame, font=("Arial", 15), bg="#232D23", fg="white", insertbackground="white", relief=tk.FLAT, highlightthickness=2, highlightcolor="#4CAF50")
        name_entry.pack(fill=tk.X, ipady=7)
        name_entry.insert(0, "Condition")
        det_frame = tk.Frame(modal, bg="#233024", bd=0)
        det_frame.pack(fill=tk.X, padx=24, pady=(8, 8))
        img = Image.open(cropped_img_path)
        img.thumbnail((320, 120))
        tk_img = ImageTk.PhotoImage(img)
        img_label = tk.Label(det_frame, image=tk_img, bg="#233024")
        img_label.image = tk_img
        img_label.pack(pady=(12, 8))
        vis_frame = tk.Frame(det_frame, bg="#233024")
        vis_frame.pack(fill=tk.X, pady=(8, 0))
        vis_label = tk.Label(vis_frame, text="Visibility", font=("Arial", 11), fg="#B0FFB0", bg="#233024")
        vis_label.pack(side=tk.LEFT)
        vis_var = tk.StringVar(value="Present")
        vis_btn = tk.Button(vis_frame, text="✔ Present", font=("Arial", 13), bg="#233024", fg="#4CAF50", bd=0, relief=tk.FLAT, command=lambda: vis_var.set("Present"))
        vis_btn.pack(side=tk.LEFT, padx=10)
        det_type_frame = tk.Frame(det_frame, bg="#233024")
        det_type_frame.pack(fill=tk.X, pady=(8, 0))
        det_type_label = tk.Label(det_type_frame, text="Detection type", font=("Arial", 11), fg="#B0FFB0", bg="#233024")
        det_type_label.pack(side=tk.LEFT)
        det_type_var = tk.StringVar(value="Exact")
        det_type_options = [
            ("Exact", "🗔"),
            ("Screen", "📱"),
            ("Area", "⬚")
        ]
        def show_det_type_menu(event=None):
            menu = tk.Menu(modal, tearoff=0, bg="#232D23", fg="#4CAF50", font=("Arial", 12))
            for val, icon in det_type_options:
                menu.add_command(label=f"{icon}  {val}", command=lambda v=val: det_type_var.set(v))
            menu.tk_popup(det_type_btn.winfo_rootx(), det_type_btn.winfo_rooty() + det_type_btn.winfo_height())
        det_type_btn = tk.Button(det_type_frame, text=f"🗔  {det_type_var.get()} ▼", font=("Arial", 13), bg="#233024", fg="#4CAF50", bd=1, relief=tk.FLAT, command=show_det_type_menu)
        det_type_btn.pack(side=tk.LEFT, padx=10)
        def update_det_type(*args):
            icon = next((icon for val, icon in det_type_options if val == det_type_var.get()), "🗔")
            det_type_btn.config(text=f"{icon}  {det_type_var.get()} ▼")
        det_type_var.trace_add('write', update_det_type)
        slider_frame = tk.Frame(modal, bg="#233024")
        slider_frame.pack(fill=tk.X, padx=24, pady=(16, 0))
        slider_label = tk.Label(slider_frame, text="Sensitivity", font=("Arial", 11), fg="#B0FFB0", bg="#233024")
        slider_label.pack(anchor="w")
        slider = ttk.Scale(slider_frame, from_=0, to=10, orient=tk.HORIZONTAL)
        slider.set(5)
        slider.pack(fill=tk.X, pady=(4, 8))

    def show_alt_floating_overlay_bar(self, x, y):
        overlay = tk.Toplevel(self.master)
        overlay.title("Klick'r Overlay Alt")
        overlay.geometry(f"60x320+{x}+{y}")
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.95)
        overlay.config(bg="#000000")
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
        btn_frame = tk.Frame(overlay, bg="#000000")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        # Back (left arrow)
        left_btn = tk.Button(btn_frame, text="←", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        left_btn.pack(pady=(10, 32), fill=tk.X)
        # Record (solid circle)
        circle_btn = tk.Button(btn_frame, text="●", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        circle_btn.pack(pady=(0, 32), fill=tk.X)
        # Add (plus)
        plus_btn = tk.Button(btn_frame, text="＋", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        plus_btn.pack(pady=(0, 32), fill=tk.X)
        # Eye (solid diamond as fallback)
        eye_btn = tk.Button(btn_frame, text="◆", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        eye_btn.pack(pady=(0, 32), fill=tk.X)
        # Move (solid arrows)
        move_btn = tk.Button(btn_frame, text=" 1F1", font=("Arial", 26, "bold"), bg="#000000", fg="white", bd=0, relief=tk.FLAT, activebackground="#000000", activeforeground="white")
        move_btn.pack(pady=(0, 0), fill=tk.X)

    def search_scenarios(self):
        messagebox.showinfo("Search", "Search functionality to be implemented.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop() 
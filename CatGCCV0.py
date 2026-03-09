import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import platform
import pygame
import array

# --- ACCompiler 1.x ---
# Configuration: 600x400, /files = off

class ACCompiler:
    def __init__(self, root):
        self.root = root
        self.root.title("ACCompiler 1.x")
        self.root.geometry("600x400")
        
        # Initialize Pygame Mixer for sound feedback
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        
        # UI Setup
        self.setup_ui()
        
    def setup_ui(self):
        # Top Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        # "/files = off" implies no Open/Save dialogs, strictly compile in-memory or temp
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        self.build_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.build_menu.add_command(label="Compile & Run", command=self.compile_run, accelerator="F5")
        self.menu_bar.add_cascade(label="Build", menu=self.build_menu)
        
        self.root.config(menu=self.menu_bar)
        
        # Main Editor Area
        self.editor_frame = tk.Frame(self.root)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_editor = tk.Label(self.editor_frame, text="Source Code (C):")
        self.lbl_editor.pack(anchor="w")
        
        self.code_area = scrolledtext.ScrolledText(self.editor_frame, width=70, height=15, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.code_area.pack(fill=tk.BOTH, expand=True)
        
        # Default template
        self.code_area.insert(tk.END, '#include <stdio.h>\n\nint main() {\n    printf("Hello from ACCompiler 1.x!");\n    return 0;\n}\n')
        
        # Output/Console Area
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_output = tk.Label(self.output_frame, text="Compiler Output:")
        self.lbl_output.pack(anchor="w")
        
        self.output_area = scrolledtext.ScrolledText(self.output_frame, height=8, state='disabled', bg="black", fg="#00ff00")
        self.output_area.pack(fill=tk.BOTH, expand=True)
        
        # Key Bindings
        self.root.bind('<F5>', lambda e: self.compile_run())

    def play_sound(self, success=True):
        """Generates a simple beep using pygame."""
        sample_rate = 22050
        duration = 0.1
        
        if success:
            # High pitch beep
            freq = 880
        else:
            # Low pitch buzz
            freq = 220
            
        # Generate sine wave array
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        amplitude = 4096 # Volume
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(amplitude * (2 ** 15 - 1) * 0.5 * (1 if (int(t * freq * 2) % 2) else -1))
            buf[i] = val

        try:
            sound = pygame.mixer.Sound(buffer=buf)
            sound.play()
            pygame.time.delay(int(duration * 1000))
        except Exception as e:
            print(f"Sound error: {e}")

    def log_output(self, message):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def compile_run(self):
        code = self.code_area.get("1.0", tk.END)
        source_file = "ac_temp.c"
        exe_file = "ac_temp.exe" if platform.system() == "Windows" else "./ac_temp"

        # Clean up previous builds if they exist
        try:
            if os.path.exists(source_file): os.remove(source_file)
            if os.path.exists(exe_file): os.remove(exe_file)
        except OSError:
            pass

        # Write temp source
        with open(source_file, "w") as f:
            f.write(code)

        self.log_output(">> Compiling with GCC...")
        
        # Check for GCC
        compiler = "gcc"
        try:
            # Compile command
            result = subprocess.run([compiler, source_file, "-o", exe_file], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_output(">> Compilation Successful!")
                self.play_sound(success=True)
                
                self.log_output(">> Running Program...")
                self.log_output("-" * 30)
                
                # Run command
                run_result = subprocess.run([exe_file], capture_output=True, text=True, timeout=5)
                
                self.log_output(run_result.stdout)
                if run_result.stderr:
                    self.log_output(run_result.stderr)
                    
                self.log_output("-" * 30)
                self.log_output(f">> Process finished (Return code: {run_result.returncode})")
            else:
                self.play_sound(success=False)
                self.log_output(">> Compilation Failed!")
                self.log_output(result.stderr)

        except FileNotFoundError:
            self.play_sound(success=False)
            self.log_output(">> Error: GCC compiler not found. Please install MinGW or GCC and ensure it is in your PATH.")
        except subprocess.TimeoutExpired:
            self.log_output(">> Error: Execution timed out.")
        except Exception as e:
            self.log_output(f">> Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ACCompiler(root)
    root.mainloop()

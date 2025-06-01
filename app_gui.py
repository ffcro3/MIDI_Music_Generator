# app_gui.py

import os
import datetime # Para criar nomes de pastas com data/hora
import re       # Para limpar o nome do projeto
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Esconde o prompt de inicialização do Pygame

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import platform
import subprocess
import random
import tempfile
import mido
import pygame

# Importe sua classe MusicGenerator e MidiVisualizer
from music_generator import MusicGenerator
from midi_visualizer import MidiVisualizer # Assumindo que esta classe está em midi_visualizer.py

class TranceGenGUI:
    def __init__(self, master):
        self.master = master
        master.title("Liquid Funk Music Generator") 
        master.geometry("1000x800")

        self.music_generator = MusicGenerator()

        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            self.log_mixer_init = "Pygame mixer inicializado com sucesso."
        except Exception as e:
            self.log_mixer_init = f"AVISO: Não foi possível inicializar o Pygame mixer. A reprodução MIDI pode não funcionar. Erro: {e}"

        # Variáveis de controle
        self.project_name_var = tk.StringVar(value='MeuProjetoMusical') # Novo: Nome do Projeto
        self.bpm_var = tk.IntVar(value=174)
        self.duration_measures_var = tk.IntVar(value=16)
        self.root_key_var = tk.StringVar(value='A')
        
        self.scale_options = sorted(list(self.music_generator.scales.keys()))
        self.scale_type_var = tk.StringVar(value='Minor')

        # BooleanVars para controle das partes
        self.generate_bass_var = tk.BooleanVar(value=True) 
        self.generate_chords_var = tk.BooleanVar(value=True)
        self.generate_lead_var = tk.BooleanVar(value=True)
        self.generate_pads_var = tk.BooleanVar(value=True)
        self.generate_arpeggio_var = tk.BooleanVar(value=False)
        self.generate_drums_var = tk.BooleanVar(value=True)

        self.selected_style_var = tk.StringVar(value='Drum and Bass')

        # Configuração da UI
        self.setup_ui()

        # Área de log
        self.log_text_area = scrolledtext.ScrolledText(master, height=10, state='disabled', wrap=tk.WORD)
        self.log_text_area.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.log_text_area.insert(tk.END, self.log_mixer_init + "\n")
        self.log_text_area.see(tk.END)

        # Variáveis de estado da reprodução MIDI
        self.playing_midi = False
        self.midi_file_path = None # Caminho do MIDI completo temporário (para reprodução)
        self.midi_player = None 
        self.update_progress_job = None
        self.start_playback_time = 0

        # Dados do MIDI gerado para reprodução e visualização
        self.generated_all_midi_events = None
        self.generated_total_ticks = 0
        self.generated_us_per_beat = 0
        self.generated_bpm = 0
        
        # current_project_base_dir agora é apenas um indicador da pasta base do projeto,
        # a pasta de sessão completa é criada/verificada no momento do salvamento.
        self.current_project_base_dir = None 
        self.temp_midi_file_for_playback = None # Caminho para o MIDI temporário de reprodução

    def setup_ui(self):
        control_frame = ttk.LabelFrame(self.master, text="Controles de Geração Liquid Funk")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        control_frame.columnconfigure(1, weight=1)

        row_idx = 0

        ttk.Label(control_frame, text=f"Estilo Musical: {self.selected_style_var.get()}").grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        row_idx += 1
        
        # NOVO CAMPO: Nome do Projeto
        ttk.Label(control_frame, text="Nome do Projeto:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(control_frame, textvariable=self.project_name_var).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(control_frame, text="BPM:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(control_frame, from_=160, to=180, textvariable=self.bpm_var, wrap=True).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(control_frame, text="Duração (Compassos):").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(control_frame, textvariable=self.duration_measures_var).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(control_frame, text="Tônica:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(control_frame, textvariable=self.root_key_var,
                     values=['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
                     state='readonly').grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(control_frame, text="Tipo de Escala:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(control_frame, textvariable=self.scale_type_var,
                     values=self.scale_options, state='readonly').grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        parts_frame = ttk.LabelFrame(control_frame, text="Gerar Partes:")
        parts_frame.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Checkbutton(parts_frame, text="Baixo", variable=self.generate_bass_var).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(parts_frame, text="Acordes", variable=self.generate_chords_var).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(parts_frame, text="Melodia", variable=self.generate_lead_var).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(parts_frame, text="Pads", variable=self.generate_pads_var).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(parts_frame, text="Arpejo", variable=self.generate_arpeggio_var).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(parts_frame, text="Bateria", variable=self.generate_drums_var).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        row_idx += 1

        # Botões de ação
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1) 

        ttk.Button(button_frame, text="Gerar MIDI", command=self.generate_music).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Reproduzir MIDI", command=self.play_midi).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Parar Reprodução", command=self.stop_midi_playback).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        save_menubutton = ttk.Menubutton(button_frame, text="Salvar MIDI")
        save_menubutton.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        save_menu = tk.Menu(save_menubutton, tearoff=0)
        save_menu.add_command(label="Salvar MIDI Completo...", command=self.save_midi_full_to_default_location)
        save_menu.add_command(label="Salvar Partes Separadas...", command=self.save_midi_parts_to_default_location)
        save_menubutton["menu"] = save_menu
        
        row_idx += 1

        ttk.Button(control_frame, text="Abrir Pasta de MIDIs Gerados", command=self.open_generated_midi_folder).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Visualizador MIDI e Barras de Rolagem
        visualizer_frame = ttk.Frame(self.master)
        visualizer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        visualizer_frame.grid_rowconfigure(0, weight=1)
        visualizer_frame.grid_columnconfigure(0, weight=1)

        self.midi_visualizer = MidiVisualizer(visualizer_frame, total_ticks=1, bg="grey", height=300)
        self.midi_visualizer.grid(row=0, column=0, sticky="nsew")

        self.midi_visualizer.vbar.grid(row=0, column=1, sticky="ns")
        self.midi_visualizer.hbar.grid(row=1, column=0, sticky="ew")

    def log_message(self, message):
        self.log_text_area.config(state="normal")
        self.log_text_area.insert(tk.END, message + "\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.config(state="disabled")

    def clean_filename(self, filename):
        """Remove caracteres inválidos para nomes de arquivo e diretório."""
        # Remove caracteres que não são letras, números, espaços, hífens ou underscores
        cleaned_name = re.sub(r'[^\w\s-]', '', filename)
        # Substitui espaços por underscores e remove múltiplos underscores
        cleaned_name = re.sub(r'\s+', '_', cleaned_name)
        cleaned_name = re.sub(r'__+', '_', cleaned_name)
        # Remove underscores do início ou fim
        cleaned_name = cleaned_name.strip('_')
        return cleaned_name if cleaned_name else "SemNome" # Garante que não retorne vazio

    def get_current_project_session_dir(self):
        """
        Retorna o caminho completo da pasta de sessão do projeto atual,
        criando-a se não existir.
        """
        project_name = self.clean_filename(self.project_name_var.get())
        if not project_name: # Garante que haja um nome de projeto
            project_name = "Projeto_Anonimo"
            self.project_name_var.set(project_name) # Atualiza a var com o nome padrão

        base_midi_dir = os.path.join(os.getcwd(), "MIDI")
        session_dir = os.path.join(base_midi_dir, project_name)
        
        os.makedirs(session_dir, exist_ok=True) # Cria a pasta se não existir
        return session_dir

    def generate_music(self):
        root_key = self.root_key_var.get()
        scale_type = self.scale_type_var.get()
        bpm = self.bpm_var.get()
        
        num_measures = self.duration_measures_var.get()
        num_beats = num_measures * 4 

        generate_bass = self.generate_bass_var.get()
        generate_chords = self.generate_chords_var.get()
        generate_lead = self.generate_lead_var.get()
        generate_pads = self.generate_pads_var.get()
        generate_arpeggio = self.generate_arpeggio_var.get()
        generate_drums = self.generate_drums_var.get()
        selected_style = self.selected_style_var.get() 

        project_name_for_log = self.clean_filename(self.project_name_var.get()) # Apenas para log

        self.log_message(f"Gerando MIDI para {selected_style} (Projeto: {project_name_for_log}, BPM: {bpm}, Duração: {num_measures} compassos)...")
        self.stop_midi_playback() 

        try:
            all_midi_events, log_details, total_ticks, us_per_beat = self.music_generator.generate_music_parts(
                root_key, scale_type, bpm, num_beats,
                generate_bass, generate_chords, generate_lead, generate_pads, generate_arpeggio,
                generate_drums,
                selected_style
            )
            self.log_message(log_details)

            self.generated_all_midi_events = all_midi_events
            self.generated_total_ticks = total_ticks
            self.generated_us_per_beat = us_per_beat
            self.generated_bpm = bpm

            # Salvar MIDI em um arquivo temporário para REPRODUÇÃO
            if self.temp_midi_file_for_playback and os.path.exists(self.temp_midi_file_for_playback):
                os.remove(self.temp_midi_file_for_playback) 

            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi_file:
                self.temp_midi_file_for_playback = tmp_midi_file.name

            self.music_generator.save_midi_file(all_midi_events, self.temp_midi_file_for_playback, bpm)
            self.midi_file_path = self.temp_midi_file_for_playback 

            self.log_message(f"MIDI gerado e salvo temporariamente para reprodução em: {self.midi_file_path}")

            # Define o current_project_base_dir para o botão "Abrir Pasta"
            # O diretório real de salvamento é calculado no momento do save
            self.current_project_base_dir = self.get_current_project_session_dir()
            self.log_message(f"Pasta base do projeto definida: {self.current_project_base_dir}")


            # Atualização do Visualizador
            self.midi_visualizer.set_midi_data(all_midi_events, self.music_generator.ticks_per_beat)
            self.midi_visualizer.xview_moveto(0) 
            self.midi_visualizer.yview_moveto(0) 

            #messagebox.showinfo("Sucesso", "Música MIDI gerada e visualizada com sucesso! Agora você pode salvá-la no diretório padrão.")

        except Exception as e:
            messagebox.showerror("Erro de Geração", f"Ocorreu um erro ao gerar a música MIDI: {e}")
            self.log_message(f"ERRO: {e}")

    def play_midi(self):
        if not self.midi_file_path or not os.path.exists(self.midi_file_path):
            messagebox.showwarning("Aviso", "Nenhum arquivo MIDI gerado para reproduzir. Gere a música primeiro.")
            return

        self.stop_midi_playback() 

        try:
            pygame.mixer.music.load(self.midi_file_path)
            pygame.mixer.music.play()
            self.playing_midi = True
            self.start_playback_time = pygame.time.get_ticks() / 1000.0 
            self.update_progress_line() 
            self.log_message("Reproduzindo MIDI...")
        except pygame.error as e:
            messagebox.showerror("Erro de Reprodução", f"Não foi possível reproduzir o MIDI. Verifique se os codecs estão instalados ou se o arquivo é válido. Erro: {e}")
            self.log_message(f"ERRO de reprodução Pygame: {e}")

    def stop_midi_playback(self):
        if self.playing_midi:
            pygame.mixer.music.stop() 
            self.playing_midi = False
            if self.update_progress_job:
                self.master.after_cancel(self.update_progress_job) 
                self.update_progress_job = None
            self.midi_visualizer.update_progress_line(0) 
            self.log_message("Reprodução MIDI parada.")

    def save_midi_full_to_default_location(self):
        """Salva o MIDI completo no diretório de sessão atual do projeto, com timestamp no nome do arquivo."""
        if not self.generated_all_midi_events:
            messagebox.showwarning("Aviso", "Nenhum MIDI gerado para salvar. Gere a música primeiro.")
            return

        session_dir = self.get_current_project_session_dir() # Obtém o diretório ATUALIZADO
        if not session_dir: # Fallback caso get_current_project_session_dir falhe inesperadamente
            messagebox.showerror("Erro de Salvamento", "Não foi possível determinar o diretório para salvar. Tente novamente.")
            return

        try:
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            full_midi_filename = os.path.join(session_dir, f"Full_Mix_{timestamp_file}.mid")
            self.music_generator.save_midi_file(self.generated_all_midi_events, full_midi_filename, self.generated_bpm)
            self.log_message(f"MIDI completo salvo em: {full_midi_filename}")
            messagebox.showinfo("Sucesso", f"MIDI completo salvo em:\n{full_midi_filename}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo MIDI completo: {e}")
            self.log_message(f"ERRO ao salvar MIDI completo: {e}")

    def save_midi_parts_to_default_location(self):
        """Salva as partes MIDI separadamente no diretório de sessão atual do projeto, com timestamp nos nomes dos arquivos."""
        if not self.generated_all_midi_events:
            messagebox.showwarning("Aviso", "Nenhum MIDI gerado para salvar. Gere a música primeiro.")
            return

        session_dir = self.get_current_project_session_dir() # Obtém o diretório ATUALIZADO
        if not session_dir: # Fallback caso get_current_project_session_dir falhe inesperadamente
            messagebox.showerror("Erro de Salvamento", "Não foi possível determinar o diretório para salvar as partes. Tente novamente.")
            return

        try:
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            for part_name, events in self.generated_all_midi_events.items():
                if events:
                    # Formata o nome da pasta (ex: "Baixo", "Acordes")
                    part_dir_name = part_name.replace(' ', '_').capitalize()
                    part_dir = os.path.join(session_dir, part_dir_name)
                    os.makedirs(part_dir, exist_ok=True)
                    
                    # Formata o nome do arquivo (ex: "baixo_YYYYMMDD_HHMMSS.mid")
                    part_filename = os.path.join(part_dir, f"{part_name.replace(' ', '_').lower()}_{timestamp_file}.mid")
                    
                    temp_midi_events = {part_name: events} 
                    self.music_generator.save_midi_file(temp_midi_events, part_filename, self.generated_bpm)
                    self.log_message(f"Parte '{part_name}' salva em: {part_filename}")
            
            messagebox.showinfo("Sucesso", f"Partes MIDI salvas separadamente na pasta:\n{session_dir}")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar Partes", f"Ocorreu um erro ao salvar as partes MIDI: {e}")
            self.log_message(f"ERRO ao salvar partes MIDI: {e}")

    def update_progress_line(self):
        if self.playing_midi and pygame.mixer.music.get_busy():
            elapsed_ms = pygame.mixer.music.get_pos() 
            elapsed_seconds = elapsed_ms / 1000.0 

            if self.generated_us_per_beat > 0 and self.music_generator.ticks_per_beat > 0:
                current_ticks = mido.second2tick(elapsed_seconds, self.music_generator.ticks_per_beat, self.generated_us_per_beat)
            else:
                current_ticks = 0

            if current_ticks <= self.generated_total_ticks:
                self.midi_visualizer.update_progress_line(current_ticks)
            else:
                self.stop_midi_playback()
                return

            self.update_progress_job = self.master.after(50, self.update_progress_line)
        else:
            self.stop_midi_playback() 

    def open_generated_midi_folder(self):
        """Abre a pasta de sessão do projeto atual no explorador de arquivos do sistema."""
        session_dir = self.get_current_project_session_dir() # Obtém o diretório ATUALIZADO
        
        if not session_dir or not os.path.exists(session_dir):
            messagebox.showwarning("Aviso", "Nenhum diretório de projeto válido encontrado ou a pasta ainda não foi criada. Gere a música ou salve algo primeiro.")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(session_dir)
            elif platform.system() == "Darwin": # macOS
                subprocess.Popen(["open", session_dir])
            else: # Linux
                subprocess.Popen(["xdg-open", session_dir])
            self.log_message(f"Abrindo pasta de MIDIs gerados: {session_dir}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta. Erro: {e}")
            self.log_message(f"ERRO ao abrir pasta: {e}")

    # Certifique-se de que quaisquer arquivos temporários sejam limpos ao fechar o app
    def on_closing(self):
        if self.temp_midi_file_for_playback and os.path.exists(self.temp_midi_file_for_playback):
            os.remove(self.temp_midi_file_for_playback)
            self.log_message(f"Arquivo temporário '{self.temp_midi_file_for_playback}' removido.")
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranceGenGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) 
    root.mainloop()
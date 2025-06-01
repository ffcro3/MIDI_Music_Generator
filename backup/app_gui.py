# app_gui.py

import os
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
        master.title("Liquid Funk Music Generator") # Título mais específico para o gênero
        master.geometry("1000x800")

        self.music_generator = MusicGenerator()

        # Inicializar Pygame Mixer (para reprodução de áudio/MIDI)
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8) # Define 8 canais para diversas partes
            self.log_mixer_init = "Pygame mixer inicializado com sucesso."
        except Exception as e:
            self.log_mixer_init = f"AVISO: Não foi possível inicializar o Pygame mixer. A reprodução MIDI pode não funcionar. Erro: {e}"

        # Variáveis de controle
        self.bpm_var = tk.IntVar(value=174) # BPM padrão para Drum and Bass/Liquid Funk
        # Alterado de 'beats' para 'measures' (compassos)
        self.duration_measures_var = tk.IntVar(value=16) # Duração padrão em compassos (ex: 16 compassos = 64 beats em 4/4)
        self.root_key_var = tk.StringVar(value='A') # Tônica padrão para Liquid Funk
        self.scale_type_var = tk.StringVar(value='Minor') # Escala menor é comum em Liquid Funk
        self.save_path_var = tk.StringVar(value=os.getcwd()) # Caminho padrão para salvar

        # BooleanVars para controle das partes (ajustado para o foco no Liquid Funk)
        self.generate_bass_var = tk.BooleanVar(value=True) # Baixo é essencial
        self.generate_chords_var = tk.BooleanVar(value=True) # Acordes e Pads são importantes
        self.generate_lead_var = tk.BooleanVar(value=True) # Melodia lead
        self.generate_pads_var = tk.BooleanVar(value=True) # Pads são uma marca do Liquid Funk
        self.generate_arpeggio_var = tk.BooleanVar(value=False) # Arpejo pode ser menos proeminente, mas opcional
        self.generate_drums_var = tk.BooleanVar(value=True) # Bateria é a espinha dorsal do DnB

        # Estilo musical (agora fixo para "Drum and Bass" ou "Liquid Funk" conforme seu gerador)
        # Se você adicionou "Liquid Funk" como uma chave separada no music_styles_data do MusicGenerator,
        # altere a linha abaixo para 'Liquid Funk'. Caso contrário, 'Drum and Bass' é a chave usada.
        self.selected_style_var = tk.StringVar(value='Drum and Bass') # Valor padrão fixo e único

        # Configuração da UI
        self.setup_ui()

        # Visualizador MIDI
        self.midi_visualizer = MidiVisualizer(master, total_ticks=1, bg="grey", height=300, scrollregion=(0,0,1,1))
        self.midi_visualizer.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configura as linhas e colunas para expandir
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Área de log
        self.log_text_area = scrolledtext.ScrolledText(master, height=10, state='disabled', wrap=tk.WORD)
        self.log_text_area.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.log_text_area.insert(tk.END, self.log_mixer_init + "\n")
        self.log_text_area.see(tk.END)

        # Variáveis de estado da reprodução MIDI
        self.playing_midi = False
        self.midi_file_path = None
        self.midi_player = None # Não diretamente usado para pygame.mixer.music
        self.update_progress_job = None
        self.start_playback_time = 0

        # Dados do MIDI gerado para reprodução e visualização
        self.generated_all_midi_events = None
        self.generated_total_ticks = 0
        self.generated_us_per_beat = 0
        self.generated_bpm = 0

    def setup_ui(self):
        control_frame = ttk.LabelFrame(self.master, text="Controles de Geração Liquid Funk") # Título do frame
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        control_frame.columnconfigure(1, weight=1) # Coluna para Spinbox/Entry/Combobox expande

        row_idx = 0

        # Exibe o estilo musical fixo (não há mais seleção)
        ttk.Label(control_frame, text=f"Estilo Musical: {self.selected_style_var.get()}").grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        row_idx += 1

        # BPM
        ttk.Label(control_frame, text="BPM:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(control_frame, from_=160, to=180, textvariable=self.bpm_var, wrap=True).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew") # Faixa de BPM típica para DnB
        row_idx += 1

        # Duração em Compassos (Medidas)
        ttk.Label(control_frame, text="Duração (Compassos):").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(control_frame, textvariable=self.duration_measures_var).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Tônica
        ttk.Label(control_frame, text="Tônica:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(control_frame, textvariable=self.root_key_var,
                     values=['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
                     state='readonly').grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Tipo de Escala
        ttk.Label(control_frame, text="Tipo de Escala:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Combobox(control_frame, textvariable=self.scale_type_var,
                     values=['Major', 'Minor'], state='readonly').grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Checkboxes para partes musicais
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

        ttk.Button(button_frame, text="Gerar MIDI", command=self.generate_music_only).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Reproduzir MIDI", command=self.play_midi).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Parar Reprodução", command=self.stop_midi_playback).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        row_idx += 1

        ttk.Button(control_frame, text="Salvar MIDI Como...", command=self.save_midi_as).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        row_idx += 1

    def log_message(self, message):
        self.log_text_area.config(state="normal")
        self.log_text_area.insert(tk.END, message + "\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.config(state="disabled")

    # Esta função não é mais necessária, pois o estilo é fixo.
    def _update_bpm_for_style(self):
        pass

    def generate_music_only(self):
        root_key = self.root_key_var.get()
        scale_type = self.scale_type_var.get()
        bpm = self.bpm_var.get()
        
        # OBTÉM A DURAÇÃO EM COMPASSOS E CONVERTE PARA BEATS
        num_measures = self.duration_measures_var.get()
        num_beats = num_measures * 4 # Assumindo compasso 4/4 (4 beats por compasso)

        generate_bass = self.generate_bass_var.get()
        generate_chords = self.generate_chords_var.get()
        generate_lead = self.generate_lead_var.get()
        generate_pads = self.generate_pads_var.get()
        generate_arpeggio = self.generate_arpeggio_var.get()
        generate_drums = self.generate_drums_var.get()
        selected_style = self.selected_style_var.get() # Será 'Drum and Bass' ou 'Liquid Funk'

        self.log_message(f"Gerando MIDI para {selected_style} (BPM: {bpm}, Duração: {num_measures} compassos)...")
        self.stop_midi_playback() # Para qualquer reprodução anterior

        try:
            # Chama o gerador de música com os parâmetros da GUI
            all_midi_events, log_details, total_ticks, us_per_beat = self.music_generator.generate_music_parts(
                root_key, scale_type, bpm, num_beats, # Passa num_beats para o gerador
                generate_bass, generate_chords, generate_lead, generate_pads, generate_arpeggio,
                generate_drums,
                selected_style
            )
            self.log_message(log_details)

            # Armazena os dados gerados para reprodução e visualização
            self.generated_all_midi_events = all_midi_events
            self.generated_total_ticks = total_ticks
            self.generated_us_per_beat = us_per_beat
            self.generated_bpm = bpm

            # Salva o MIDI em um arquivo temporário para reprodução
            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi_file:
                self.midi_file_path = tmp_midi_file.name

            self.music_generator.save_midi_file(all_midi_events, self.midi_file_path, bpm)

            self.log_message(f"MIDI gerado e salvo temporariamente em: {self.midi_file_path}")

            # Atualiza o visualizador MIDI
            self.midi_visualizer.total_ticks = total_ticks
            self.midi_visualizer.set_midi_data(all_midi_events, self.music_generator.ticks_per_beat)
            self.midi_visualizer.redraw_notes()
            self.midi_visualizer.xview_moveto(0) # Volta ao início da visualização

            messagebox.showinfo("Sucesso", "Música MIDI gerada e visualizada com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro de Geração", f"Ocorreu um erro ao gerar a música MIDI: {e}")
            self.log_message(f"ERRO: {e}")

    def play_midi(self):
        if not self.midi_file_path or not os.path.exists(self.midi_file_path):
            messagebox.showwarning("Aviso", "Nenhum arquivo MIDI gerado para reproduzir.")
            return

        self.stop_midi_playback() # Garante que nada esteja tocando antes de iniciar

        try:
            pygame.mixer.music.load(self.midi_file_path)
            pygame.mixer.music.play()
            self.playing_midi = True
            self.start_playback_time = pygame.time.get_ticks() / 1000.0 # Tempo de início para a linha de progresso
            self.update_progress_line() # Inicia a atualização da linha de progresso
            self.log_message("Reproduzindo MIDI...")
        except pygame.error as e:
            messagebox.showerror("Erro de Reprodução", f"Não foi possível reproduzir o MIDI. Verifique se os codecs estão instalados ou se o arquivo é válido. Erro: {e}")
            self.log_message(f"ERRO de reprodução Pygame: {e}")

    def stop_midi_playback(self):
        if self.playing_midi:
            pygame.mixer.music.stop() # Para a reprodução
            self.playing_midi = False
            if self.update_progress_job:
                self.master.after_cancel(self.update_progress_job) # Cancela a atualização da linha de progresso
                self.update_progress_job = None
            self.midi_visualizer.update_progress_line(0) # Reseta a linha de progresso
            self.log_message("Reprodução MIDI parada.")

    def save_midi_as(self):
        if not self.generated_all_midi_events:
            messagebox.showwarning("Aviso", "Nenhum MIDI gerado para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")],
            initialdir=self.save_path_var.get(),
            title="Salvar Arquivo MIDI Como"
        )
        if file_path:
            try:
                import shutil
                shutil.copy(self.midi_file_path, file_path) # Copia o arquivo temporário para o destino escolhido
                self.save_path_var.set(os.path.dirname(file_path)) # Atualiza o último diretório salvo
                self.log_message(f"MIDI salvo em: {file_path}")
                messagebox.showinfo("Sucesso", f"Arquivo MIDI salvo em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo MIDI: {e}")
                self.log_message(f"ERRO ao salvar: {e}")

    def update_progress_line(self):
        if self.playing_midi and pygame.mixer.music.get_busy():
            elapsed_ms = pygame.mixer.music.get_pos() # Tempo decorrido em milissegundos
            elapsed_seconds = elapsed_ms / 1000.0 # Converte para segundos

            if self.generated_us_per_beat > 0 and self.music_generator.ticks_per_beat > 0:
                current_ticks = mido.second2tick(elapsed_seconds, self.music_generator.ticks_per_beat, self.generated_us_per_beat)
            else:
                current_ticks = 0

            # Atualiza a linha de progresso no visualizador
            if current_ticks <= self.generated_total_ticks:
                self.midi_visualizer.update_progress_line(current_ticks)
            else:
                # Se a reprodução for além do total_ticks, para
                self.stop_midi_playback()
                return

            # Agenda a próxima atualização
            self.update_progress_job = self.master.after(50, self.update_progress_line)
        else:
            self.stop_midi_playback() # Para a reprodução se ela não estiver mais ativa

    # Esta função open_midi_file é um resquício, não sendo mais usada para reprodução
    # mas sim para abrir o MIDI com o programa padrão do sistema.
    def open_midi_file(self, filename):
        try:
            if platform.system() == "Windows":
                os.startfile(filename)
            elif platform.system() == "Darwin": # macOS
                subprocess.Popen(["open", filename])
            else: # Linux
                subprocess.Popen(["xdg-open", filename])
            self.log_text_area.config(state="normal")
            self.log_text_area.insert(tk.END, f"Tentando abrir '{filename}' com o reprodutor padrão (apenas para visualização/edição externa)...\n")
            self.log_text_area.config(state="disabled")
        except Exception as e:
            self.log_text_area.config(state="normal")
            self.log_text_area.insert(tk.END, f"Não foi possível abrir o arquivo MIDI externamente. Erro: {e}\n")
            self.log_text_area.config(state="disabled")
            messagebox.showwarning("Aviso", f"Não foi possível abrir o arquivo MIDI externamente. Por favor, abra-o manualmente.\nErro: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranceGenGUI(root)
    root.mainloop()
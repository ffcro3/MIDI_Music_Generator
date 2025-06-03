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
import datetime # Para criar nomes de pastas com data/hora
import re       # Para limpar o nome do projeto
import pygame

# Importe sua classe MusicGenerator e MidiVisualizer
from music_generator import MusicGenerator
from midi_visualizer import MidiVisualizer # Assumindo que esta classe está em midi_visualizer.py

class TranceGenGUI:
    def __init__(self, master):
        self.master = master
        
        # Título da aplicação - Agora mais genérico para múltiplos gêneros
        master.title("Gerador de Música Eletrônica") 
        master.geometry("1000x800")

        self.music_generator = MusicGenerator()

        # Inicializar Pygame Mixer (para reprodução de áudio/MIDI)
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8) # Define 8 canais para diversas partes
            self.log_mixer_init = "Pygame mixer inicializado com sucesso."
        except Exception as e:
            self.log_mixer_init = f"AVISO: Não foi possível inicializar o Pygame mixer. A reprodução MIDI pode não funcionar. Erro: {e}"

        # Variáveis de controle da GUI
        self.project_name_var = tk.StringVar(value='MeuProjetoMusical') # Nome do Projeto para organização de pastas
        self.bpm_var = tk.IntVar(value=174) # BPM padrão (será atualizado pelo gênero)
        self.duration_measures_var = tk.IntVar(value=16) # Duração em compassos
        self.root_key_var = tk.StringVar(value='A') # Tônica
        
        # Opções de escala (carregadas do MusicGenerator)
        self.scale_options = sorted(list(self.music_generator.scales.keys()))
        self.scale_type_var = tk.StringVar(value='Minor') # Tipo de escala

        # BooleanVars para controle das partes a serem geradas
        self.generate_bass_var = tk.BooleanVar(value=True) 
        self.generate_chords_var = tk.BooleanVar(value=True)
        self.generate_lead_var = tk.BooleanVar(value=True)
        self.generate_pads_var = tk.BooleanVar(value=True)
        self.generate_arpeggio_var = tk.BooleanVar(value=False)
        self.generate_drums_var = tk.BooleanVar(value=True)

        # Variáveis e lista de gêneros para o dropdown
        self.available_genres = sorted(list(self.music_generator.genre_configs.keys()))
        # Seleciona o primeiro da lista ou "Drum and Bass" como fallback
        self.selected_genre_var = tk.StringVar(value=self.available_genres[0] if self.available_genres else "Drum and Bass") 

        # Variáveis de estado da reprodução MIDI
        self.playing_midi = False
        self.midi_file_path = None # Caminho do MIDI completo temporário (para reprodução)
        self.midi_player = None 
        self.update_progress_job = None
        self.start_playback_time = 0 # Tempo de início da reprodução para a linha de progresso
        self.music_bpm = 0 # BPM da música que está tocando para cálculo da linha de progresso

        # Dados do MIDI gerado para reprodução, visualização e salvamento
        self.generated_all_midi_events = None # Eventos MIDI completos
        self.generated_total_ticks = 0 # Total de ticks da música gerada
        self.generated_us_per_beat = 0 # Microsegundos por batida da música gerada
        self.generated_bpm = 0 # BPM da música gerada
        self.generated_instrument_programs = {} # Programas de instrumento usados na geração

        # current_project_base_dir agora é apenas um indicador da pasta base do projeto,
        # a pasta de sessão completa é criada/verificada no momento do salvamento.
        self.current_project_base_dir = None 
        self.temp_midi_file_for_playback = None # Caminho para o MIDI temporário de reprodução

        self.setup_ui() # Chama a função para construir a interface

        # Área de log (no final para ficar visível)
        self.log_text_area = scrolledtext.ScrolledText(master, height=10, state='disabled', wrap=tk.WORD)
        self.log_text_area.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.log_text_area.insert(tk.END, self.log_mixer_init + "\n")
        self.log_text_area.see(tk.END)

        # Chama a função para aplicar as configurações iniciais do gênero
        self._apply_genre_config() 

    def setup_ui(self):
        control_frame = ttk.LabelFrame(self.master, text="Controles de Geração Musical")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        control_frame.columnconfigure(1, weight=1) # Coluna para Spinbox/Entry/Combobox expande

        row_idx = 0

        # Dropdown para Seleção de Gênero
        ttk.Label(control_frame, text="Gênero:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        genre_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_genre_var, values=self.available_genres, state="readonly")
        genre_dropdown.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        genre_dropdown.bind("<<ComboboxSelected>>", self._on_genre_selected) 
        row_idx += 1
        
        # Campo: Nome do Projeto
        ttk.Label(control_frame, text="Nome do Projeto:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(control_frame, textvariable=self.project_name_var).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        ttk.Label(control_frame, text="BPM:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(control_frame, from_=60, to=220, textvariable=self.bpm_var, wrap=True).grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
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
        
        # Menu de Salvar MIDI (Completo e Partes Separadas)
        save_menubutton = ttk.Menubutton(button_frame, text="Salvar MIDI")
        save_menubutton.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        save_menu = tk.Menu(save_menubutton, tearoff=0)
        save_menu.add_command(label="Salvar MIDI Completo...", command=self.save_midi_full_to_default_location)
        save_menu.add_command(label="Salvar Partes Separadas...", command=self.save_midi_parts_to_default_location)
        save_menubutton["menu"] = save_menu
        
        row_idx += 1

        # Botão para Abrir Pasta de MIDIs Gerados
        ttk.Button(control_frame, text="Abrir Pasta de MIDIs Gerados", command=self.open_generated_midi_folder).grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Frame para o Visualizador MIDI e suas barras de rolagem
        visualizer_container_frame = ttk.Frame(self.master)
        visualizer_container_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configura o grid dentro do container para que o canvas e as barras de rolagem se expandam
        visualizer_container_frame.grid_rowconfigure(0, weight=1)
        visualizer_container_frame.grid_columnconfigure(0, weight=1)

        # Inicializa o visualizador com um total_ticks padrão (será atualizado)
        self.midi_visualizer = MidiVisualizer(visualizer_container_frame, total_ticks=1, bg="grey", height=300)
        self.midi_visualizer.grid(row=0, column=0, sticky="nsew") # Posiciona o canvas

        # CRIAÇÃO E POSICIONAMENTO CORRETO DAS BARRAS DE ROLAGEM
        # Barra de rolagem vertical
        vbar = ttk.Scrollbar(visualizer_container_frame, orient=tk.VERTICAL, command=self.midi_visualizer.yview)
        vbar.grid(row=0, column=1, sticky="ns") # Posiciona a barra vertical à direita do canvas
        self.midi_visualizer.config(yscrollcommand=vbar.set) # Liga o canvas à barra de rolagem vertical

        # Barra de rolagem horizontal
        hbar = ttk.Scrollbar(visualizer_container_frame, orient=tk.HORIZONTAL, command=self.midi_visualizer.xview)
        hbar.grid(row=1, column=0, sticky="ew") # Posiciona a barra horizontal abaixo do canvas
        self.midi_visualizer.config(xscrollcommand=hbar.set) # Liga o canvas à barra de rolagem horizontal

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

        base_midi_dir = os.path.join(os.getcwd(), "MIDIs_Gerados")
        session_dir = os.path.join(base_midi_dir, project_name)
        
        os.makedirs(session_dir, exist_ok=True) # Cria a pasta se não existir
        return session_dir

    def _apply_genre_config(self):
        # Aplica as configurações do gênero selecionado
        selected_genre = self.selected_genre_var.get()
        config = self.music_generator.genre_configs.get(selected_genre)

        if config:
            self.bpm_var.set(config.get('default_bpm', 120)) # Atualiza o BPM
            
            # NOVIDADE: Atualiza o tipo de escala com base na configuração do gênero
            default_scale = config.get('default_scale_type', 'Minor') # Padrão para 'Minor' se não especificado
            self.scale_type_var.set(default_scale)

            # Instrument programs (apenas para exibição ou feedback, não altera a geração)
            self.log_message(f"Configurações para '{selected_genre}' aplicadas:")
            self.log_message(f"  BPM padrão: {self.bpm_var.get()}")
            self.log_message(f"  Escala padrão: {self.scale_type_var.get()}") # Log da escala padrão
            
            inst_progs = config.get('instrument_programs', {})
            for part, program_num in inst_progs.items():
                self.log_message(f"  {part.capitalize()}: MIDI Program {program_num} ({self._get_instrument_name(program_num)})")
        else:
            self.log_message(f"AVISO: Configuração para gênero '{selected_genre}' não encontrada. Usando padrões.")

    def _on_genre_selected(self, event=None):
        # Chama a função de aplicação de configurações quando o gênero muda
        self._apply_genre_config()

    def _get_instrument_name(self, program_num):
        # Um mapeamento simples de alguns programas MIDI. Pode ser expandido.
        # Fonte: General MIDI Level 1 Sound Set
        instruments = {
            0: "Acoustic Grand Piano", 1: "Bright Acoustic Piano",
            25: "Acoustic Guitar (steel)", 33: "Electric Bass (finger)",
            39: "Synth Bass 2", 42: "Cello", 51: "Synth Voice", 62: "Synth Brass 1",
            80: "Synth Lead 1 (square)", 81: "Synth Lead 2 (sawtooth)",
            89: "Pad 2 (Warm)", 90: "Pad 3 (Polysynth)", 92: "Pad 5 (Bowed)", 93: "Pad 6 (Metallic)",
            36: "Fretless Bass", 37: "Slap Bass 1", 38: "Slap Bass 2", 40: "Violin",
            41: "Viola", 43: "Contrabass", 44: "Tremolo Strings", 45: "Pizzicato Strings",
            46: "Orchestral Harp", 47: "Timpani", 48: "String Ensemble 1", 49: "String Ensemble 2",
            50: "Synth Strings 1", 52: "Orchestra Hit", 53: "Trumpet", 54: "Trombone",
            55: "Tuba", 56: "French Horn", 57: "Brass Section", 58: "Synth Brass 2",
            59: "Soprano Sax", 60: "Alto Sax", 61: "Tenor Sax", 63: "Oboe",
            64: "English Horn", 65: "Bassoon", 66: "Clarinet", 67: "Piccolo",
            68: "Flute", 69: "Recorder", 70: "Pan Flute", 71: "Blown Bottle",
            72: "Shakuhachi", 73: "Whistle", 74: "Ocarina", 75: "Lead 3 (Calliope)",
            76: "Lead 4 (Chiff)", 77: "Lead 5 (Charang)",
            78: "Lead 6 (Voice)", 
            79: "Lead 7 (5th Sawtooth)", 82: "Lead 8 (Bass & Lead)", 83: "Pad 1 (New Age)",
            84: "Pad 4 (Choir)", 85: "Pad 7 (Halo)", 86: "Pad 8 (Sweep)", 87: "FX 1 (Rain)",
            88: "FX 2 (Soundtrack)", 91: "FX 3 (Crystal)", 94: "FX 4 (Atmosphere)",
            95: "FX 5 (Brightness)", 96: "FX 6 (Goblins)", 97: "FX 7 (Echoes)",
            98: "FX 8 (Sci-Fi)", 99: "Sitar", 100: "Banjo", 101: "Shamisen",
            102: "Koto", 103: "Kalimba", 104: "Bagpipe", 105: "Fiddle",
            106: "Shanai", 107: "Tinkle Bell", 108: "Agogo", 109: "Steel Drums",
            110: "Woodblock", 111: "Taiko Drum", 112: "Melodic Tom", 113: "Synth Drum",
            114: "Reverse Cymbal", 115: "Guitar Fret Noise", 116: "Breath Noise",
            117: "Seashore", 118: "Bird Tweet", 119: "Telephone Ring", 120: "Helicopter",
            121: "Applause", 122: "Gunshot"
        }
        return instruments.get(program_num, f"Instrumento MIDI {program_num}")

    def generate_music(self):
        self.stop_midi_playback() # Garante que nada esteja tocando antes de gerar
        self.log_text_area.config(state="normal")
        self.log_text_area.delete(1.0, tk.END) # Limpa o log anterior
        self.log_text_area.config(state="disabled")

        self.log_message("Iniciando geração de música...")

        root_key = self.root_key_var.get()
        scale_type = self.scale_type_var.get() # Agora este valor é atualizado pelo gênero
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
        selected_genre = self.selected_genre_var.get() # Será 'Drum and Bass' ou 'Liquid Funk'

        self.log_message(f"Gerando MIDI para {selected_genre} (BPM: {bpm}, Duração: {num_measures} compassos, Escala: {scale_type})...")
        

        # Validação de entradas
        if not root_key or not scale_type:
            messagebox.showerror("Erro de Entrada", "Por favor, selecione um Tom e Tipo de Escala.")
            self.log_message("Geração abortada: Tom ou Tipo de Escala não selecionados.")
            return

        if num_beats % 4 != 0:
            messagebox.showerror("Erro de Entrada", "O número de batidas deve ser um múltiplo de 4 para garantir compassos completos.")
            self.log_message("Geração abortada: Número de batidas inválido.")
            return

        try:
            # Chama o gerador de música com os parâmetros da GUI
            all_midi_events, log_details, total_ticks, us_per_beat = self.music_generator.generate_music_parts(
                root_key, scale_type, bpm, num_beats, # Passa num_beats para o gerador
                generate_bass, generate_chords, generate_lead, generate_pads, generate_arpeggio,
                generate_drums,
                selected_genre
            )
            self.log_message(log_details)

            # Armazena os dados gerados para reprodução e visualização
            self.generated_all_midi_events = all_midi_events
            self.generated_total_ticks = total_ticks
            self.generated_us_per_beat = us_per_beat
            self.generated_bpm = bpm
            
            # Obtém os programas de instrumento do gênero selecionado para salvar/reproduzir
            selected_genre_config = self.music_generator.genre_configs.get(selected_genre, {})
            self.generated_instrument_programs = selected_genre_config.get('instrument_programs', {
                'bass': 39, 'chords': 1, 'lead': 81, 'pads': 89, 'arpeggio': 81, 'drums': 0
            })

            # Salva o MIDI em um arquivo temporário para reprodução posterior pelo botão "Reproduzir MIDI"
            if self.temp_midi_file_for_playback and os.path.exists(self.temp_midi_file_for_playback):
                os.remove(self.temp_midi_file_for_playback) 

            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi_file:
                self.temp_midi_file_for_playback = tmp_midi_file.name

            # Salva o arquivo temporário usando os programas de instrumento corretos
            self.music_generator.save_midi_file(
                self.generated_all_midi_events, 
                self.temp_midi_file_for_playback, 
                self.generated_bpm, 
                self.generated_instrument_programs
            )
            self.midi_file_path = self.temp_midi_file_for_playback 

            self.log_message(f"Música gerada e salva temporariamente em '{self.midi_file_path}'. Agora você pode reproduzi-la ou salvá-la.")

            # Define o current_project_base_dir para o botão "Abrir Pasta"
            # O diretório real de salvamento é calculado no momento do save
            self.current_project_base_dir = self.get_current_project_session_dir()
            self.log_message(f"Pasta base do projeto definida: {self.current_project_base_dir}")

            # Atualização do Visualizador
            self.midi_visualizer.set_midi_data(all_midi_events, total_ticks, self.music_generator.ticks_per_beat)
            self.midi_visualizer.xview_moveto(0) 
            self.midi_visualizer.yview_moveto(0) 

            #messagebox.showinfo("Sucesso", "Música MIDI gerada e visualizada com sucesso! Agora você pode reproduzi-la ou salvá-la.")

        except Exception as e:
            self.log_message(f"Ocorreu um erro durante a geração: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    # Chamado pelo botão "Reproduzir MIDI"
    def play_midi(self):
        if not self.midi_file_path or not os.path.exists(self.midi_file_path):
            messagebox.showwarning("Reproduzir MIDI", "Nenhuma música foi gerada ainda. Clique em 'Gerar Música' primeiro.")
            self.log_message("Tentativa de reprodução falhou: nenhuma música gerada.")
            return
        
        self._start_midi_playback(self.midi_file_path, self.generated_bpm)

    def _start_midi_playback(self, filename, bpm):
        self.stop_midi_playback() # Para qualquer reprodução anterior
        
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            self.playing_midi = True
            self.start_playback_time = pygame.time.get_ticks() / 1000.0 # Tempo em segundos quando a reprodução começou
            self.music_bpm = bpm
            
            # Inicia a atualização da linha de progresso
            self.update_progress_line()
            
            self.log_message(f"Reproduzindo MIDI: '{filename}' (BPM: {bpm})...")
        except pygame.error as e:
            self.log_message(f"Erro ao reproduzir MIDI (Pygame): {e}. Verifique se o mixer está inicializado e o arquivo é válido.")
        except Exception as e:
            self.log_message(f"Erro inesperado durante a reprodução MIDI: {e}")

    def stop_midi_playback(self):
        if self.playing_midi:
            pygame.mixer.music.stop()
            self.playing_midi = False
            if self.update_progress_job:
                self.master.after_cancel(self.update_progress_job)
                self.update_progress_job = None
            self.midi_visualizer.update_progress_line(0) # Reseta a linha de progresso
            self.log_message("Reprodução MIDI parada.")

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

    def save_midi_full_to_default_location(self):
        """Salva o MIDI completo no diretório de sessão atual do projeto, com timestamp no nome do arquivo."""
        if not self.generated_all_midi_events or not self.generated_bpm or not self.generated_instrument_programs:
            messagebox.showwarning("Salvar MIDI Completo", "Nenhuma música foi gerada ainda para salvar.")
            return

        session_dir = self.get_current_project_session_dir() # Obtém o diretório ATUALIZADO
        if not session_dir: 
            messagebox.showerror("Erro de Salvamento", "Não foi possível determinar o diretório para salvar. Tente novamente.")
            return

        try:
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            full_midi_filename = os.path.join(session_dir, f"Full_Mix_{timestamp_file}.mid")
            self.music_generator.save_midi_file(self.generated_all_midi_events, full_midi_filename, self.generated_bpm, self.generated_instrument_programs)
            self.log_message(f"MIDI completo salvo em: {full_midi_filename}")
            messagebox.showinfo("Sucesso", f"MIDI completo salvo com sucesso em:\n{full_midi_filename}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo MIDI completo: {e}")
            self.log_message(f"ERRO ao salvar MIDI completo: {e}")

    def save_midi_parts_to_default_location(self):
        """Salva as partes MIDI separadamente no diretório de sessão atual do projeto, com timestamp nos nomes dos arquivos."""
        if not self.generated_all_midi_events or not self.generated_bpm or not self.generated_instrument_programs:
            messagebox.showwarning("Salvar Partes Separadas", "Nenhuma música foi gerada ainda para salvar.")
            return

        session_dir = self.get_current_project_session_dir() 
        if not session_dir: 
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
                    # Usa o programa de instrumento específico para esta parte
                    single_part_instrument_program = {part_name: self.generated_instrument_programs.get(part_name, 0)}

                    self.music_generator.save_midi_file(temp_midi_events, part_filename, self.generated_bpm, single_part_instrument_program)
                    self.log_message(f"Parte '{part_name}' salva em: {part_filename}")
            
            messagebox.showinfo("Sucesso", f"Partes MIDI salvas separadamente na pasta:\n{session_dir}")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar Partes", f"Ocorreu um erro ao salvar as partes MIDI: {e}")
            self.log_message(f"ERRO ao salvar partes MIDI: {e}")

    def open_generated_midi_folder(self):
        """Abre a pasta de sessão do projeto atual no explorador de arquivos do sistema."""
        session_dir = self.get_current_project_session_dir() 
        
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

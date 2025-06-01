# midi_visualizer.py

import tkinter as tk

class MidiVisualizer(tk.Canvas):
    def __init__(self, master, total_ticks, **kwargs):
        super().__init__(master, **kwargs)
        self.total_ticks = total_ticks
        self.note_height = 10 
        self.start_midi_note = 36 # C2
        self.end_midi_note = 84   # C6 (para cobrir a faixa usual)
        self.num_midi_notes_visible = self.end_midi_note - self.start_midi_note + 1
        
        self.all_midi_events = {} # Inicializa para evitar NameError
        self.ticks_per_beat = 480 # Valor padrão, será atualizado por set_midi_data

        self.progress_line_id = None # Armazenará o ID da linha de progresso
        
        self.bind("<Configure>", self._on_resize)
        self.current_scroll_x = 0 

    def _on_resize(self, event):
        self.redraw_notes()
        # Após redimensionar, se a linha de progresso existir, redesenha-a
        if self.progress_line_id:
            self.update_progress_line(self.get_current_progress_ticks())

    def get_current_progress_ticks(self):
        """Retorna a posição atual da linha de progresso em ticks (se existir)."""
        if self.progress_line_id:
            coords = self.coords(self.progress_line_id)
            if coords:
                # A linha é (x1, y1, x2, y2), então x1 é a posição
                pixels_per_tick = self.winfo_width() / self.total_ticks if self.total_ticks > 0 else 1
                return coords[0] / pixels_per_tick if pixels_per_tick > 0 else 0
        return 0

    def set_midi_data(self, all_midi_events, ticks_per_beat):
        self.all_midi_events = all_midi_events
        self.ticks_per_beat = ticks_per_beat
        self.redraw_notes()
        self.delete_progress_line() # Garante que a linha seja removida ao carregar novos dados

    def redraw_notes(self):
        self.delete("all") # Limpa o canvas
        # Não deleta a linha de progresso para não piscar, mas a excluímos antes de redesenhar tudo no app_gui

        if not hasattr(self, 'all_midi_events') or not self.all_midi_events or self.total_ticks == 0:
            return

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            return 

        pixels_per_tick = canvas_width / self.total_ticks if self.total_ticks > 0 else 1 # Evitar divisão por zero

        # Desenhar linhas de compasso (a cada 4 beats)
        for i in range(0, self.total_ticks + 1, self.ticks_per_beat * 4):
            x = i * pixels_per_tick
            if x > canvas_width: break 
            self.create_line(x, 0, x, canvas_height, fill="lightgray", dash=(2, 2))

        # Cores para cada tipo de parte
        colors = { 
            'bass': 'blue',
            'chords': 'green',
            'lead': 'red',
            'pads': 'purple',
            'arpeggio': 'orange' 
        }

        # Desenhar as notas
        for part_name, events in self.all_midi_events.items():
            if not events: continue 

            for event_type, note, velocity, time in events:
                if event_type == 'note_on':
                    note_off_time = None
                    for off_event_type, off_note, _, off_time in events:
                        if off_event_type == 'note_off' and off_note == note and off_time >= time:
                            note_off_time = off_time
                            break
                    
                    if note_off_time is not None:
                        x1 = time * pixels_per_tick
                        x2 = note_off_time * pixels_per_tick
                        
                        y_pos_relative = (note - self.start_midi_note) 
                        y1 = canvas_height - (y_pos_relative * (canvas_height / self.num_midi_notes_visible))
                        y2 = y1 - self.note_height 
                        
                        y1 = max(0, min(canvas_height, y1))
                        y2 = max(0, min(canvas_height, y2))
                        
                        self.create_rectangle(x1, y1, x2, y2, fill=colors.get(part_name, 'black'), outline="")
        
        # Redesenha a linha de progresso se ela existir
        if self.progress_line_id:
            self.update_progress_line(self.get_current_progress_ticks())

    def update_progress_line(self, current_ticks):
        """Cria ou atualiza a linha de progresso no canvas."""
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        if canvas_width == 0 or canvas_height == 0 or self.total_ticks == 0:
            return

        pixels_per_tick = canvas_width / self.total_ticks
        x_position = current_ticks * pixels_per_tick

        if self.progress_line_id:
            self.coords(self.progress_line_id, x_position, 0, x_position, canvas_height)
        else:
            self.progress_line_id = self.create_line(x_position, 0, x_position, canvas_height, fill="red", width=2, tags="progress_line")
        
        # Ajusta a visualização para manter a linha de progresso visível
        # Se a linha está muito para a direita, rola o canvas
        visible_left, visible_right = self.xview()
        current_x_scroll = visible_left * canvas_width # Posição em pixels do lado esquerdo da vista

        # Se a linha de progresso estiver fora da vista à direita
        if x_position > (current_x_scroll + canvas_width):
            # Calcula a nova posição de rolagem para centralizar a linha ou mantê-la visível
            new_scroll_x = x_position - (canvas_width / 2) # Tenta centralizar
            if new_scroll_x < 0: new_scroll_x = 0 # Não rola para antes do início

            # Converte pixels para a fração de rolagem esperada pelo xview
            scroll_fraction = new_scroll_x / (self.total_ticks * pixels_per_tick) if (self.total_ticks * pixels_per_tick) > 0 else 0
            self.xview_moveto(scroll_fraction)
        # Se a linha de progresso estiver fora da vista à esquerda (rola para trás)
        elif x_position < current_x_scroll:
            new_scroll_x = x_position - (canvas_width / 2)
            if new_scroll_x < 0: new_scroll_x = 0
            scroll_fraction = new_scroll_x / (self.total_ticks * pixels_per_tick) if (self.total_ticks * pixels_per_tick) > 0 else 0
            self.xview_moveto(scroll_fraction)

    def delete_progress_line(self):
        """Remove a linha de progresso do canvas."""
        if self.progress_line_id:
            self.delete(self.progress_line_id)
            self.progress_line_id = None
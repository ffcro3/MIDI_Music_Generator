# midi_visualizer.py

import tkinter as tk

class MidiVisualizer(tk.Canvas):
    def __init__(self, master, total_ticks, **kwargs):
        super().__init__(master, **kwargs)
        self.total_ticks = total_ticks
        self.note_height = 10 
        
        # Amplia a faixa de notas para visualização
        self.min_midi_note = 21 # A0 (nota MIDI mais baixa na maioria dos pianos)
        self.max_midi_note = 108 # C8 (nota MIDI mais alta na maioria dos pianos)
        
        self.num_total_midi_notes = self.max_midi_note - self.min_midi_note + 1
        
        self.all_midi_events = {} 
        self.ticks_per_beat = 480 

        self.progress_line_id = None 
        
        self.bind("<Configure>", self._on_resize)
        
        # Configurar barras de rolagem
        self.hbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.xview)
        self.vbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=self.yview)
        
        # Conectar as barras de rolagem ao canvas
        self.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        
    def _on_resize(self, event):
        # Quando o canvas é redimensionado, ajustamos o scrollregion
        
        # Recalcula o scrollregion com a nova largura e altura do canvas
        self.configure(scrollregion=(0, 0, self.get_content_width_in_pixels(), self.get_content_height_in_pixels()))

        self.redraw_notes()
        # Não é necessário chamar update_progress_line aqui.
        # redraw_notes já redesenha a linha de progresso se ela existir.


    def get_content_width_in_pixels(self):
        """Calcula a largura total do conteúdo em pixels para o scrollregion horizontal."""
        
        pixels_per_beat = 30 # Ajuste este valor para controlar a "densidade" horizontal
        
        # O total_ticks precisa ser convertido para beats (semínimas)
        total_beats = self.total_ticks / self.ticks_per_beat if self.ticks_per_beat > 0 else 0
        
        calculated_width = total_beats * pixels_per_beat
        
        # Garante que a largura do conteúdo seja pelo menos a largura da janela para que a barra de rolagem apareça se necessário
        return max(self.winfo_width(), calculated_width)


    def get_content_height_in_pixels(self):
        """Calcula a altura total do conteúdo em pixels para o scrollregion vertical."""
        
        calculated_height = self.num_total_midi_notes * self.note_height + 20 # +20 para um pequeno padding
        
        # Garante que a altura do conteúdo seja pelo menos a altura da janela
        return max(self.winfo_height(), calculated_height)


    def set_midi_data(self, all_midi_events, ticks_per_beat):
        self.all_midi_events = all_midi_events
        self.ticks_per_beat = ticks_per_beat
        
        # Encontra o total de ticks mais alto de todos os eventos para definir a largura total do scrollregion
        max_tick = 0
        for part_name, events in self.all_midi_events.items():
            for event_type, note, velocity, time in events:
                if event_type == 'note_on':
                    # Procura a nota off correspondente para pegar a duração
                    note_off_time = None
                    for off_event_type, off_note, _, off_time in events:
                        if off_event_type == 'note_off' and off_note == note and off_time >= time:
                            note_off_time = off_time
                            break
                    if note_off_time is not None:
                        max_tick = max(max_tick, note_off_time)
                    else: # Se não encontrar note_off, assume uma duração curta
                        max_tick = max(max_tick, time + self.ticks_per_beat) # Assume 1 beat de duração
                
        self.total_ticks = max_tick if max_tick > 0 else 1 # Garante que total_ticks seja pelo menos 1

        # Atualiza o scrollregion com a nova largura e altura
        self.config(scrollregion=(0, 0, self.get_content_width_in_pixels(), self.get_content_height_in_pixels()))
        
        self.redraw_notes()
        self.delete_progress_line()

    def redraw_notes(self):
        self.delete("all") 

        canvas_width = self.winfo_width() # Largura visível do canvas
        canvas_height = self.winfo_height() # Altura visível do canvas

        if canvas_width == 0 or canvas_height == 0:
            return 

        # Calcula a escala de pixels por tick para a largura total do *scrollregion*
        content_width_pixels = self.get_content_width_in_pixels()
        pixels_per_tick = content_width_pixels / self.total_ticks if self.total_ticks > 0 else 1

        # Mapeamento vertical: notas MIDI para posição Y
        content_height_pixels = self.get_content_height_in_pixels()
        pixels_per_midi_note = content_height_pixels / self.num_total_midi_notes

        # Desenhar linhas de compasso (a cada 4 beats)
        for i in range(0, self.total_ticks + 1, self.ticks_per_beat * 4):
            x = i * pixels_per_tick
            # Desenha a linha vertical que atravessa toda a altura do scrollregion
            self.create_line(x, 0, x, content_height_pixels, fill="lightgray", dash=(2, 2))

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
                        
                        # Mapeamento vertical para Y: notas MIDI para posição Y
                        # Notas mais altas terão um Y menor (mais para cima no canvas)
                        # Queremos que a nota mais baixa (min_midi_note) apareça no fundo do canvas
                        # e a nota mais alta (max_midi_note) apareça no topo.
                        
                        y_bottom = content_height_pixels - ((note - self.min_midi_note) * pixels_per_midi_note)
                        y_top = y_bottom - self.note_height
                        
                        self.create_rectangle(x1, y_bottom, x2, y_top, fill=colors.get(part_name, 'black'), outline="")
        
        # Redesenha a linha de progresso se ela existir.
        # A posição é mantida pelo update_progress_line principal.
        if self.progress_line_id:
            # Reutiliza a última posição conhecida ou 0 se não houver
            last_progress_x = self.coords(self.progress_line_id)[0] if self.coords(self.progress_line_id) else 0
            
            # Converte pixels para ticks para chamar update_progress_line
            # Isso é um pouco redundante, mas garante que a linha seja redesenhada no lugar certo
            # após um redimensionamento, assumindo que já estava em alguma posição.
            current_ticks_on_redraw = last_progress_x / pixels_per_tick if pixels_per_tick > 0 else 0
            self.update_progress_line(current_ticks_on_redraw)


    def update_progress_line(self, current_ticks):
        """Cria ou atualiza a linha de progresso no canvas."""
        canvas_width = self.winfo_width() # Largura visível do canvas
        canvas_height = self.winfo_height() # Altura visível do canvas

        if canvas_width == 0 or canvas_height == 0 or self.total_ticks == 0:
            return

        # pixels_per_tick é calculado com base na largura total do conteúdo
        content_width_pixels = self.get_content_width_in_pixels()
        pixels_per_tick = content_width_pixels / self.total_ticks if self.total_ticks > 0 else 1
        
        x_position_on_content = current_ticks * pixels_per_tick

        if self.progress_line_id:
            # Move a linha existente. Note que ela se estende por toda a altura do scrollregion.
            self.coords(self.progress_line_id, x_position_on_content, 0, x_position_on_content, self.get_content_height_in_pixels())
        else:
            self.progress_line_id = self.create_line(x_position_on_content, 0, x_position_on_content, self.get_content_height_in_pixels(), fill="red", width=2, tags="progress_line")
            # Envia a linha para o topo para que fique visível sobre as notas
            self.tag_raise(self.progress_line_id) 
        
        # Ajusta a visualização para manter a linha de progresso visível
        # `xview_moveto` trabalha com frações do scrollregion total
        visible_left_fraction, visible_right_fraction = self.xview()
        
        # Converte a posição da linha em pixels para a fração do scrollregion
        line_fraction = x_position_on_content / content_width_pixels if content_width_pixels > 0 else 0

        # Se a linha de progresso estiver fora da vista à direita
        if line_fraction > visible_right_fraction:
            # Rola para que a linha fique no meio da vista
            new_scroll_fraction = line_fraction - (0.5 * (visible_right_fraction - visible_left_fraction))
            self.xview_moveto(new_scroll_fraction)
        # Se a linha de progresso estiver fora da vista à esquerda
        elif line_fraction < visible_left_fraction:
            new_scroll_fraction = line_fraction - (0.5 * (visible_right_fraction - visible_left_fraction))
            if new_scroll_fraction < 0: new_scroll_fraction = 0
            self.xview_moveto(new_scroll_fraction)

    def delete_progress_line(self):
        """Remove a linha de progresso do canvas."""
        if self.progress_line_id:
            self.delete(self.progress_line_id)
            self.progress_line_id = None
# midi_visualizer.py

import tkinter as tk

class MidiVisualizer(tk.Canvas):
    def __init__(self, master, total_ticks, **kwargs):
        super().__init__(master, **kwargs)
        self.total_ticks = total_ticks
        self.note_height = 10 
        
        # Ajustado: Faixa de notas MIDI para exibição (mais ampla)
        self.min_display_note = 21 # A0 (nota MIDI mais baixa)
        self.max_display_note = 108 # C8 (nota MIDI mais alta)
        self.num_midi_notes_visible = self.max_display_note - self.min_display_note + 1
        
        self.all_midi_events = {} # Inicializa para evitar NameError
        self.ticks_per_beat = 480 # Valor padrão, será atualizado por set_midi_data

        self.progress_line_id = None # Armazenará o ID da linha de progresso
        
        self.bind("<Configure>", self._on_resize)
        self.current_scroll_x = 0 

        # Calcula a altura do canvas para as notas usando a faixa de exibição
        self.canvas_height = self.num_midi_notes_visible * self.note_height

        # Define um valor inicial para pixels_per_tick para evitar divisão por zero
        # Será ajustado no _on_resize e set_midi_data para melhor visualização
        self.pixels_per_tick = 0.5 

        # Vincula eventos da roda do mouse para rolagem condicional (vertical por padrão, horizontal com Shift)
        self.bind("<MouseWheel>", self._on_mouse_scroll) # Windows/macOS
        self.bind("<Button-4>", self._on_mouse_scroll) # Linux (roda para cima)
        self.bind("<Button-5>", self._on_mouse_scroll) # Linux (roda para baixo)


    def _on_resize(self, event):
        # Atualiza a largura do canvas visível
        self.visible_canvas_width = self.winfo_width()
        
        # Recalcula pixels_per_tick para tentar encaixar a música na largura visível,
        # mas permitindo rolagem se for muito longa.
        if self.total_ticks > 0:
            # Tenta fazer com que 4 compassos (16 batidas) sejam visíveis inicialmente
            # Se a música for menor, ajusta para a música inteira.
            desired_visible_ticks = 16 * self.ticks_per_beat # 4 compassos
            
            # Calcula pixels_per_tick para a largura visível atual
            calculated_pp_tick = self.visible_canvas_width / desired_visible_ticks
            
            # Se a música inteira for menor que a largura visível, ajusta pp_tick para caber tudo
            if self.total_ticks * calculated_pp_tick < self.visible_canvas_width:
                 self.pixels_per_tick = self.visible_canvas_width / (self.total_ticks * 1.05) # Pequena margem
            else:
                 self.pixels_per_tick = calculated_pp_tick
        else:
            self.pixels_per_tick = 0.5 # Fallback se não houver ticks

        self.redraw_notes()
        
        # Após redimensionar, se a linha de progresso existir, redesenha-a
        if self.progress_line_id:
            self.update_progress_line(self.get_current_progress_ticks())

    def get_current_progress_ticks(self):
        """Retorna a posição atual da linha de progresso em ticks (se existir)."""
        if self.progress_line_id:
            # A posição da linha é o primeiro ponto X da linha
            x_coord = self.coords(self.progress_line_id)[0]
            return int(x_coord / self.pixels_per_tick)
        return 0

    def set_midi_data(self, all_midi_events, total_ticks, ticks_per_beat):
        """
        Define os dados MIDI para o visualizador.
        :param all_midi_events: Dicionário de eventos MIDI por parte.
        :param total_ticks: O número total de ticks da música.
        :param ticks_per_beat: A resolução de ticks por batida.
        """
        self.all_midi_events = all_midi_events
        self.total_ticks = total_ticks 
        self.ticks_per_beat = ticks_per_beat
        
        # Força o recálculo de pixels_per_tick e redraw ao definir novos dados
        self._on_resize(None) # Simula um evento de redimensionamento para recalcular pp_tick e redraw
        
        # Atualiza a região de rolagem do canvas com base no novo total_ticks e pixels_per_tick
        scroll_width = self.total_ticks * self.pixels_per_tick * 1.05 # Pequena margem para rolagem
        self.config(scrollregion=(0, 0, scroll_width, self.canvas_height))
        self.xview_moveto(0) # Volta ao início após carregar novos dados

    def redraw_notes(self):
        self.delete("notes") # Limpa todas as notas existentes
        
        # Calcula a largura total do conteúdo do MIDI
        content_width = self.total_ticks * self.pixels_per_tick
        
        # Ajusta a largura do canvas para ser pelo menos a largura visível ou o conteúdo
        self.config(width=max(self.winfo_width(), content_width))
        
        # Desenha as notas
        for part_name, events in self.all_midi_events.items():
            for event_type, note, velocity, time in events:
                if event_type == 'note_on':
                    # Encontra o evento 'note_off' correspondente
                    note_off_time = None
                    for off_event_type, off_note, off_velocity, off_time in events:
                        if off_event_type == 'note_off' and off_note == note and off_time >= time:
                            note_off_time = off_time
                            break
                    
                    if note_off_time is not None:
                        x1 = time * self.pixels_per_tick
                        x2 = note_off_time * self.pixels_per_tick
                        
                        # Mapeia a nota MIDI para a posição Y no visualizador
                        # Inverte a ordem para que notas mais altas fiquem no topo
                        # Usa min_display_note para mapear corretamente dentro da faixa visível
                        y1 = self.canvas_height - ((note - self.min_display_note) * self.note_height)
                        y2 = y1 - self.note_height # Altura da nota

                        # Cor da nota (pode ser personalizada por parte ou velocidade)
                        color = "blue"
                        if part_name == 'bass': color = "darkred"
                        elif part_name == 'chords': color = "green"
                        elif part_name == 'lead': color = "purple"
                        elif part_name == 'pads': color = "orange"
                        elif part_name == 'arpeggio': color = "teal"
                        elif part_name == 'drums': color = "gray" # Bateria pode ter cores diferentes para cada instrumento

                        self.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", tags="notes")

        # Redesenha a linha de progresso para garantir que esteja visível
        if self.progress_line_id:
            self.update_progress_line(self.get_current_progress_ticks())


    def update_progress_line(self, current_ticks):
        """
        Atualiza a posição da linha de progresso no visualizador e rola o canvas.
        :param current_ticks: A posição atual em ticks MIDI.
        """
        x_position = current_ticks * self.pixels_per_tick
        
        if self.progress_line_id:
            self.delete(self.progress_line_id)
        
        # Desenha a linha de progresso
        self.progress_line_id = self.create_line(x_position, 0, x_position, self.canvas_height, fill="red", width=2, tags="progress_line")
        
        # Rola o canvas para manter a linha de progresso visível
        canvas_width = self.winfo_width()
        
        # Adiciona verificação de tipo para garantir que xview() retorne uma tupla.
        xview_result = self.xview() 
        if not isinstance(xview_result, tuple) or len(xview_result) < 2:
            # Fallback seguro caso xview() retorne algo inesperado
            print(f"WARNING: self.xview() returned unexpected type/length: {type(xview_result)} - {xview_result}. Defaulting to (0.0, 1.0).")
            visible_left_fraction = 0.0
            visible_right_fraction = 1.0 
        else:
            visible_left_fraction = xview_result[0]
            visible_right_fraction = xview_result[1]
        
        # Converte as frações de rolagem para pixels
        # Garante que total_scrollable_width não seja zero para evitar ZeroDivisionError
        total_scrollable_width = self.total_ticks * self.pixels_per_tick * 1.5 
        if total_scrollable_width == 0: 
            total_scrollable_width = 1 # Evita divisão por zero, embora o scroll não funcione bem neste caso

        current_x_scroll_pixel_start = visible_left_fraction * total_scrollable_width
        current_x_scroll_pixel_end = visible_right_fraction * total_scrollable_width 

        # Se a linha de progresso estiver fora da vista à direita
        if x_position > current_x_scroll_pixel_end - (canvas_width * 0.2): # Rola um pouco antes do final
            new_scroll_x = x_position - (canvas_width * 0.5) # Tenta centralizar
            if new_scroll_x < 0: new_scroll_x = 0 # Não rola para antes do início
            
            scroll_fraction = new_scroll_x / total_scrollable_width
            self.xview_moveto(scroll_fraction)
        # Se a linha de progresso estiver fora da vista à esquerda (rola para trás)
        elif x_position < current_x_scroll_pixel_start + (canvas_width * 0.2): # Rola um pouco depois do início
            new_scroll_x = x_position - (canvas_width * 0.5)
            if new_scroll_x < 0: new_scroll_x = 0
            scroll_fraction = new_scroll_x / total_scrollable_width
            self.xview_moveto(scroll_fraction)

    # Função para lidar com o scroll do mouse
    def _on_mouse_scroll(self, event):
        # Determina a direção do scroll
        scroll_direction = 0
        if event.delta: # Windows/macOS
            scroll_direction = -int(event.delta / 120) # -1 para scroll para baixo, 1 para scroll para cima
        elif event.num == 4: # Linux (roda para cima)
            scroll_direction = 1
        elif event.num == 5: # Linux (roda para baixo)
            scroll_direction = -1
        else:
            return # Não é um evento de scroll de roda

        # Verifica se a tecla Shift está pressionada (estado 0x1)
        if event.state & 0x1: # Shift key is pressed
            # Rolagem horizontal
            scroll_amount_units = 5 # Rolagem mais suave em "unidades" (pode ser ajustado)
            self.xview_scroll(scroll_direction * scroll_amount_units, "units")
        else:
            # Rolagem vertical (padrão)
            scroll_amount_units = 5 # Ajuste a sensibilidade da rolagem vertical
            self.yview_scroll(scroll_direction * scroll_amount_units, "units")

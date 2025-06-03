# music_generator.py

import random
import mido
import json
import os

class MusicGenerator:
    def __init__(self):
        self.scales = {
            'Major': {
                'intervals': [0, 2, 4, 5, 7, 9, 11],
                'chords': {
                    'I': [0, 4, 7],
                    'ii': [2, 5, 9],
                    'iii': [4, 7, 11],
                    'IV': [5, 9, 12],
                    'V': [7, 11, 14],
                    'vi': [9, 12, 16],
                    'vii°': [11, 14, 17]
                }
            },
            'Minor': { # Natural Minor
                'intervals': [0, 2, 3, 5, 7, 8, 10],
                'chords': {
                    'i': [0, 3, 7],
                    'ii°': [2, 5, 8],
                    'III': [3, 7, 10],
                    'iv': [5, 8, 12],
                    'V': [7, 10, 14], # Pode ser V maior/dominante para cadência (harmônica)
                    'v': [7, 10, 14], # V menor (natural)
                    'VI': [8, 12, 15],
                    'VII': [10, 14, 17],
                    'bVII': [10, 13, 17], # Adicionado bVII para maior flexibilidade em estilos eletrônicos
                    'vii°': [10, 13, 16] 
                }
            }
        }
        
        self.ticks_per_beat = 480 # Resolução MIDI padrão (PPQ)

        self.genre_configs = self._load_genre_configs()

    def _load_genre_configs(self):
        config_path = os.path.join(os.path.dirname(__file__), 'genres_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo de configuração de gêneros '{config_path}' não foi encontrado.")
            print("Carregando configurações de gênero de fallback...")
            # Retorna uma configuração de fallback para DNB para que o programa continue funcionando
            return {
                "Drum and Bass": {
                    "default_bpm": 174,
                    "default_scale_type": "Minor",
                    "chords_progressions": [
                        ["i", "VI", "VII", "III"]
                    ],
                    "bass_pattern_density": 0.8,
                    "drum_patterns": {
                        "kick": [[[0, 100, 1], [960, 100, 1]]],
                        "snare": [[[480, 90, 1], [1440, 90, 1]]],
                        "hihat_closed": [
                            [[240, 70, 0.5], [720, 70, 0.5],
                            [1200, 70, 0.5], [1680, 70, 0.5]]
                        ],
                        "hihat_open": [[]],
                        "percussion": [[]]
                    },
                    "instrument_programs": {
                        "bass": 39, "chords": 1, "lead": 81, "pads": 89, "arpeggio": 81
                    }
                }
            }
        except json.JSONDecodeError as e:
            print(f"Erro ao ler o arquivo JSON de configuração de gêneros: {e}")
            print("O arquivo JSON pode estar mal formatado. Carregando configurações de gênero de fallback...")
            return {
                "Drum and Bass": {
                    "default_bpm": 174,
                    "default_scale_type": "Minor",
                    "chords_progressions": [
                        ["i", "VI", "VII", "III"]
                    ],
                    "bass_pattern_density": 0.8,
                    "drum_patterns": {
                        "kick": [[[0, 100, 1], [960, 100, 1]]],
                        "snare": [[[480, 90, 1], [1440, 90, 1]]],
                        "hihat_closed": [
                            [[240, 70, 0.5], [720, 70, 0.5],
                            [1200, 70, 0.5], [1680, 70, 0.5]]
                        ],
                        "hihat_open": [[]],
                        "percussion": [[]]
                    },
                    "instrument_programs": {
                        "bass": 39, "chords": 1, "lead": 81, "pads": 89, "arpeggio": 81
                    }
                }
            }

    def _get_note_from_root_and_interval(self, root_key, scale_type, interval, base_octave_midi_note):
        midi_notes_map = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        root_midi_value = midi_notes_map[root_key]
        
        octave_offset = (base_octave_midi_note // 12) * 12

        return octave_offset + root_midi_value + interval

    def generate_music_parts(self, root_key, scale_type, bpm, num_beats,
                             generate_bass, generate_chords, generate_lead,
                             generate_pads, generate_arpeggio, generate_drums,
                             selected_style):
        log_details = ""
        all_midi_events = {}

        config = self.genre_configs.get(selected_style, self.genre_configs.get('Drum and Bass', {}))
        
        # Obtém a progressão de acordes do JSON
        chord_progression_roman = random.choice(config.get('chords_progressions', [['i', 'VI', 'VII', 'III']]))
        
        instrument_programs = config.get('instrument_programs', {
            'bass': 39, 'chords': 1, 'lead': 81, 'pads': 89, 'arpeggio': 81, 'drums': 0
        })
        drum_patterns_config = config.get('drum_patterns', {})

        part_channels = {
            'bass': 0, 'chords': 1, 'lead': 2,
            'pads': 3, 'arpeggio': 4, 'drums': 9
        }

        # Bass
        if generate_bass:
            # Passa a progressão de acordes para a função de geração de baixo
            all_midi_events['bass'] = self.generate_bass_line(root_key, scale_type, num_beats, chord_progression_roman)
            log_details += "Bass gerado.\n"

        # Drums
        if generate_drums:
            # A função generate_drums agora é mais genérica e usa os padrões do JSON
            all_midi_events['drums'] = self.generate_drums(num_beats, drum_patterns_config)
            log_details += "Bateria gerada.\n"

        # Chords
        if generate_chords:
            # Passa a progressão de acordes e o estilo para a função de geração de acordes
            all_midi_events['chords'] = self.generate_chords(root_key, scale_type, num_beats, chord_progression_roman, selected_style)
            log_details += "Acordes gerados.\n"


        if generate_lead:
            # Passa a progressão de acordes para a função de geração de melodia
            all_midi_events['lead'] = self.generate_lead_melody(root_key, scale_type, num_beats, chord_progression_roman, selected_style)
            log_details += "Melodia gerada.\n"

        if generate_pads:
            # Passa a progressão de acordes para a função de geração de pads
            all_midi_events['pads'] = self.generate_pads(root_key, scale_type, num_beats, chord_progression_roman, selected_style)
            log_details += "Pads gerados.\n"

        if generate_arpeggio:
            # Passa a progressão de acordes para a função de geração de arpejo
            all_midi_events['arpeggio'] = self.generate_arpeggio(root_key, scale_type, num_beats, chord_progression_roman)
            log_details += "Arpejo gerado.\n"

        total_ticks = num_beats * self.ticks_per_beat
        us_per_beat = mido.bpm2tempo(bpm)

        return all_midi_events, log_details, total_ticks, us_per_beat

    def generate_bass_line(self, root_key, scale_type, num_beats, chord_progression_roman):
        events = []
        root_midi = self._get_note_from_root_and_interval(root_key, 'Major', 0, 0) # Obtém o valor MIDI da tônica
        # Oitava mais baixa para o baixo, garantindo que a nota esteja em uma faixa MIDI válida
        scale_notes = [self._get_note_from_root_and_interval(root_key, scale_type, interval, 36) for interval in self.scales[scale_type]['intervals']]
        
        quantization_unit = self.ticks_per_beat // 4 # Semicolcheia (120 ticks)
        
        base_velocity = 85
        velocity_range = 15 # Variação de +/- 15 da base

        for beat_num in range(num_beats):
            beat_start_tick = beat_num * self.ticks_per_beat
            
            # Obtém o nome do acorde para o compasso atual
            measure_idx = beat_num // 4
            chord_name = chord_progression_roman[measure_idx % len(chord_progression_roman)]
            
            # Obtém a nota raiz do acorde na escala correta
            chord_root_interval = self.scales[scale_type]['chords'][chord_name][0]
            base_note = self._get_note_from_root_and_interval(root_key, scale_type, chord_root_interval, 36) # Oitava do baixo

            # Decide o ritmo da nota principal (semínima, colcheia, pontuada)
            rhythmic_options = [
                (self.ticks_per_beat, 1), # Semínima
                (self.ticks_per_beat // 2, 2), # Colcheia
                (int(self.ticks_per_beat * 1.5), 0.75), # Semínima pontuada
                (self.ticks_per_beat * 2, 0.5) # Mínima
            ]
            duration_ticks, _ = random.choice(rhythmic_options)
            
            # Garante que a duração seja um múltiplo da unidade de quantização
            duration_ticks = (duration_ticks // quantization_unit) * quantization_unit
            if duration_ticks == 0: duration_ticks = quantization_unit # Evita duração zero

            # Velocity com variação para humanizar
            velocity = random.randint(base_velocity - velocity_range, base_velocity + velocity_range)
            
            # Adiciona a nota principal
            events.append(('note_on', base_note, velocity, beat_start_tick))
            # Pequeno release para evitar sobreposição
            events.append(('note_off', base_note, 0, beat_start_tick + duration_ticks - (quantization_unit // 2)))

            # Chance de adicionar notas extras em subdivisões (colcheias/semicolcheias) para groove
            current_sub_tick = beat_start_tick + duration_ticks # Começa após a nota principal
            
            while current_sub_tick < beat_start_tick + self.ticks_per_beat: # Dentro da mesma batida
                if random.random() < 0.6: # 60% de chance de adicionar uma nota extra
                    sub_note_duration = random.choice([quantization_unit, quantization_unit * 2]) # Semicolcheia ou Colcheia
                    sub_note = random.choice(scale_notes + [base_note + 7, base_note + 12]) # Varia a nota
                    sub_velocity = random.randint(base_velocity - velocity_range - 20, base_velocity - velocity_range) # Mais suave

                    events.append(('note_on', sub_note, sub_velocity, current_sub_tick))
                    events.append(('note_off', sub_note, 0, current_sub_tick + sub_note_duration - (quantization_unit // 2)))
                    current_sub_tick += sub_note_duration
                else:
                    # Se não gerou nota, avança um pouco para dar espaço
                    current_sub_tick += quantization_unit
                
                # Garante que não ultrapasse o final da batida
                if current_sub_tick >= beat_start_tick + self.ticks_per_beat:
                    break
            
        return events

    def generate_chords(self, root_key, scale_type, num_beats, chord_progression_roman, selected_style):
        events = []
        
        # Obtém a configuração do gênero
        config = self.genre_configs.get(selected_style, {})
        chord_rhythmic_patterns = config.get('chord_rhythmic_patterns', [])

        progression_length = len(chord_progression_roman)
        
        # Parâmetros de dinamismo adicionais
        note_skip_probability = 0.1 # 10% de chance de pular uma nota dentro de um acorde
        chord_event_skip_probability = 0.05 # 5% de chance de pular um evento de acorde dentro do padrão rítmico
        velocity_random_range = 10 # Variação de +/- 10 na velocity final
        timing_random_range = 15 # Variação de +/- 15 ticks no timing (para humanização)
        duration_random_range = 20 # Variação de +/- 20 ticks na duração

        for measure_num in range(num_beats // 4): # Para cada compasso
            chord_name = chord_progression_roman[measure_num % progression_length]
            chord_intervals = self.scales[scale_type]['chords'][chord_name]
            
            base_note_for_chord = self._get_note_from_root_and_interval(root_key, scale_type, 0, 60) # Oitava dos acordes
            
            start_tick_measure = measure_num * self.ticks_per_beat * 4
            
            if selected_style == 'House' and chord_rhythmic_patterns:
                # Se for House e existirem padrões rítmicos, escolhe um aleatoriamente
                chosen_pattern = random.choice(chord_rhythmic_patterns)
                
                for note_event_data in chosen_pattern:
                    # Chance de pular o evento de acorde inteiro no padrão rítmico
                    if random.random() < chord_event_skip_probability:
                        continue

                    offset = note_event_data['offset']
                    duration = note_event_data['duration']
                    velocity_mult = note_event_data['velocity_mult']
                    
                    # Adiciona variação de timing
                    random_timing_offset = random.randint(-timing_random_range, timing_random_range)
                    final_offset = start_tick_measure + offset + random_timing_offset
                    # Garante que o offset não seja negativo
                    if final_offset < start_tick_measure:
                        final_offset = start_tick_measure

                    # Adiciona variação de duração
                    random_duration_offset = random.randint(-duration_random_range, duration_random_range)
                    final_duration = duration + random_duration_offset
                    # Garante que a duração mínima seja razoável (ex: 30 ticks)
                    if final_duration < 30:
                        final_duration = 30
                    
                    for note_offset in chord_intervals:
                        # Chance de pular uma nota individual dentro do acorde
                        if random.random() < note_skip_probability:
                            continue

                        note = base_note_for_chord + note_offset
                        
                        # Aplica multiplicador de velocity e adiciona variação aleatória
                        base_vel = int(random.randint(70, 90) * velocity_mult)
                        final_velocity = max(20, min(127, base_vel + random.randint(-velocity_random_range, velocity_random_range))) # Garante velocity entre 20-127
                        
                        events.append(('note_on', note, final_velocity, final_offset))
                        # Pequeno release para o efeito de "corte"
                        events.append(('note_off', note, 0, final_offset + final_duration - 10)) 
            else:
                # Comportamento padrão para outros gêneros ou se não houver padrão rítmico
                duration_ticks = self.ticks_per_beat * 4 - 10 # Padrão de 1 compasso sustentado
                if selected_style == 'Trance' or selected_style == 'Psytrance':
                    duration_ticks = self.ticks_per_beat * 8 - 10 # Pads mais longos para Trance/Psytrance

                for note_offset in chord_intervals:
                    note = base_note_for_chord + note_offset
                    velocity = random.randint(70, 90) # Variação de velocity
                    events.append(('note_on', note, velocity, start_tick_measure))
                    events.append(('note_off', note, 0, start_tick_measure + duration_ticks)) 

        return events

    def generate_lead_melody(self, root_key, scale_type, num_beats, chord_progression_roman, selected_style):
        events = []
        root_midi = self._get_note_from_root_and_interval(root_key, 'Major', 0, 0) # Obtém o valor MIDI da tônica
        # Oitava mais alta para melodia
        scale_notes = [self._get_note_from_root_and_interval(root_key, scale_type, interval, 72) for interval in self.scales[scale_type]['intervals']]
        
        # Definir uma resolução de quantização para a melodia (ex: semicolcheia)
        quantization_unit = self.ticks_per_beat // 4 # Semicolcheia (120 ticks)

        # Reintroduzir mais variedade na melodia
        for beat_num in range(num_beats): # Loop para cada batida (quarter note)
            beat_start_tick = beat_num * self.ticks_per_beat
            
            # Decide quantas notas na melodia para esta batida (mais variação)
            num_notes_in_beat = random.randint(0, 4) # Pode ter de 0 a 4 notas por batida
            
            if num_notes_in_beat == 0 and random.random() < 0.3: # Pequena chance de silêncio total na batida
                continue

            for i in range(num_notes_in_beat):
                # Garante que a nota comece em um ponto quantizado dentro da batida
                note_start_tick = beat_start_tick + (i * quantization_unit) 
                
                # Escolhe uma nota da escala ou um salto melódico pequeno
                if random.random() < 0.7: # Maior chance de seguir a escala
                    melody_note = random.choice(scale_notes)
                else: # Pequena chance de um salto para criar interesse
                    melody_note = random.choice(scale_notes + [scale_notes[0] + 12, scale_notes[0] - 12])

                # Evita notas muito fora da faixa comum
                if melody_note < 60: melody_note = 60 # C4
                if melody_note > 96: melody_note = 96 # C7 (para ter mais espaço)

                velocity = random.randint(75, 100) # Variação de velocity
                
                # Duração da nota: colcheia, semicolheia, ou semínima (quantizada)
                duration_multipliers = [1, 2, 4] # Semicolcheia, Colcheia, Semínima
                duration_ticks = random.choice(duration_multipliers) * quantization_unit
                
                # Garante que a nota não ultrapasse o final da batida
                if note_start_tick + duration_ticks > beat_start_tick + self.ticks_per_beat:
                    duration_ticks = (beat_start_tick + self.ticks_per_beat) - note_start_tick
                    duration_ticks = (duration_ticks // quantization_unit) * quantization_unit
                    if duration_ticks <= 0: continue # Evita notas com duração zero ou negativa

                events.append(('note_on', melody_note, velocity, note_start_tick))
                # Ajusta a duração para não sobrepor a próxima nota perfeitamente, dando um pequeno "release"
                events.append(('note_off', melody_note, 0, note_start_tick + duration_ticks - (quantization_unit // 2))) 
                
        return events


    def generate_pads(self, root_key, scale_type, num_beats, chord_progression_roman, selected_style):
        events = []
        root_midi = self._get_note_from_root_and_interval(root_key, 'Major', 0, 0) # Obtém o valor MIDI da tônica
        
        current_tick = 0
        pad_duration = self.ticks_per_beat * 8 # Pad dura 2 compassos (8 batidas)
        
        # Usar a progressão de acordes do JSON
        progression_length = len(chord_progression_roman)

        for block_num in range(num_beats // 8): # Para cada bloco de 2 compassos
            # Seleciona o acorde da progressão (looping)
            # Usamos `block_num * 2` porque cada bloco tem 2 compassos e a progressão é por compasso.
            chord_name = chord_progression_roman[(block_num * 2) % progression_length] 
            chord_intervals = self.scales[scale_type]['chords'][chord_name]

            # Ajusta as notas do acorde para a oitava correta (geralmente uma oitava acima da melodia principal, ou mais cheia)
            base_note_for_pad = self._get_note_from_root_and_interval(root_key, scale_type, 0, 48) # Oitava dos pads
            
            start_tick = block_num * self.ticks_per_beat * 8
            
            duration_ticks = self.ticks_per_beat * 4 - 10 # Padrão de 1 compasso
            if selected_style == 'Trance' or selected_style == 'Psytrance':
                duration_ticks = self.ticks_per_beat * 8 - 10 # Pads mais longos para Trance/Psytrance

            for note_offset in chord_intervals:
                note = base_note_for_pad + note_offset
                velocity = random.randint(50, 70) # Pads são mais suaves
                events.append(('note_on', note, velocity, start_tick))
                events.append(('note_off', note, 0, start_tick + duration_ticks)) # Pequeno release
            
        return events

    def generate_arpeggio(self, root_key, scale_type, num_beats, chord_progression_roman):
        events = []
        root_midi = self._get_note_from_root_and_interval(root_key, 'Major', 0, 0) # Obtém o valor MIDI da tônica
        
        # Define a menor duração para as notas do arpejo (Fusa - 32nd note)
        # Permite variação: 1/16, 1/32, 1/64
        arpeggio_quantization_options = [
            self.ticks_per_beat // 4,  # Semicolcheia (1/16)
            self.ticks_per_beat // 8,  # Fusa (1/32)
            self.ticks_per_beat // 16  # Semifusa (1/64)
        ]
        arpeggio_note_duration = random.choice(arpeggio_quantization_options)
        
        progression_length = len(chord_progression_roman)
        
        # Tipos de padrão de arpejo para mais variedade
        arpeggio_styles = ['up', 'down', 'up_down', 'random_order', 'broken_chord']

        for beat_num in range(num_beats): # Loop para cada batida
            current_beat_start_tick = beat_num * self.ticks_per_beat
            
            # Obtém o nome do acorde para o compasso atual
            measure_idx = beat_num // 4
            chord_name = chord_progression_roman[measure_idx % progression_length]
            current_chord_intervals = self.scales[scale_type]['chords'][chord_name]
            
            base_note_for_arpeggio = self._get_note_from_root_and_interval(root_key, scale_type, 0, 72) # Oitava mais alta
            arpeggio_notes_base = sorted([base_note_for_arpeggio + interval for interval in current_chord_intervals])
            
            # Estende as notas do acorde para incluir mais oitavas para o arpejo
            extended_arpeggio_notes = []
            for note in arpeggio_notes_base:
                if note - 12 >= 36: extended_arpeggio_notes.append(note - 12) # Oitava abaixo
                extended_arpeggio_notes.append(note)
                if note + 12 <= 108: extended_arpeggio_notes.append(note + 12) # Oitava acima
            extended_arpeggio_notes = sorted(list(set(extended_arpeggio_notes))) # Remove duplicatas e ordena

            # Escolhe um estilo de arpejo aleatoriamente para esta batida/bloco
            chosen_style = random.choice(arpeggio_styles)
            
            arpeggio_pattern_notes = []
            if chosen_style == 'up':
                arpeggio_pattern_notes = extended_arpeggio_notes
            elif chosen_style == 'down':
                arpeggio_pattern_notes = list(reversed(extended_arpeggio_notes))
            elif chosen_style == 'up_down':
                arpeggio_pattern_notes = extended_arpeggio_notes + list(reversed(extended_arpeggio_notes[1:-1]))
            elif chosen_style == 'random_order':
                arpeggio_pattern_notes = random.sample(extended_arpeggio_notes, len(extended_arpeggio_notes))
            elif chosen_style == 'broken_chord': # Toca notas do acorde de forma não sequencial
                # Escolhe 2-3 notas aleatórias do acorde base para tocar em sequência
                num_broken_notes = random.randint(2, min(4, len(arpeggio_notes_base)))
                arpeggio_pattern_notes = random.sample(arpeggio_notes_base, num_broken_notes)
                # Adiciona variação de oitava para as notas do broken chord
                arpeggio_pattern_notes = [n + random.choice([-12, 0, 12]) for n in arpeggio_pattern_notes]
                arpeggio_pattern_notes = sorted([n for n in arpeggio_pattern_notes if 36 <= n <= 108]) # Filtra faixa MIDI

            # Garante que o arpejo preenche a batida com a duração escolhida
            notes_per_beat = self.ticks_per_beat // arpeggio_note_duration
            
            for i in range(notes_per_beat):
                if not arpeggio_pattern_notes: break # Evita erro se o padrão estiver vazio
                arpeggio_note = arpeggio_pattern_notes[i % len(arpeggio_pattern_notes)]
                
                velocity = random.randint(65, 85) # Variação de velocity

                tick_position = current_beat_start_tick + (i * arpeggio_note_duration)
                
                events.append(('note_on', arpeggio_note, velocity, tick_position))
                events.append(('note_off', arpeggio_note, 0, tick_position + arpeggio_note_duration - (self.ticks_per_beat // 64))) # Pequeno release
        
        return events

    def generate_drums(self, num_beats, drum_patterns_config):
        events = []
        # Definir notas MIDI para bateria (General MIDI Standard)
        KICK = 36  # C1
        SNARE = 38 # D1
        CLOSED_HIHAT = 42 # F#1
        OPEN_HIHAT = 46 # A#1
        RIDE = 51 # D#2
        CRASH = 49 # C#2

        # Seleciona um padrão aleatório para cada tipo de instrumento de bateria
        chosen_kick_pattern = random.choice(drum_patterns_config.get('kick', [[]]))
        chosen_snare_pattern = random.choice(drum_patterns_config.get('snare', [[]]))
        chosen_hihat_closed_pattern = random.choice(drum_patterns_config.get('hihat_closed', [[]]))
        chosen_hihat_open_pattern = random.choice(drum_patterns_config.get('hihat_open', [[]]))
        chosen_percussion_pattern = random.choice(drum_patterns_config.get('percussion', [[]]))
        
        for measure_idx in range(num_beats // 4):
            measure_start_tick = measure_idx * self.ticks_per_beat * 4

            # Adiciona kick
            for offset_ticks_json, velocity, duration_beats in chosen_kick_pattern:
                duration_ticks = int(duration_beats * self.ticks_per_beat)
                events.append(('note_on', KICK, velocity, measure_start_tick + offset_ticks_json))
                events.append(('note_off', KICK, 0, measure_start_tick + offset_ticks_json + duration_ticks))
            
            # Adiciona snare
            for offset_ticks_json, velocity, duration_beats in chosen_snare_pattern:
                duration_ticks = int(duration_beats * self.ticks_per_beat)
                events.append(('note_on', SNARE, velocity, measure_start_tick + offset_ticks_json))
                events.append(('note_off', SNARE, 0, measure_start_tick + offset_ticks_json + duration_ticks))

            # Adiciona hihat_closed
            for offset_ticks_json, velocity, duration_beats in chosen_hihat_closed_pattern:
                duration_ticks = int(duration_beats * self.ticks_per_beat)
                events.append(('note_on', CLOSED_HIHAT, velocity, measure_start_tick + offset_ticks_json))
                events.append(('note_off', CLOSED_HIHAT, 0, measure_start_tick + offset_ticks_json + duration_ticks))

            # Adiciona hihat_open
            for offset_ticks_json, velocity, duration_beats in chosen_hihat_open_pattern:
                duration_ticks = int(duration_beats * self.ticks_per_beat)
                events.append(('note_on', OPEN_HIHAT, velocity, measure_start_tick + offset_ticks_json))
                events.append(('note_off', OPEN_HIHAT, 0, measure_start_tick + offset_ticks_json + duration_ticks))
            
            # Adiciona percussão genérica
            for offset_ticks_json, velocity, duration_beats in chosen_percussion_pattern:
                duration_ticks = int(duration_beats * self.ticks_per_beat)
                events.append(('note_on', random.choice([RIDE, CRASH]), velocity, measure_start_tick + offset_ticks_json)) # Varia entre Ride e Crash
                events.append(('note_off', random.choice([RIDE, CRASH]), 0, measure_start_tick + offset_ticks_json + duration_ticks))

        return events

    def save_midi_file(self, all_midi_events, filename, bpm, instrument_programs):
        mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        mid.tempo = mido.bpm2tempo(bpm) # Define o tempo principal do arquivo MIDI

        # Mapeamento de canais e nomes de partes
        part_channel_map = {
            'bass': {'channel': 0},
            'chords': {'channel': 1},
            'lead': {'channel': 2},
            'pads': {'channel': 3},
            'arpeggio': {'channel': 4},
            'drums': {'channel': 9}
        }

        # Cria uma trilha para cada parte gerada
        for part_name, part_data in part_channel_map.items():
            if part_name in all_midi_events:
                track = mido.MidiTrack()
                mid.tracks.append(track)
                
                # Define o programa (instrumento) para a trilha
                program = instrument_programs.get(part_name, 0) # Obtém o programa do dicionário passado
                track.append(mido.Message('program_change', program=program, channel=part_data['channel'], time=0))

                events = all_midi_events[part_name]
                events.sort(key=lambda x: x[3]) # Garante que os eventos estejam em ordem cronológica
                
                current_ticks = 0
                for event_type, note, velocity, time in events:
                    delta_time = time - current_ticks # Calcula o tempo delta
                    
                    # Evita delta_time negativo, caso haja algum erro na ordenação ou eventos no mesmo tick
                    if delta_time < 0: delta_time = 0 

                    # Garante que delta_time é um inteiro antes de adicionar à mensagem MIDI
                    track.append(mido.Message(event_type, channel=part_data['channel'], note=note, velocity=velocity, time=int(delta_time)))
                    current_ticks = time # Atualiza o tempo atual para o próximo cálculo de delta

        # Se não houver eventos, criar uma trilha vazia para o arquivo ser válido
        if not mid.tracks:
            mid.tracks.append(mido.MidiTrack())

        mid.save(filename)
        return True # Retorna True em caso de sucesso
